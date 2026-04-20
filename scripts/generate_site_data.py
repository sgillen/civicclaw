#!/usr/bin/env python3
"""Generate CivicClaw site markdown for public district pages.

Publish pipeline:
  1. sf_weekly_digest.py --district N --json  →  build/bundles/dN.json  (raw data bundle)
  2. Agent reads bundle + STYLE.md + user profile  →  docs/data/dN.md  (styled narrative)

The bundle step is reliable and deterministic (this script handles it).
The narrative synthesis step requires an LLM and is done by the caller/agent.

Canonical output:
- build/bundles/d{district}.json      (intermediate)
- docs/data/d{district}.md            (final — agent-written)
- docs/data/site-refresh-summary.json
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DISTRICT_TIMEOUT = 720

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
DOCS_DATA_DIR = REPO_ROOT / "docs" / "data"
LOGS_DIR = REPO_ROOT / "logs" / "site-build"
BUNDLES_DIR = REPO_ROOT / "build" / "bundles"

DISTRICTS = list(range(1, 12))


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Generate CivicClaw site markdown for district pages")
    parser.add_argument("--district", type=int, action="append", help="Generate only the given district (repeatable)")
    parser.add_argument("--retry-failed", action="store_true", help="Read site-refresh-summary.json and rerun only failed/timeout districts")
    parser.add_argument("--bundle-only", action="store_true", help="Only produce JSON bundles; do not write narrative markdown (for agent-driven synthesis)")
    return parser.parse_args()


def resolve_districts(args):
    if args.district:
        ordered = []
        seen = set()
        for d in args.district:
            if 1 <= d <= 11 and d not in seen:
                ordered.append(d)
                seen.add(d)
        return ordered
    if args.retry_failed:
        summary_path = DOCS_DATA_DIR / "site-refresh-summary.json"
        if summary_path.exists():
            try:
                summary = json.loads(summary_path.read_text())
                districts = []
                for entry in summary.get("districts", []):
                    if entry.get("status") in ("failed", "timeout"):
                        d = entry.get("district")
                        if isinstance(d, int):
                            districts.append(d)
                if districts:
                    return districts
            except Exception:
                pass
    return DISTRICTS


def run_text(script: str, args: list[str], timeout: int = DISTRICT_TIMEOUT) -> str:
    cmd = [sys.executable, str(SCRIPTS_DIR / script), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"{script} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def append_log(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")


def build_last_updated_summary(completed: list[int], failed: list[dict], districts: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "generated_at": now.isoformat(),
        "generated_at_epoch_ms": int(now.timestamp() * 1000),
        "generated_at_display_utc": now.strftime("%Y-%m-%d %H:%M UTC"),
        "completed": completed,
        "failed": failed,
        "districts": districts,
    }


def merge_with_existing_summary(completed: list[int], failed: list[dict], district_status: list[dict]) -> tuple[list[int], list[dict], list[dict]]:
    summary_path = DOCS_DATA_DIR / "site-refresh-summary.json"
    if not summary_path.exists():
        return completed, failed, district_status
    try:
        existing = json.loads(summary_path.read_text())
    except Exception:
        return completed, failed, district_status

    completed_set = list(dict.fromkeys((existing.get("completed", []) or []) + completed))

    failed_map = {entry.get("district"): entry for entry in (existing.get("failed", []) or []) if isinstance(entry, dict)}
    for entry in failed:
        failed_map[entry.get("district")] = entry

    status_map = {entry.get("district"): entry for entry in (existing.get("districts", []) or []) if isinstance(entry, dict)}
    for entry in district_status:
        status_map[entry.get("district")] = entry

    # If a district is now completed/ok, clear old failed entry for it.
    for d in completed:
        failed_map.pop(d, None)

    merged_failed = sorted(failed_map.values(), key=lambda x: x.get("district", 0))
    merged_status = [status_map[d] for d in sorted(status_map) if d is not None]
    return completed_set, merged_failed, merged_status


def main():
    args = parse_args()
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    BUNDLES_DIR.mkdir(parents=True, exist_ok=True)

    bundle_only = args.bundle_only
    districts_to_run = resolve_districts(args)
    completed = []
    failed = []
    district_status = []

    for district in districts_to_run:
        t0 = time.time()
        district_log = LOGS_DIR / f"d{district}.log"
        district_log.write_text("")
        bundle_path = BUNDLES_DIR / f"d{district}.json"
        print(f"[D{district}] Generating bundle...", flush=True)
        append_log(district_log, f"[{datetime.now(timezone.utc).isoformat()}] start district {district}")
        try:
            # Step 1: produce the JSON data bundle
            cmd = [sys.executable, str(SCRIPTS_DIR / "sf_weekly_digest.py"), "--district", str(district), "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=DISTRICT_TIMEOUT)
            if result.stderr:
                append_log(district_log, result.stderr)
            if result.returncode != 0:
                raise RuntimeError(f"sf_weekly_digest.py failed: {(result.stderr or result.stdout).strip()[:300]}")
            bundle_text = result.stdout
            if not bundle_text or not bundle_text.strip():
                raise RuntimeError("weekly digest --json returned empty output")
            try:
                bundle = json.loads(bundle_text)
            except json.JSONDecodeError as je:
                raise RuntimeError(f"weekly digest --json returned invalid JSON: {je}")
            write_json(bundle_path, bundle)
            append_log(district_log, f"bundle ok at {bundle_path}")

            if bundle_only:
                # Caller/agent will synthesize narrative from bundle
                completed.append(district)
                district_status.append({
                    "district": district,
                    "status": "bundle_ok",
                    "seconds": round(time.time() - t0, 2),
                    "bundle_path": str(bundle_path.relative_to(REPO_ROOT)),
                    "log_path": f"logs/site-build/d{district}.log",
                })
            else:
                # Step 2 (legacy text path): use sf_weekly_digest.py text output directly
                # This produces a data dump, not a styled narrative. For styled reports,
                # use --bundle-only and have the agent synthesize from the bundle.
                cmd_text = [sys.executable, str(SCRIPTS_DIR / "sf_weekly_digest.py"), "--district", str(district)]
                result_text = subprocess.run(cmd_text, capture_output=True, text=True, timeout=DISTRICT_TIMEOUT)
                if result_text.returncode != 0 or not result_text.stdout.strip():
                    raise RuntimeError(f"text report failed: {result_text.stderr.strip()[:300]}")
                (DOCS_DATA_DIR / f"d{district}.md").write_text(result_text.stdout)
                completed.append(district)
                district_status.append({
                    "district": district,
                    "status": "ok",
                    "seconds": round(time.time() - t0, 2),
                    "report_path": f"docs/data/d{district}.md",
                    "bundle_path": str(bundle_path.relative_to(REPO_ROOT)),
                    "log_path": f"logs/site-build/d{district}.log",
                })

            append_log(district_log, f"[{datetime.now(timezone.utc).isoformat()}] ok in {time.time() - t0:.2f}s")
            print(f"[D{district}] OK ({time.time() - t0:.0f}s)", flush=True)
        except subprocess.TimeoutExpired:
            elapsed = time.time() - t0
            error = f"timeout after {elapsed:.0f}s"
            append_log(district_log, f"[{datetime.now(timezone.utc).isoformat()}] timeout: {error}")
            failed.append({"district": district, "error": error})
            district_status.append({
                "district": district,
                "status": "timeout",
                "seconds": round(elapsed, 2),
                "error": error,
                "log_path": f"logs/site-build/d{district}.log",
            })
            print(f"[D{district}] TIMEOUT after {elapsed:.0f}s", file=sys.stderr, flush=True)
        except Exception as e:
            elapsed = time.time() - t0
            error = str(e)
            append_log(district_log, f"[{datetime.now(timezone.utc).isoformat()}] failed: {error}")
            failed.append({"district": district, "error": error})
            district_status.append({
                "district": district,
                "status": "failed",
                "seconds": round(elapsed, 2),
                "error": error,
                "log_path": f"logs/site-build/d{district}.log",
            })
            print(f"[D{district}] FAIL after {elapsed:.0f}s: {e}", file=sys.stderr, flush=True)

        # Refresh the summary after every district.
        write_json(
            DOCS_DATA_DIR / "site-refresh-summary.json",
            build_last_updated_summary(completed, failed, district_status),
        )

    if districts_to_run != DISTRICTS:
        completed, failed, district_status = merge_with_existing_summary(completed, failed, district_status)

    write_json(DOCS_DATA_DIR / "site-refresh-summary.json", build_last_updated_summary(completed, failed, district_status))
    print(f"Done. Completed: {completed}. Failed: {[f['district'] for f in failed]}", flush=True)
    if districts_to_run != DISTRICTS:
        print(f"Run scope: {districts_to_run}", flush=True)


if __name__ == "__main__":
    main()
