"""Snapshot of how many people are being tracked right now, for the OPC UA server.

track.py feeds this every frame; it writes a small JSON snapshot twice a
second to a tmpfs volume shared with the OPC UA container (opcua/server.py),
which serves it. Written atomically (temp file + rename), so the reader never
sees a partial file.
"""

from __future__ import annotations

import json
import os
import time

WRITE_INTERVAL_S = 0.5


class PeopleState:
    def __init__(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self._count = 0
        self._frame_time = 0.0
        self._camera_connected = False
        self._last_write = 0.0

    def update(self, count: int, frame_time: float) -> None:
        """Record one frame's person count (tracks including held ones, see detectors.TrackHold)."""
        self._camera_connected = True
        self._count = count
        self._frame_time = frame_time
        self._publish()

    def disconnected(self) -> None:
        """The source dropped or the tracker is stopping: nothing is being observed."""
        self._count = 0
        self._camera_connected = False
        self._publish(force=True)

    def _publish(self, force: bool = False) -> None:
        now = time.time()
        if not force and now - self._last_write < WRITE_INTERVAL_S:
            return
        snapshot = {
            "written": now,
            "frame_time": self._frame_time,
            "camera_connected": self._camera_connected,
            "count": self._count,
        }
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(snapshot, f)
        os.replace(tmp, self.path)
        self._last_write = now
