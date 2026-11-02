#!/usr/bin/env python3
"""Publish pages from the scheduled/ backlog when their time arrives.

Usage:
  python3 tools/scheduled/publish.py          publish everything that is due
  python3 tools/scheduled/publish.py --check  list problems, change nothing

scheduled/schedule.json is a list of entries like:
  {"at": "2027-01-10T12:00:00+00:00",
   "page": "fellowship.html",
   "source": "scheduled/fellowship-lent-2027-open.html"}

Publishing copies the source over the live page, then removes the source and
its entry. Uses only the Python standard library, so GitHub needs no setup.
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEDULE = ROOT / "scheduled" / "schedule.json"


def load():
    return json.loads(SCHEDULE.read_text())


def save(entries):
    SCHEDULE.write_text(json.dumps(entries, indent=2) + "\n")


def parse_time(value):
    when = datetime.fromisoformat(value)
    if when.tzinfo is None:
        raise ValueError(f"{value} has no timezone offset")
    return when


def last_commit(path):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", path],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    return int(out) if out else None


def problems(entries, now):
    found = []
    for entry in entries:
        label = f"{entry.get('page')} at {entry.get('at')}"
        try:
            when = parse_time(entry["at"])
            page, source = entry["page"], entry["source"]
        except (KeyError, TypeError, ValueError) as err:
            found.append(f"{label}: entry is not valid ({err})")
            continue
        if not (ROOT / source).is_file():
            found.append(f"{label}: {source} does not exist")
            continue
        if when <= now:
            found.append(f"{label}: overdue, has not been published")
        page_time, source_time = last_commit(page), last_commit(source)
        if page_time and source_time and page_time > source_time:
            found.append(f"{label}: the live page changed after {source} was written, so publishing would overwrite those edits")
    return found


def publish(entries, now):
    remaining, published = [], []
    for entry in sorted(entries, key=lambda e: parse_time(e["at"])):
        if parse_time(entry["at"]) > now:
            remaining.append(entry)
            continue
        shutil.copyfile(ROOT / entry["source"], ROOT / entry["page"])
        (ROOT / entry["source"]).unlink()
        published.append(entry)
    if published:
        save(remaining)
    return published


def main():
    now = datetime.now(timezone.utc)
    entries = load()
    if "--check" in sys.argv:
        found = problems(entries, now)
        print("\n".join(found) if found else f"No problems. {len(entries)} scheduled.")
        return 1 if found else 0
    for entry in publish(entries, now):
        print(f"Published {entry['page']} from {entry['source']} (due {entry['at']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
