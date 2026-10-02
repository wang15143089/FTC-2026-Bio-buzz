#!/usr/bin/env python3
"""Watch a long-running CAD inspection and say whether it is still progressing.

This is the operator side of ``AI_Long_Running_Process_No_Output_Guide.md`` for
runs of ``tools/inspect_geometry.py``.  It is deliberately read-only: it never
terminates, signals or restarts the process it watches.  It reports, and the
operator decides.

Evidence it reads

* the JSON state published by ``--progress-file`` (stage, elapsed time, CPU time,
  heartbeat and stage counters, ``active``);
* the run log written by ``--log-file``, whose size and modification time give
  the last moment the process actually produced output;
* the watched process itself, for existence and total CPU time.

The guide's two timeouts stay separate.  An output timeout only triggers an
inspection; only a progress timeout - elapsed time with no verifiable advance at
all - is reported as stalled.

Typical use, while the run is going::

    .venv-cad\\Scripts\\python.exe tools\\watch_long_run.py ^
        --progress-file tmp\\inspect_progress.json --log-file tmp\\inspect.log

    .venv-cad\\Scripts\\python.exe tools\\watch_long_run.py --once

The reported state is one of RUNNING, SILENT_ACTIVE, BLOCKED, SUSPECTED_STALL,
FINISHED, GONE or UNKNOWN.  The exit status is 1 only for SUSPECTED_STALL, so a
wrapper can notice it without treating a slow but healthy run as a failure.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import sys
import time
from ctypes import wintypes
from pathlib import Path

POLL_SECONDS = 20.0
OUTPUT_TIMEOUT_S = 60.0
PROGRESS_TIMEOUT_S = 600.0

RUNNING = "RUNNING"
SILENT_ACTIVE = "SILENT_ACTIVE"
BLOCKED = "BLOCKED"
SUSPECTED_STALL = "SUSPECTED_STALL"
FINISHED = "FINISHED"
GONE = "GONE"
UNKNOWN = "UNKNOWN"

ACTIONS = {
    RUNNING: "continue: output and progress are both current",
    SILENT_ACTIVE: "continue: output is quiet but CPU time is still climbing",
    BLOCKED: "inspect the blocking resource (disk, lock, stdin, subprocess) before stopping anything",
    SUSPECTED_STALL: "collect diagnostics, locate the last checkpoint, prefer a graceful stop",
    FINISHED: "read the report; the run reached its own end",
    GONE: "the process left while its state still said active; read the run log before restarting",
    UNKNOWN: "no state file yet; check the paths, or wait for the run to publish its first stage",
}

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]


def process_cpu_seconds(pid: int) -> float | None:
    """Total CPU time of *pid*, or None when it is gone or cannot be sampled.

    This reads the process handle directly, so it keeps working while the watched
    process holds the interpreter lock and cannot refresh its own state file.
    """
    if sys.platform != "win32" or not pid:
        return None
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return None
    try:
        created, exited = FILETIME(), FILETIME()
        kernel, user = FILETIME(), FILETIME()
        ok = kernel32.GetProcessTimes(
            handle,
            ctypes.byref(created),
            ctypes.byref(exited),
            ctypes.byref(kernel),
            ctypes.byref(user),
        )
        if not ok:
            return None
        ticks = ((kernel.dwHighDateTime << 32) | kernel.dwLowDateTime) + (
            (user.dwHighDateTime << 32) | user.dwLowDateTime
        )
        return round(ticks / 1e7, 2)
    finally:
        kernel32.CloseHandle(handle)


def read_state(path: Path) -> dict:
    # the writer swaps the file in, so a reader can momentarily be refused on
    # Windows; retry briefly rather than report a false UNKNOWN
    for attempt in range(5):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return {}
        except OSError:
            if attempt == 4:
                return {}
            time.sleep(0.05)
    return {}


def stat_or_none(path: Path | None):
    if path is None:
        return None
    try:
        return path.stat()
    except OSError:
        return None


def probe(progress_file: Path, log_file: Path | None) -> dict:
    """One observation of everything the guide says to look at."""
    state = read_state(progress_file)
    pid = int(state.get("pid") or 0)
    progress_stat = stat_or_none(progress_file)
    log_stat = stat_or_none(log_file)
    return {
        "observed_at": time.time(),
        "clock": dt.datetime.now().strftime("%H:%M:%S"),
        "state": state,
        "pid": pid,
        "active": state.get("active"),
        "stage": state.get("stage", "?"),
        "elapsed_s": state.get("elapsed_s"),
        "state_cpu_s": state.get("cpu_time_s"),
        "heartbeats": state.get("heartbeats"),
        "stages_done": state.get("stages_done"),
        "check": (state.get("check_index"), state.get("check_total")),
        "process_cpu_s": process_cpu_seconds(pid),
        "state_mtime": progress_stat.st_mtime if progress_stat else None,
        "log_size": log_stat.st_size if log_stat else None,
        "log_mtime": log_stat.st_mtime if log_stat else None,
    }


def fingerprint(sample: dict) -> tuple:
    """Everything that counts as a verifiable advance, per the guide section 5.2."""
    return (
        sample["process_cpu_s"],
        sample["state_cpu_s"],
        sample["heartbeats"],
        sample["stages_done"],
        sample["check"],
        sample["state_mtime"],
        sample["log_size"],
    )


def classify(sample: dict, previous: dict | None, last_advance: float,
             output_timeout: float, progress_timeout: float) -> tuple[str, list[str]]:
    now = sample["observed_at"]
    evidence: list[str] = []

    if not sample["state"]:
        return UNKNOWN, ["no state file was readable"]

    if sample["active"] is False:
        evidence.append("the state file reports active=false")
        return FINISHED, evidence

    if sample["pid"] and sample["process_cpu_s"] is None:
        evidence.append(f"pid {sample['pid']} no longer exists")
        return GONE, evidence

    last_output = max(
        value for value in (sample["state_mtime"], sample["log_mtime"], 0.0) if value is not None
    )
    output_age = now - last_output
    progress_age = now - last_advance
    evidence.append(f"stage: {sample['stage']}")
    evidence.append(f"no new output for {output_age:.0f}s (output timeout {output_timeout:.0f}s)")
    evidence.append(f"no verifiable advance for {progress_age:.0f}s (progress timeout {progress_timeout:.0f}s)")

    if sample["process_cpu_s"] is not None:
        evidence.append(f"process CPU time {sample['process_cpu_s']:.1f}s")
    if previous is not None:
        grew = (sample["process_cpu_s"] or 0) - (previous["process_cpu_s"] or 0)
        evidence.append(f"CPU time change since the last sample: {grew:+.1f}s")

    if progress_age > progress_timeout:
        return SUSPECTED_STALL, evidence
    if output_age > output_timeout:
        if previous is not None and (sample["process_cpu_s"] or 0) > (previous["process_cpu_s"] or 0):
            return SILENT_ACTIVE, evidence
        return BLOCKED, evidence
    return RUNNING, evidence


def report(state: str, evidence: list[str], sample: dict) -> None:
    print(f"STATE: {state}")
    print("EVIDENCE:")
    for line in evidence:
        print(f"  - {line}")
    check = sample.get("check") or (None, None)
    if check[0] is not None:
        print(f"  - check {check[0]}/{check[1]}")
    print(f"ACTION: {ACTIONS[state]}")
    sys.stdout.flush()


def _advance_reference(sample: dict) -> float:
    """Best available timestamp of the last verifiable advance, for a first sample."""
    moments = [value for value in (sample["state_mtime"], sample["log_mtime"]) if value]
    return max(moments) if moments else sample["observed_at"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--progress-file", default="tmp/inspect_progress.json",
                        help="state file published by inspect_geometry.py --progress-file")
    parser.add_argument("--log-file", default=None,
                        help="run log written by inspect_geometry.py --log-file")
    parser.add_argument("--interval", type=float, default=POLL_SECONDS,
                        help=f"seconds between samples (default {POLL_SECONDS:.0f})")
    parser.add_argument("--output-timeout", type=float, default=OUTPUT_TIMEOUT_S,
                        help="silence that only triggers an inspection, never a stop")
    parser.add_argument("--progress-timeout", type=float, default=PROGRESS_TIMEOUT_S,
                        help="time without any verifiable advance that counts as stalled")
    parser.add_argument("--once", action="store_true", help="take one sample, report and exit")
    args = parser.parse_args(argv)

    progress_file = Path(args.progress_file)
    log_file = Path(args.log_file) if args.log_file else None

    if args.once:
        # two samples, so the CPU comparison is a real measurement rather than a
        # guess about a process we only looked at once
        first = probe(progress_file, log_file)
        time.sleep(min(2.0, args.interval))
        sample = probe(progress_file, log_file)
        last_advance = _advance_reference(first)
        if fingerprint(sample) != fingerprint(first):
            last_advance = sample["observed_at"]
        state, evidence = classify(sample, first, last_advance,
                                   args.output_timeout, args.progress_timeout)
        report(state, evidence, sample)
        return 1 if state == SUSPECTED_STALL else 0

    previous: dict | None = None
    last_advance = 0.0
    last_fingerprint: tuple | None = None
    last_state: str | None = None

    while True:
        sample = probe(progress_file, log_file)
        current = fingerprint(sample)
        if last_fingerprint is None:
            last_advance = _advance_reference(sample)
        elif current != last_fingerprint:
            last_advance = sample["observed_at"]
        last_fingerprint = current

        state, evidence = classify(sample, previous, last_advance,
                                   args.output_timeout, args.progress_timeout)
        if state != last_state:
            print(f"[{sample['clock']}]")
            report(state, evidence, sample)
            last_state = state
        else:
            print(f"[{sample['clock']}] {state}  stage={sample['stage']}  "
                  f"elapsed={sample['elapsed_s']}s  cpu={sample['process_cpu_s']}s")
            sys.stdout.flush()

        previous = sample
        if state in (FINISHED, GONE):
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
