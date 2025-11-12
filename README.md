## GroupDocs for Node.js dependency update notifier

Tracks selected npm dependencies and opens a GitHub issue when a new version is detected.

### How it works

- A scheduled workflow runs daily, executes `check_deps.py`, and commits `deps.json` changes.
- A second workflow triggers on `deps.json` changes and creates an issue summarizing updates.

### Tracked dependencies

- `java` — `https://www.npmjs.com/package/java`
- `node-gyp` — `https://www.npmjs.com/package/node-gyp`

### Run locally

1. Ensure Python 3 is installed.
2. From repo root, run:

```bash
python check_deps.py
```

This will create/update `deps.json` at the repository root.
