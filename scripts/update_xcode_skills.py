#!/usr/bin/env python3
"""Generate Xcode AdditionalDocumentation skills.

Usage:
  python3 scripts/update_xcode_skills.py [--clean]

This script reads the local Xcode AdditionalDocumentation directory and
creates/updates skill folders under skills/xcode-additional-docs.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(
    "/Applications/Xcode.app/Contents/PlugIns/IDEIntelligenceChat.framework/"
    "Versions/Current/Resources/AdditionalDocumentation"
)
SKILLS_DIR = Path("skills/xcode-additional-docs")

NAME_RE = re.compile(r"[^a-z0-9]+")


def normalize(name: str) -> str:
    normalized = name.strip().lower()
    normalized = NAME_RE.sub("-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def read_title(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    return path.stem


def xcode_version() -> tuple[str, str]:
    result = subprocess.run(
        ["xcodebuild", "-version"],
        check=True,
        capture_output=True,
        text=True,
    )
    version = "Unknown"
    build = "Unknown"
    for line in result.stdout.splitlines():
        if line.startswith("Xcode "):
            version = line.replace("Xcode ", "", 1).strip()
        elif line.startswith("Build version "):
            build = line.replace("Build version ", "", 1).strip()
    return version, build


def write_skill(skill_dir: Path, title: str, path: Path, version: str, build: str) -> None:
    description = (
        "Guidance for {title} from Xcode AdditionalDocumentation. "
        "Use when implementing, updating, or reviewing related features and "
        "you need to consult the local Xcode doc at {doc_path}. "
        "(Xcode {version} {build})"
    ).format(title=title, doc_path=path, version=version, build=build)

    content = f"""---
name: {skill_dir.name}
description: "{description}"
---

# {title}

## Overview
Use this skill to consult the local Xcode AdditionalDocumentation file for "{title}" when implementing or reviewing related features. Keep context minimal: read only the relevant sections and summarize in your own words.

## Workflow
1. Define the concrete question or decision you need to make.
2. Read the smallest necessary section(s) from the reference file.
3. Summarize relevant guidance and apply it to code/tests.

## Reference
- Path: `{path}`
- Notes: This file can change with Xcode updates; cite the file path and Xcode build when using guidance.
"""

    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")


def write_index(version: str, build: str, skills: list[str]) -> None:
    content = """# Xcode AdditionalDocumentation Skills

Generated from the local Xcode AdditionalDocumentation directory.

- Xcode: {version} ({build})
- Source: {source}
- Skills: {count}

## Regeneration

Run:

```bash
python3 scripts/update_xcode_skills.py --clean
```

Then commit the changes and tag the repo using:

```
git tag -a "xcode-{version}-{build}" -m "Xcode {version} ({build})"
```
""".format(
        version=version,
        build=build,
        source=BASE_DIR,
        count=len(skills),
    )
    (SKILLS_DIR / "README.md").write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="Remove stale skill folders")
    args = parser.parse_args()

    if not BASE_DIR.exists():
        raise SystemExit(f"Missing Xcode AdditionalDocumentation at {BASE_DIR}")

    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    version, build = xcode_version()

    md_files = sorted(BASE_DIR.glob("*.md"))
    expected = []

    for md_file in md_files:
        skill_name = normalize(md_file.stem)
        expected.append(skill_name)
        skill_dir = SKILLS_DIR / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        title = read_title(md_file)
        write_skill(skill_dir, title, md_file, version, build)

    if args.clean:
        for child in SKILLS_DIR.iterdir():
            if child.is_dir() and child.name not in expected:
                shutil.rmtree(child)

    write_index(version, build, expected)
    print(f"Generated {len(expected)} skills in {SKILLS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
