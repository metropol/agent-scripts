# agent-scripts

Utilities and shared assets for agent workflows.

## Xcode AdditionalDocumentation skills

This repo includes generated skills under `skills/xcode-additional-docs`.

### Regenerate after Xcode updates

```bash
python3 scripts/update_xcode_skills.py --clean
```

Then commit changes and tag using the Xcode version and build:

```bash
git tag -a "xcode-<version>-<build>" -m "Xcode <version> (<build>)"
```

Example:

```bash
git tag -a "xcode-16.4-16E300" -m "Xcode 16.4 (16E300)"
```

### Notes
- Skills reference the local AdditionalDocumentation paths and are not vendored.
- Users can clone this repo wherever they want and point Codex to the `skills/` folder.
