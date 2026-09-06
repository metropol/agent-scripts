#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime, timezone

SESSIONS = Path.home() / ".codex" / "sessions"

def latest_session_files(limit=20):
    files = sorted(
        SESSIONS.glob("**/rollout-*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[:limit]

def extract_latest_rate_limits(path):
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in reversed(lines):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        payload = event.get("payload", {})
        if payload.get("type") != "token_count":
            continue

        rate_limits = payload.get("rate_limits")
        if rate_limits:
            timestamp = event.get("timestamp")
            info = payload.get("info")
            return {
                "timestamp": timestamp,
                "session_file": str(path),
                "rate_limits": rate_limits,
                "token_info": info,
            }

    return None

def unix_to_local(ts):
    if ts is None:
        return None
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")

def main():
    for file in latest_session_files():
        snapshot = extract_latest_rate_limits(file)
        if snapshot:
            rl = snapshot["rate_limits"]

            primary = rl.get("primary", {})
            secondary = rl.get("secondary", {})

            output = {
                "observed_at": snapshot["timestamp"],
                "session_file": snapshot["session_file"],
                "five_hour": {
                    "used_percent": primary.get("used_percent"),
                    "window_minutes": primary.get("window_minutes"),
                    "resets_at_unix": primary.get("resets_at"),
                    "resets_at_local": unix_to_local(primary.get("resets_at")),
                },
                "weekly": {
                    "used_percent": secondary.get("used_percent"),
                    "window_minutes": secondary.get("window_minutes"),
                    "resets_at_unix": secondary.get("resets_at"),
                    "resets_at_local": unix_to_local(secondary.get("resets_at")),
                },
                "token_info": snapshot["token_info"],
            }

            print(json.dumps(output, indent=2))
            return

    raise SystemExit("No recent token_count event with rate_limits found.")

if __name__ == "__main__":
    main()
