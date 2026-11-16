"""Person detection and tracking for the camera relay pipeline.

Runs in one of two modes, chosen automatically from the `src` argument:

  live (src is an rtsp:// URL)
      Continuously reads the newest frame from an RTSP source, annotates it
      with person boxes + track IDs, and republishes it to an RTSP sink.
      Never exits on its own; designed to run as a long-lived container.

  file (src is a path)
      Processes a clip end-to-end, writes an annotated .mp4, prints timing
      stats, and exits. Used for offline benchmarking and model experiments.

Detection runs on the Hailo-8L AI HAT+ (see detectors.py and README.md).
The two modes differ in how they handle being slower than their input: file
mode subsamples deterministically; live mode always jumps to the newest frame
and drops whatever it missed.
"""

import argparse
import os
import signal
import subprocess
import sys
import threading
import time

# Silence libav's own logging inside OpenCV (fatal only). While the camera is
# offline every reconnect attempt logged "method DESCRIBE failed: 404", ~7,500
# lines a day. This script logs disconnects and reconnects itself; to see
# libav's detail when debugging, set OPENCV_FFMPEG_LOGLEVEL=16 (error). Must
# be set before OpenCV initializes its FFmpeg backend.
os.environ.setdefault("OPENCV_FFMPEG_LOGLEVEL", "8")
# Single-threaded H.264 decode. OpenCV's default (one thread per core) makes
# FFmpeg decode frames in parallel, which holds back ~3 frames: ~100ms of
# latency at 30fps, measured with a flip test (tracker-added latency 210ms ->
# 87ms). One thread decodes 720p at ~280fps on this Pi, 9x what the camera
# sends. (OPENCV_FFMPEG_CAPTURE_OPTIONS "threads;1" does NOT work: OpenCV
# sets the thread count itself.)
os.environ.setdefault("OPENCV_FFMPEG_THREADS", "1")
# HailoRT otherwise writes hailort.log into the working directory, which is
# the bind-mounted app/ folder. Errors still raise exceptions in Python.
os.environ.setdefault("HAILORT_LOGGER_PATH", "NONE")

import cv2  # noqa: E402

import detectors
from state import PeopleState

# COCO class 0 is "person". Restricting detection to this one class both
# matches the project's goal and keeps non-person false positives (the model
# liked to label dogs as "cow") out of the tracker entirely. Shared with
# detectors.py rather than redefined, since both need the same value.
PERSON_CLASS_ID = detectors.PERSON_CLASS_ID

# Resolved relative to the working directory, which the Dockerfile sets to
# /app — the same directory this script and the tracker config are mounted in.
TRACKER_CONFIG = "bytetrack_custom.yaml"

BOX_COLOR = (255, 64, 0)  # BGR
TEXT_COLOR = (255, 255, 255)

RECONNECT_DELAY_SECONDS = 3
STATS_INTERVAL_SECONDS = 30
# Live mode exits after the source has been gone this long, releasing the
# Hailo, the encoder and ~450 MiB (PyTorch, loaded by ultralytics' tracker,
# can't be unloaded in-process). Docker's restart policy starts a fresh
# process, which waits for the source at ~50 MiB before loading anything
# heavy. Long enough to ride out relay hiccups and publisher reconnects.
IDLE_EXIT_SECONDS = 120

_ROTATE_CODES = {
    "cw": cv2.ROTATE_90_CLOCKWISE,
    "ccw": cv2.ROTATE_90_COUNTERCLOCKWISE,
    "180": cv2.ROTATE_180,
}

# Set by the SIGTERM/SIGINT handler so the live loop can exit its infinite
# loop and release the capture and the ffmpeg subprocess. Without this,
# `docker stop` would SIGKILL us and orphan the encoder mid-frame.
_shutdown = threading.Event()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("src", help="video file path, or rtsp:// URL for live mode")
    parser.add_argument("dst", help="output file path, or rtsp:// URL to republish to")
    parser.add_argument(
        "--height",
        type=int,
        default=420,
        help="scale frames to this height (aspect preserved) before inference and encoding",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=12.0,
        help="file mode: subsample the source to approximately this rate. "
        "live mode: the nominal rate declared to the encoder (actual rate is "
        "whatever the hardware manages; real timestamps come from the wall clock)",
    )
    parser.add_argument(
        "--rotate",
        choices=["none", "cw", "ccw", "180"],
        default="none",
        help="rotate frames before processing, for sources whose pixels are stored "
        "rotated with no rotation metadata (both OpenCV and ffmpeg decode those sideways)",
    )
    parser.add_argument(
        "--hef",
        default="model.hef",
        help="path to the compiled Hailo .hef model (default: model.hef in the working directory)",
    )
    parser.add_argument(
        "--tiles",
        type=int,
        default=1,
        help="run detection on this many overlapping vertical strips of the full-resolution "
        "frame (one batched inference), so small or distant people are seen in more detail",
    )
    parser.add_argument(
        "--nms-iou",
        type=float,
        default=None,
        help="override the model's NMS overlap threshold; higher keeps more people who "
        "stand partly behind each other (default: the HEF's own)",
    )
    parser.add_argument(
        "--hold",
        type=float,
        default=1.0,
        help="keep showing and counting a person for this many seconds after the "
        "tracker loses them, so brief misses (partial occlusion) don't flicker",
    )
    parser.add_argument(
        "--state-file",
        default=None,
        help="live mode: keep a JSON snapshot of the current person count here, "
        "for the OPC UA server",
    )
    return parser.parse_args()


def scaled_size(width: int, height: int, target_height: int) -> tuple[int, int]:
    """Scale to target_height, preserving aspect ratio.

    Width is rounded to an even number because H.264 chroma subsampling
    requires even dimensions; an odd width makes libx264 fail or pad.
    """
    target_height = min(target_height, height)
    target_width = int(round(width * target_height / height / 2)) * 2
    return max(2, target_width), target_height


def open_capture(src: str, retry_forever: bool) -> cv2.VideoCapture:
    """Open a video source, optionally waiting for it to appear.

    A live publisher (the remote camera) is frequently not connected when
    this process starts, so live mode waits rather than failing. Logging is
    throttled: the retry runs every few seconds and would otherwise fill the
    container log with megabytes of identical lines while idle.
    """
    attempt = 0
    while not _shutdown.is_set():
        cap = cv2.VideoCapture(src)
        if cap.isOpened():
            if attempt:
                print(f"connected to {src.split('@')[-1]}", flush=True)
            return cap
        cap.release()
        if not retry_forever:
            raise SystemExit(f"could not open {src}")
        # Log the first failure, then back off to roughly once a minute.
        if attempt == 0 or attempt % 20 == 0:
            print(f"waiting for {src.split('@')[-1]} ...", flush=True)  # without credentials
        attempt += 1
        _shutdown.wait(RECONNECT_DELAY_SECONDS)
    raise SystemExit("shutting down")


class LatestFrameReader:
    """Reads an RTSP source in a background thread, keeping only the newest frame.

    This exists because inference here is slower than the incoming frame rate.
    Reading strictly in sequence meant the consumer fell further behind with
    every frame, so the server-side backlog grew until MediaMTX dropped the
    session entirely ("reader is too slow, discarding N frames", then an i/o
    timeout). Draining the socket continuously and letting the consumer skip
    to whatever is current keeps latency bounded no matter how slow inference is.
    """

    def __init__(self, src: str) -> None:
        self.src = src
        self.cap = open_capture(src, retry_forever=True)
        self._lock = threading.Lock()
        self._frame = None
        self._frame_id = 0
        self._frame_time = 0.0
        self._new_frame = threading.Condition(self._lock)
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _loop(self) -> None:
        while not _shutdown.is_set():
            ok, frame = self.cap.read()
            if not ok:
                # A dropped source is routine here (remote camera over a
                # relayed VPN link), so reconnect rather than exit.
                print("source read failed, reconnecting...", file=sys.stderr, flush=True)
                self.cap.release()
                self.cap = open_capture(self.src, retry_forever=True)
                continue
            with self._new_frame:
                # No copy needed: cv2 allocates a fresh array per read(), and
                # consumers only ever build new arrays from this one (rotate,
                # resize), so the handed-out reference is never mutated.
                self._frame = frame
                self._frame_id += 1
                # Wall clock, not monotonic: this becomes the timestamps
                # served over OPC UA. It's when the frame reached this Pi, so
                # it trails real-world capture by the source's encode plus
                # network time (a few hundred ms over the relay).
                self._frame_time = time.time()
                self._new_frame.notify_all()

    def get_latest(self, last_seen_id: int, timeout: float | None = 5.0):
        """Wait for a frame newer than last_seen_id.

        Returns (frame, frame_id, arrival_time), or (None, last_seen_id, 0.0)
        if the timeout elapsed without a new frame — which happens while the
        reader thread is reconnecting. Pass timeout=None to wait indefinitely.
        """
        with self._new_frame:
            got = self._new_frame.wait_for(
                lambda: (self._frame is not None and self._frame_id != last_seen_id)
                or _shutdown.is_set(),
                timeout=timeout,
            )
            if not got or self._frame is None or self._frame_id == last_seen_id:
                return None, last_seen_id, 0.0
            return self._frame, self._frame_id, self._frame_time

    def release(self) -> None:
        self.thread.join(timeout=2)
        self.cap.release()


class RtspWriter:
    """Publishes annotated frames to an RTSP path via an ffmpeg subprocess.

    cv2.VideoWriter cannot push to a network sink, so raw BGR frames are piped
    to ffmpeg's stdin and it handles encoding and RTSP publishing.
    """

    # Wait between failed publisher restarts, so a sustained outage (MediaMTX
    # down) doesn't spawn a new process for every frame.
    RESTART_BACKOFF_SECONDS = 2

    def __init__(self, url: str, width: int, height: int, fps: float, live: bool) -> None:
        # A keyframe every ~2s. libx264 defaults to one every 250 frames,
        # which at this pipeline's low frame rate is tens of seconds — long
        # enough that a viewer connecting mid-GOP sees a blank or garbled
        # picture until the next keyframe arrives.
        gop = max(1, round(fps * 2))
        self.cmd = [
            "ffmpeg", "-y", "-loglevel", "warning",
            "-f", "rawvideo", "-pix_fmt", "bgr24",
            "-s", f"{width}x{height}",
        ]
        if live:
            # Frames are produced slower than `fps` (inference is the
            # bottleneck), so timestamping them by frame index would make the
            # stream's timeline advance slower than real time — a viewer
            # drifts further behind live the longer they watch. Wall-clock
            # timestamps pin the timeline to reality instead.
            #
            # Note the deliberate absence of `-r` here: an input frame rate
            # overrides wall-clock timestamps entirely. Measured, feeding
            # 12s of frames at half the nominal rate: with `-r` the output
            # was 6s of media, without it 11.56s. Do not add `-r` back for
            # live mode.
            self.cmd += ["-use_wallclock_as_timestamps", "1"]
        else:
            # File mode genuinely has a fixed, known output rate.
            self.cmd += ["-r", str(fps)]
        self.cmd += [
            "-i", "-",
            "-an", "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
            "-g", str(gop), "-keyint_min", str(gop), "-sc_threshold", "0",
        ]
        if live:
            self.cmd += ["-fps_mode", "passthrough"]
        self.cmd += ["-f", "rtsp", "-rtsp_transport", "tcp", url]

        self.live = live
        self.proc = self._spawn()

    def _spawn(self) -> subprocess.Popen:
        # Unbuffered: with Python's default buffer, the last few KB of each
        # frame waited in it until the next frame was written.
        return subprocess.Popen(self.cmd, stdin=subprocess.PIPE, bufsize=0)

    def write(self, frame) -> None:
        """Write one frame, restarting the encoder if the pipe has broken.

        In live mode a broken pipe means the publish connection dropped; the
        process restarts and carries on, because taking the whole container
        down for a transient network fault would lose the stream entirely.
        In file mode a broken pipe is a genuine error and propagates.
        """
        try:
            self.proc.stdin.write(frame.tobytes())
            return
        except (BrokenPipeError, ValueError):
            if not self.live:
                raise

        print("output pipe broke, restarting ffmpeg publisher...", file=sys.stderr, flush=True)
        self._close_proc()
        _shutdown.wait(self.RESTART_BACKOFF_SECONDS)
        self.proc = self._spawn()
        try:
            self.proc.stdin.write(frame.tobytes())
        except (BrokenPipeError, ValueError):
            # Still failing (sink likely down). Drop this frame rather than
            # crash; the next frame retries, paced by the backoff above.
            print("publisher restart failed, dropping frame", file=sys.stderr, flush=True)

    def _close_proc(self) -> None:
        try:
            if self.proc.stdin and not self.proc.stdin.closed:
                self.proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)

    def release(self) -> None:
        self._close_proc()


def make_writer(dst: str, width: int, height: int, fps: float, live: bool):
    if dst.startswith("rtsp://"):
        return RtspWriter(dst, width, height, fps, live)
    return cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))


def prepare_frame(frame, rotate_code, size: tuple[int, int]):
    """Rotate (if needed); return (full-resolution frame, downscaled frame).

    Detection runs on the full-resolution frame, so --tiles gets real detail;
    everything after it (tracking, drawing, encoding) uses the downscaled
    one, which cuts the encode cost, and encoding competes with inference
    for the same CPUs.
    """
    if rotate_code is not None:
        frame = cv2.rotate(frame, rotate_code)
    return frame, cv2.resize(frame, size, interpolation=cv2.INTER_AREA)


def draw_tracks(frame, tracks):
    """Draw boxes + track IDs from a detectors.track() result onto frame in place.

    Replaces ultralytics' own Results.plot(), which only works on an
    ultralytics Results object — not available here since detection runs on
    the Hailo, outside ultralytics (see detectors.py). tracks is an
    (N, 8) array: x1, y1, x2, y2, track_id, score, cls, det_idx.
    """
    for x1, y1, x2, y2, track_id, score, _cls, _idx in tracks:
        p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.rectangle(frame, p1, p2, BOX_COLOR, 2)
        label = f"id:{int(track_id)} person {score:.2f}"
        label_y = max(p1[1] - 6, 12)
        cv2.putText(frame, label, (p1[0], label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 1, cv2.LINE_AA)
    return frame


def detect_and_track(detector: detectors.HailoDetector, tracker, hold: detectors.TrackHold, full, frame, now: float):
    """Detect on full, track on its downscaled copy frame; return the tracks to show and count.

    Tracker state (which the tracker object carries internally, keyed by its
    own frame_id counter) is what keeps a given person on the same ID from
    frame to frame; hold adds the ones it lost within the last --hold seconds.
    """
    xywh, conf, cls = detector.detect(full)
    xywh *= [frame.shape[1] / full.shape[1], frame.shape[0] / full.shape[0]] * 2
    return hold.update(detectors.track(tracker, xywh, conf, cls, frame), now)


def build_pipeline(args):
    """Load the tracker and the model onto the Hailo; returns (detector, tracker, hold)."""
    tracker = detectors.build_tracker(TRACKER_CONFIG)
    # Pass the tracker everything it can use: its second matching pass keeps
    # existing tracks alive on weak detections (see bytetrack_custom.yaml).
    detector = detectors.HailoDetector(
        args.hef, conf_threshold=tracker.args.track_low_thresh, nms_iou=args.nms_iou, tiles=args.tiles
    )
    return detector, tracker, detectors.TrackHold(args.hold)


def run_live(args, rotate_code) -> None:
    state = PeopleState(args.state_file) if args.state_file else None
    reader = None
    writer = None
    detector = None
    source_dims = None
    size = None
    source_up = False
    try:
        # Blocks until the source is publishing; inside the try so a
        # shutdown while waiting still runs the cleanup below. Nothing heavy
        # is loaded until then (see IDLE_EXIT_SECONDS).
        reader = LatestFrameReader(args.src)
        detector, tracker, hold = build_pipeline(args)
        processed = 0
        latency_sum = latency_max = 0.0
        last_report = last_frame_at = time.monotonic()
        last_id = 0
        while not _shutdown.is_set():
            # None means no frame for 5s: the source dropped and the reader
            # is reconnecting. Loop again and wait.
            frame, last_id, arrived = reader.get_latest(last_id)
            if frame is None and source_up:
                source_up = False
                if state:
                    state.disconnected()
            if frame is None and time.monotonic() - last_frame_at > IDLE_EXIT_SECONDS:
                print(
                    f"no source for {IDLE_EXIT_SECONDS}s, exiting to free the Hailo and memory; "
                    "the restart policy brings this back to wait for it",
                    flush=True,
                )
                _shutdown.set()  # also stops the reader thread's reconnect loop
                break
            if frame is not None:
                last_frame_at = time.monotonic()
                # Dimensions come from each real frame rather than the
                # capture's reported properties (over RTSP those can be zero
                # or stale), and are re-checked every frame because the
                # publisher can reconnect at a different resolution. Keeping
                # the old output size after such a change squashed 16:9 input
                # into the previous 4:3 box.
                height, width = frame.shape[:2]
                if (width, height) != source_dims:
                    source_dims = (width, height)
                    if args.rotate in ("cw", "ccw"):
                        width, height = height, width
                    size = scaled_size(width, height, args.height)
                    if writer is not None:
                        writer.release()
                    writer = make_writer(args.dst, size[0], size[1], args.fps, live=True)
                    # Old track coordinates belong to the previous frame
                    # geometry, and reset() restarts track IDs.
                    hold.reset()
                    tracker.reset()
                    print(
                        f"live: source {width}x{height}, publishing {size[0]}x{size[1]} "
                        f"to {args.dst.split('@')[-1]}",
                        flush=True,
                    )
                source_up = True

                full, prepared = prepare_frame(frame, rotate_code, size)
                tracks = detect_and_track(detector, tracker, hold, full, prepared, arrived)
                if state:
                    state.update(len(tracks), arrived)
                writer.write(draw_tracks(prepared, tracks))
                latency = time.time() - arrived
                latency_sum += latency
                latency_max = max(latency_max, latency)
                processed += 1

            now = time.monotonic()
            if now - last_report > STATS_INTERVAL_SECONDS:
                interval = now - last_report
                if processed:
                    # Latency here is decode-complete to handed-to-encoder, i.e.
                    # what this process adds; it excludes the source's own
                    # capture/encode, the network, and the viewer's buffering.
                    print(
                        f"{processed / interval:.1f} fps over last {interval:.0f}s, "
                        f"pipeline latency avg {latency_sum / processed * 1000:.0f}ms "
                        f"max {latency_max * 1000:.0f}ms",
                        flush=True,
                    )
                processed = 0
                latency_sum = latency_max = 0.0
                last_report = now
    finally:
        if state:
            state.disconnected()
        if reader is not None:
            reader.release()
        if writer is not None:
            writer.release()
        if detector is not None:
            detector.close()


def run_file(args, detector: detectors.HailoDetector, tracker, hold: detectors.TrackHold, rotate_code) -> None:
    cap = open_capture(args.src, retry_forever=False)
    writer = None
    try:
        src_fps = cap.get(cv2.CAP_PROP_FPS) or 24
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if not width or not height:
            raise SystemExit(f"{args.src}: could not determine frame size (corrupt or unsupported file?)")
        if args.rotate in ("cw", "ccw"):
            width, height = height, width
        size = scaled_size(width, height, args.height)

        # Process every Nth frame to approximate the requested rate. The
        # output is written at the rate this stepping actually achieves, so
        # the result plays back at the same speed as the source.
        step = max(1, round(src_fps / args.fps))
        out_fps = src_fps / step
        writer = make_writer(args.dst, size[0], size[1], out_fps, live=False)

        frame_index = 0
        processed = 0
        started = time.time()
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_index % step == 0:
                full, prepared = prepare_frame(frame, rotate_code, size)
                # The hold runs on media time, not wall clock, since a file
                # is processed faster or slower than real time.
                tracks = detect_and_track(detector, tracker, hold, full, prepared, frame_index / src_fps)
                writer.write(draw_tracks(prepared, tracks))
                processed += 1
            frame_index += 1

        elapsed = time.time() - started
        print(f"source: {width}x{height} @ {src_fps:.1f}fps, {frame_index} frames")
        print(f"processed: {size[0]}x{size[1]} @ {out_fps:.1f}fps (step={step}), {processed} frames")
        if elapsed > 0:
            print(f"took {elapsed:.1f}s -> {processed / elapsed:.2f} fps achieved on this hardware")
        print(f"output: {args.dst}")
    finally:
        cap.release()
        if writer is not None:
            writer.release()


def main() -> None:
    args = parse_args()

    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: _shutdown.set())

    rotate_code = _ROTATE_CODES.get(args.rotate)

    # Both modes close the detector in a finally: an activated Hailo device
    # left open at interpreter exit can crash the process with a native bus
    # error instead of exiting cleanly.
    if args.src.startswith("rtsp://"):
        run_live(args, rotate_code)
        return
    detector, tracker, hold = build_pipeline(args)
    try:
        run_file(args, detector, tracker, hold, rotate_code)
    finally:
        detector.close()


if __name__ == "__main__":
    main()
