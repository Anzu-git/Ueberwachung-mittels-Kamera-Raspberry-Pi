"""OPC UA server exposing how many people the camera tracker currently sees.

Reads the tracker's snapshot (written by app/state.py to a shared tmpfs
volume) once a second and updates these variables under
Objects/PeopleTracking, all with string NodeIds in the namespace
urn:camera-tracker (ns=2 on this server):

  PersonCount      Int32       people currently tracked, including ones
                               missed for up to a second (track.py --hold)
  Timestamp        DateTime    when this snapshot was observed (UTC)
  CameraConnected  Boolean     false when the camera stream is down or the
                               tracker isn't running; the count is then 0
                               and means "not observing", not "nobody there"

Values carry the observation time as their SourceTimestamp. See README.md.
"""

import asyncio
import json
import os
import time
from datetime import datetime, timezone

from asyncua import Server, ua
from asyncua.common.utils import ServiceError
from asyncua.server.address_space import ViewService
from asyncua.server.internal_session import SessionState
from asyncua.server.uaprocessor import UaProcessor

STATE_FILE = os.environ.get("STATE_FILE", "/run/tracker-state/people.json")
ENDPOINT = os.environ.get("OPCUA_ENDPOINT", "opc.tcp://0.0.0.0:4840/camera-tracker/")
NAMESPACE = "urn:camera-tracker"
UPDATE_INTERVAL_S = 1.0
# The tracker writes every 0.5s while it's processing frames; a snapshot
# older than this means it has stopped or is waiting for the camera.
STALE_AFTER_S = 3.0


def utc(t: float) -> datetime:
    return datetime.fromtimestamp(t, timezone.utc)


# asyncua 2.0.1 bug: a TranslateBrowsePathsToNodeIds request containing a
# path with no elements raises IndexError, which fails the whole request
# (every path in the batch) instead of that one path. OPC Router sends such
# paths. OPC UA Part 4 (5.8.4) makes an empty relative path an operation-level
# Bad_NothingToDo, so return exactly that and leave every other path alone.
_translate_one = ViewService._translate_browsepath_to_nodeid


def _translate_one_guarded(self, path: ua.BrowsePath) -> ua.BrowsePathResult:
    if not path.RelativePath.Elements:
        return ua.BrowsePathResult(StatusCode=ua.StatusCode(ua.StatusCodes.BadNothingToDo))
    return _translate_one(self, path)


ViewService._translate_browsepath_to_nodeid = _translate_one_guarded


# asyncua 2.0.1 bug: when a session times out, the connection stays open and
# every further request on it is answered BadSessionNotActivated, which tells
# the client to activate a session that no longer exists. OPC Router kept
# retrying that for minutes and never recovered. The status for a session
# the server has closed is BadSessionIdInvalid (Part 4 7.34), on which
# clients create a new session. Requests that don't need a session, and
# CreateSession/ActivateSession (which report on their own), pass through.
_SESSIONLESS = {
    ua.NodeId(getattr(ua.ObjectIds, f"{name}_Encoding_DefaultBinary"))
    for name in (
        "CreateSessionRequest", "ActivateSessionRequest", "CloseSessionRequest",
        "GetEndpointsRequest", "FindServersRequest", "CloseSecureChannelRequest",
    )
}
_process_message = UaProcessor._process_message


async def _process_message_guarded(self, typeid, requesthdr, seqhdr, body):
    if self.session is not None and self.session.state == SessionState.Closed and typeid not in _SESSIONLESS:
        raise ServiceError(ua.StatusCodes.BadSessionIdInvalid)
    return await _process_message(self, typeid, requesthdr, seqhdr, body)


UaProcessor._process_message = _process_message_guarded

# Clients ask for a session timeout; after that long without a request the
# server closes the session. OPC Router asks for 15s, which a stall on the
# school's relayed Tailscale path can exceed. Revising the timeout upward is
# the server's call (clients must use the revised value), and with one or
# two clients a dead session lingering a couple of minutes costs nothing.
MIN_SESSION_TIMEOUT_MS = 120_000


def read_snapshot() -> dict | None:
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            snapshot = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    if time.time() - snapshot["written"] > STALE_AFTER_S:
        return None
    return snapshot


async def main() -> None:
    server = Server()
    await server.init()
    server.iserver.min_session_timeout_ms = MIN_SESSION_TIMEOUT_MS
    server.set_endpoint(ENDPOINT)
    server.set_server_name("Camera Tracker")
    server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
    idx = await server.register_namespace(NAMESPACE)

    # Browse names must be in our namespace too. Given an explicit NodeId and
    # a plain-string name, asyncua puts the name in namespace 0 (reserved for
    # the OPC Foundation's standard nodes), and clients that resolve
    # "2:PeopleTracking/2:PersonCount" then get BadNoMatch.
    def names(name: str, parent: str = "PeopleTracking.") -> tuple[ua.NodeId, ua.QualifiedName]:
        return ua.NodeId(f"{parent}{name}", idx), ua.QualifiedName(name, idx)

    tracking = await server.nodes.objects.add_object(*names("PeopleTracking", parent=""))
    count = await tracking.add_variable(*names("PersonCount"), 0, ua.VariantType.Int32)
    timestamp = await tracking.add_variable(*names("Timestamp"), utc(time.time()), ua.VariantType.DateTime)
    connected = await tracking.add_variable(*names("CameraConnected"), False, ua.VariantType.Boolean)

    async with server:
        print(f"serving {ENDPOINT} (namespace {NAMESPACE} = ns={idx})", flush=True)
        while True:
            snapshot = read_snapshot()
            if snapshot and snapshot["camera_connected"]:
                observed = utc(snapshot["frame_time"])
                people, is_connected = snapshot["count"], True
            else:
                observed = utc(time.time())
                people, is_connected = 0, False
            values = [
                (count, people, ua.VariantType.Int32),
                (connected, is_connected, ua.VariantType.Boolean),
                (timestamp, observed, ua.VariantType.DateTime),
            ]
            for node, value, vtype in values:
                await node.write_value(ua.DataValue(ua.Variant(value, vtype), SourceTimestamp=observed))
            await asyncio.sleep(UPDATE_INTERVAL_S)


if __name__ == "__main__":
    asyncio.run(main())
