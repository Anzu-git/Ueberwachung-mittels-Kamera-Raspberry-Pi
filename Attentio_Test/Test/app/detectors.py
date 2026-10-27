"""Person detection on the Hailo-8L, and tracking decoupled from it.

HailoDetector produces person boxes for one frame as (xywh, confidence,
class) arrays; build_tracker()/track() feed those into ultralytics'
BYTETracker directly, since model.track() only works when an ultralytics
model does its own inference.
"""

from __future__ import annotations

import threading

import numpy as np

PERSON_CLASS_ID = 0  # Class 0 is person in both the person/face HEF and COCO.


class HailoDetector:
    """Runs detection on the Hailo-8L via HailoRT's InferVStreams API.

    Verified on real hardware (Hailo-8L, HailoRT 4.23.0) — see `_decode` for
    the output format and README.md's Hailo section for the history.
    `detect()` returns (xywh, conf, cls): an (N, 4) array of box centers and
    sizes in the frame's pixel coordinates, (N,) confidences, and (N,) class
    ids (always PERSON_CLASS_ID, kept as a column because the tracker
    expects one).

    conf_threshold is also applied as the HEF's NMS score threshold, so the
    model doesn't discard candidates the tracker could use. nms_iou, if set,
    overrides the HEF's NMS overlap threshold: two person boxes overlapping
    more than this are treated as duplicates and the weaker one dropped, so
    raising it keeps people standing partly behind each other.

    tiles > 1 splits the frame into that many overlapping vertical strips and
    runs the model on each (one batched inference), so small or distant
    people are seen at close to full resolution; see _tile_rects and
    _merge_tiles.
    """

    def __init__(
        self, hef_path: str, conf_threshold: float, nms_iou: float | None = None, tiles: int = 1
    ) -> None:
        import hailo_platform as hpf  # apt package python3-hailort; see README.md

        self.conf_threshold = conf_threshold
        self.nms_iou = nms_iou
        self.tiles = tiles

        self.hef = hpf.HEF(hef_path)
        self.target = hpf.VDevice()
        configure_params = hpf.ConfigureParams.create_from_hef(
            self.hef, interface=hpf.HailoStreamInterface.PCIe
        )
        self.network_group = self.target.configure(self.hef, configure_params)[0]
        self.network_group_params = self.network_group.create_params()

        self.input_info = self.hef.get_input_vstream_infos()[0]
        self.output_info = self.hef.get_output_vstream_infos()[0]
        self.input_height, self.input_width = self.input_info.shape[:2]  # NHWC

        # UINT8 in: the models' input layers are UINT8, so float input only
        # made HailoRT convert every pixel back.
        self.input_vstreams_params = hpf.InputVStreamParams.make_from_network_group(
            self.network_group, format_type=hpf.FormatType.UINT8
        )
        self.output_vstreams_params = hpf.OutputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type=hpf.FormatType.FLOAT32
        )
        self._activation = self.network_group.activate(self.network_group_params)
        self._activation.__enter__()
        self._infer_pipeline = hpf.InferVStreams(
            self.network_group, self.input_vstreams_params, self.output_vstreams_params
        )
        self._infer_pipeline.__enter__()
        # NMS runs on the host (HailoRT's post-process op), so its thresholds
        # can change at runtime without recompiling the HEF.
        self._infer_pipeline.set_nms_score_threshold(conf_threshold)
        if nms_iou is not None:
            self._infer_pipeline.set_nms_iou_threshold(nms_iou)

    def detect(self, frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        frame_h, frame_w = frame.shape[:2]
        rects = _tile_rects(frame_w, frame_h, self.tiles)
        batch, placements = [], []
        for x0, y0, x1, y1 in rects:
            image, scale, left, top = self._letterbox(frame[y0:y1, x0:x1])
            batch.append(image)
            placements.append((x0, y0, x1, y1, scale, left, top))

        results = self._infer_pipeline.infer({self.input_info.name: np.stack(batch)})
        per_tile = self._decode(results[self.output_info.name])

        boxes, scores, tile_ids = [], [], []
        for tile, ((x0, y0, x1, y1, scale, left, top), dets) in enumerate(zip(placements, per_tile)):
            if not len(dets):
                continue
            ymin, xmin, ymax, xmax, conf = dets.T
            # Normalized model coordinates -> letterboxed input pixels ->
            # tile pixels (undo padding and scaling) -> frame pixels.
            bx1 = (xmin * self.input_width - left) / scale + x0
            bx2 = (xmax * self.input_width - left) / scale + x0
            by1 = (ymin * self.input_height - top) / scale + y0
            by2 = (ymax * self.input_height - top) / scale + y0
            box = np.stack([bx1, by1, bx2, by2], axis=1)
            box[:, 0::2] = box[:, 0::2].clip(x0, x1)
            box[:, 1::2] = box[:, 1::2].clip(y0, y1)
            boxes.append(box)
            scores.append(conf)
            tile_ids.append(np.full(len(conf), tile))

        if not boxes:
            empty = np.zeros((0, 4), dtype=np.float32)
            return empty, np.zeros(0, dtype=np.float32), np.zeros(0, dtype=np.float32)
        boxes, scores, tile_ids = np.concatenate(boxes), np.concatenate(scores), np.concatenate(tile_ids)
        if len(rects) > 1:
            boxes, scores = _merge_tiles(boxes, scores, tile_ids, rects, self.nms_iou or 0.5)

        x1, y1, x2, y2 = boxes.T
        xywh = np.stack([(x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1], axis=1).astype(np.float32)
        cls = np.zeros(len(scores), dtype=np.float32)
        return xywh, scores.astype(np.float32), cls

    def _letterbox(self, image: np.ndarray) -> tuple[np.ndarray, float, int, int]:
        """Scale into the model's square input without distorting it, padding the rest.

        Plain resizing stretched a 16:9 frame into 640x640, making people
        ~1.8x taller and thinner than anything the model was trained on.
        Returns the RGB input plus the scale and padding to undo on boxes.
        """
        import cv2

        h, w = image.shape[:2]
        scale = min(self.input_width / w, self.input_height / h)
        new_w, new_h = round(w * scale), round(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
        # Grey (114) padding, as the YOLO family is trained with.
        canvas = np.full((self.input_height, self.input_width, 3), 114, dtype=np.uint8)
        left, top = (self.input_width - new_w) // 2, (self.input_height - new_h) // 2
        canvas[top:top + new_h, left:left + new_w] = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        return canvas, scale, left, top

    def _decode(self, output) -> list[np.ndarray]:
        """Verified 2026-09-23 against real hardware (Hailo-8L, HailoRT
        4.23.0) with /usr/share/hailo-models/yolov5s_personface_h8l.hef —
        a 2-class (person, face) model with NMS baked into the HEF.

        `pipeline.infer(...)`'s return value for this HEF is, from outside
        in: a dict keyed by output vstream name -> a list with one entry per
        batch item (one per tile, see `detect()`) -> a list with one entry
        per class -> an (N, 5) float32 array, each row
        [ymin, xmin, ymax, xmax, score] in normalized [0, 1] coordinates of
        the model input. yolov8s_h8l.hef (80 COCO classes, person = 0) has
        the same layout. Returns the person rows at or above conf_threshold,
        one (N, 5) array per batch item.
        Confirmed by feeding ultralytics' bus.jpg (4 people, 2 clearly
        visible faces) and getting exactly that back: class 0 (person) had 4
        boxes at conf 0.38-0.92, class 1 (face) had 2 boxes at conf ~0.89-0.91,
        coordinates consistent with the real bounding boxes in the image.

        This was for one specific HEF; a differently-compiled model (e.g. a
        single-class person-only HEF, or one without baked-in NMS) may not
        wrap output the same way. If swapping HEFs, re-run
        scratchpad-style against a known image before trusting this blindly
        — this method still tries to degrade gracefully (unwrap only if
        it looks wrapped) rather than assume the exact shape above.
        """
        per_item = []
        for item in output:
            person_dets = np.asarray(item[PERSON_CLASS_ID], dtype=np.float32).reshape(-1, 5)
            per_item.append(person_dets[person_dets[:, 4] >= self.conf_threshold])
        return per_item

    def close(self) -> None:
        self._infer_pipeline.__exit__(None, None, None)
        self._activation.__exit__(None, None, None)
        self.target.release()


TILE_OVERLAP = 0.15  # each strip is this much wider than width / tiles
SEAM_MARGIN_PX = 4  # a box edge this close to a tile's inner edge was cut by it


def _tile_rects(width: int, height: int, tiles: int) -> list[tuple[int, int, int, int]]:
    """Split the frame into `tiles` overlapping full-height strips, left to right.

    The overlap means a person standing on a seam is usually whole in at
    least one strip. Two strips of a 16:9 frame come out near-square, which
    the square model input fits with little padding.
    """
    if tiles <= 1:
        return [(0, 0, width, height)]
    tile_w = min(width, int(np.ceil(width / tiles * (1 + TILE_OVERLAP))))
    starts = np.linspace(0, width - tile_w, tiles).round().astype(int)
    return [(int(x0), 0, int(x0) + tile_w, height) for x0 in starts]


def _merge_tiles(boxes: np.ndarray, scores: np.ndarray, tile_ids: np.ndarray, rects, iou_threshold: float):
    """Combine per-strip detections (xyxy, frame pixels) into one set.

    The model already removed duplicates within each strip, so only pairs
    from different strips are compared, strongest first:
      - the same person seen whole in both strips' overlap (IoU above
        iou_threshold): keep the stronger box;
      - a person cut by a seam, a partial box in each strip (both touching
        the seam, vertically aligned): join them into one box;
      - a sliver cut off by a seam that lies inside another strip's box:
        drop the sliver.
    Anything else is a different person, including one partly hidden behind
    another, which a plain containment rule would wrongly suppress.
    """
    width = max(r[2] for r in rects)
    cut_left = np.array([rects[t][0] > 0 and b[0] <= rects[t][0] + SEAM_MARGIN_PX for b, t in zip(boxes, tile_ids)])
    cut_right = np.array([rects[t][2] < width and b[2] >= rects[t][2] - SEAM_MARGIN_PX for b, t in zip(boxes, tile_ids)])
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])

    kept: list[int] = []
    out_boxes = boxes.copy()
    out_scores = scores.copy()
    for i in np.argsort(-scores):
        absorbed = False
        for k in kept:
            if tile_ids[i] == tile_ids[k]:
                continue
            a, b = out_boxes[k], boxes[i]
            iw = min(a[2], b[2]) - max(a[0], b[0])
            ih = min(a[3], b[3]) - max(a[1], b[1])
            if iw <= 0 or ih <= 0:
                continue
            inter = iw * ih
            area_k = (a[2] - a[0]) * (a[3] - a[1])
            if inter / (area_k + areas[i] - inter) > iou_threshold:
                absorbed = True
            elif (cut_left[i] or cut_right[i]) and (cut_left[k] or cut_right[k]):
                vertical_iou = ih / (max(a[3], b[3]) - min(a[1], b[1]))
                if vertical_iou > 0.6:
                    out_boxes[k] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    absorbed = True
            elif (cut_left[i] or cut_right[i]) and inter / areas[i] > 0.7:
                absorbed = True
            elif (cut_left[k] or cut_right[k]) and inter / area_k > 0.7:
                # The kept box is the sliver: take this one's box instead.
                out_boxes[k] = b
                cut_left[k], cut_right[k] = cut_left[i], cut_right[i]
                absorbed = True
            if absorbed:
                break
        if not absorbed:
            kept.append(i)
    return out_boxes[kept], out_scores[kept]


class _Detections:
    """Minimal stand-in for an ultralytics Results object.

    ultralytics' standalone BYTETracker (see build_tracker below) expects an
    object with .xywh/.conf/.cls attributes, len(), and boolean-mask
    __getitem__ — reverse-engineered from ultralytics/trackers/byte_tracker.py
    (_split_detections, init_track, parse_bboxes) since there is no public
    "feed it raw detections" API. This is the minimum that satisfies it.
    Internal API; may need adjusting if a future ultralytics version changes
    that protocol.
    """

    def __init__(self, xywh: np.ndarray, conf: np.ndarray, cls: np.ndarray) -> None:
        self.xywh = xywh
        self.conf = conf
        self.cls = cls

    def __len__(self) -> int:
        return len(self.conf)

    def __getitem__(self, mask):
        return _Detections(self.xywh[mask], self.conf[mask], self.cls[mask])


def build_tracker(config_path: str):
    """Construct ultralytics' BYTETracker standalone, outside model.track().

    Needed because model.track() only works with an ultralytics model doing
    its own inference, which HailoDetector isn't. Replicates what
    ultralytics.trackers.track.on_predict_start does when it builds a
    tracker for model.track(), minus the parts specific to a live predictor.
    """
    from ultralytics.trackers import BYTETracker
    from ultralytics.utils import IterableSimpleNamespace, YAML

    cfg = IterableSimpleNamespace(**YAML.load(config_path))
    cfg.device = "cpu"
    return BYTETracker(args=cfg)


# update() is not thread-safe. It's only called from the main loop thread,
# but guard anyway since this is shared state that would fail confusingly
# (not crash) if that ever changed.
_tracker_lock = threading.Lock()


def track(tracker, xywh: np.ndarray, conf: np.ndarray, cls: np.ndarray, frame: np.ndarray) -> np.ndarray:
    """Update the tracker with one frame's detections.

    Returns an (N, 8) array: x1, y1, x2, y2, track_id, score, cls, det_idx —
    ultralytics' STrack.result format, per-row for each currently active track.
    """
    with _tracker_lock:
        return tracker.update(_Detections(xywh, conf, cls), img=frame)


class TrackHold:
    """Keeps reporting a track for hold_s after the tracker last matched it.

    The tracker only returns tracks it matched in the current frame, so a
    person the detector misses for a frame or two (partly occluded, turning,
    at the frame edge) blinks out of the video and the count and back in.
    The tracker itself keeps their ID in its lost pool for track_buffer
    frames, so when it picks them back up they keep it; this only bridges
    the gap in the output, by repeating the last known box.
    """

    def __init__(self, hold_s: float) -> None:
        self.hold_s = hold_s
        self._last: dict[int, tuple[np.ndarray, float]] = {}

    def update(self, tracks: np.ndarray, now: float) -> np.ndarray:
        """Take one frame's track() result; return it plus the held tracks, same format."""
        for row in tracks:
            self._last[int(row[4])] = (row, now)
        self._last = {tid: (row, t) for tid, (row, t) in self._last.items() if now - t <= self.hold_s}
        if not self._last:
            return np.zeros((0, 8), dtype=np.float32)
        return np.stack([row for row, _ in self._last.values()])

    def reset(self) -> None:
        """Forget everything; call alongside tracker.reset(), which reuses IDs."""
        self._last.clear()
