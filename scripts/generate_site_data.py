#!/usr/bin/env python3
"""Generate CivicClaw site markdown + source manifests for all district pages."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

DISTRICT_TIMEOUT = 300   # was 900 — fail fast, don't block the batch
SOURCE_TIMEOUT = 120     # was 180

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
DOCS_DATA_DIR = REPO_ROOT / "docs" / "data"

DISTRICTS = list(range(1, 12))


def run_json(script: str, args: list[str], timeout: int = SOURCE_TIMEOUT):
    cmd = [sys.executable, str(SCRIPTS_DIR / script), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"{script} failed: {result.stderr.strip() or result.stdout.strip()}")
    return json.loads(result.stdout)


def run_text(script: str, args: list[str], timeout: int = DISTRICT_TIMEOUT) -> str:
    cmd = [sys.executable, str(SCRIPTS_DIR / script), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"{script} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def add_source(sources: list[dict], seen: set[tuple[str, str]], label: str, url: str | None, note: str | None = None):
    if not url:
        return
    key = (label, url)
    if key in seen:
        return
    entry = {"label": label, "url": url}
    if note:
        entry["note"] = note
    sources.append(entry)
    seen.add(key)


def maybe_run_json(script: str, args: list[str], timeout: int = SOURCE_TIMEOUT):
    try:
        return run_json(script, args, timeout=timeout)
    except Exception as e:
        print(f"  WARN: {script} failed for {' '.join(args)}: {e}", file=sys.stderr)
        return None


def build_district_sources(district: int) -> dict:
    sources: list[dict] = []
    seen: set[tuple[str, str]] = set()

    add_source(sources, seen, "CivicClaw repo", "https://github.com/sgillen/civicclaw", "project home")

    legistar = maybe_run_json("sf_civic_digest.py", ["--district", str(district), "--days", "7", "--json"], timeout=120) or {}
    for meeting in legistar.get("upcoming", [])[:4]:
        add_source(sources, seen, f"{meeting.get('body', 'Meeting')} agenda", meeting.get("url"), meeting.get("date"))

    journalism = maybe_run_json("sf_journalism.py", ["--district", str(district), "--days", "7", "--json"], timeout=90) or []
    for article in journalism[:5]:
        add_source(sources, seen, article.get("outlet_name", "Article"), article.get("link"), article.get("title"))

    housing = maybe_run_json("sf_housing_pipeline.py", ["--district", str(district), "--days", "90", "--json"], timeout=120) or []
    for project in housing[:4]:
        add_source(sources, seen, f"{project.get('address', 'Project')} PIM", project.get("pim_url"), project.get("status"))

    notices = maybe_run_json("sf_planning_notices.py", ["--district", str(district), "--json"], timeout=60) or []
    for notice in notices[:3]:
        email = notice.get("contact_email")
        if email:
            add_source(sources, seen, f"{notice.get('address', 'Planning notice')} contact", f"mailto:{email}", notice.get("record"))

    sfmta = maybe_run_json("sfmta_hearings.py", ["--district", str(district), "--json"], timeout=60) or []
    for hearing in sfmta[:1]:
        add_source(sources, seen, "SFMTA engineering hearing", "https://www.sfmta.com/public-notices", hearing.get("date"))

    cleanups = maybe_run_json("sf_volunteer_cleanups.py", ["--district", str(district), "--days", "14", "--json"], timeout=60) or []
    if cleanups:
        add_source(sources, seen, "Volunteer cleanups", cleanups[0].get("signup_url") or "https://refuserefusesf.org/cleanups", "signup page")

    return {
        "district": district,
        "sources": sources,
    }


def write_json(path: Path, payload: dict):
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main():
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    completed = []
    failed = []

    for district in DISTRICTS:
        t0 = time.time()
        print(f"[D{district}] Generating markdown...", flush=True)
        try:
            markdown = run_text("sf_weekly_digest.py", ["--district", str(district)], timeout=DISTRICT_TIMEOUT)
            (DOCS_DATA_DIR / f"d{district}.md").write_text(markdown)
            print(f"[D{district}] Generating sources...", flush=True)
            write_json(DOCS_DATA_DIR / f"d{district}-sources.json", build_district_sources(district))
            completed.append(district)
            print(f"[D{district}] OK ({time.time() - t0:.0f}s)", flush=True)
        except subprocess.TimeoutExpired:
            elapsed = time.time() - t0
            failed.append({"district": district, "error": f"timeout after {elapsed:.0f}s"})
            print(f"[D{district}] TIMEOUT after {elapsed:.0f}s", file=sys.stderr, flush=True)
            continue
        except Exception as e:
            elapsed = time.time() - t0
            failed.append({"district": district, "error": str(e)})
            print(f"[D{district}] FAIL after {elapsed:.0f}s: {e}", file=sys.stderr, flush=True)
            continue

    summary = {"completed": completed, "failed": failed}
    write_json(DOCS_DATA_DIR / "site-refresh-summary.json", summary)
    print(f"Done. Completed: {completed}. Failed: {[f['district'] for f in failed]}", flush=True)


if __name__ == "__main__":
    main()
