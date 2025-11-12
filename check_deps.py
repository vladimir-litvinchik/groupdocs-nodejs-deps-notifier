#!/usr/bin/env python3
import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


TRACKED_PACKAGES = [
	"java",
	"node-gyp",
]

REGISTRY_DIST_TAGS_URL = "https://registry.npmjs.org/-/package/{name}/dist-tags"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEPS_JSON_PATH = os.path.join(ROOT_DIR, "deps.json")


def fetch_latest_version(package_name: str) -> str:
	url = REGISTRY_DIST_TAGS_URL.format(name=package_name)
	req = Request(url, headers={"User-Agent": "deps-checker/1.0"})
	try:
		with urlopen(req, timeout=20) as resp:
			data = resp.read().decode("utf-8")
			obj = json.loads(data)
			latest = obj.get("latest")
			if not isinstance(latest, str) or not latest:
				raise ValueError(f"Latest tag missing for {package_name}")
			return latest
	except HTTPError as e:
		raise RuntimeError(f"HTTP error fetching {package_name}: {e.code}") from e
	except URLError as e:
		raise RuntimeError(f"Network error fetching {package_name}: {e.reason}") from e


def read_current_deps(path: str) -> dict:
	if not os.path.exists(path):
		return {}
	with open(path, "r", encoding="utf-8") as f:
		try:
			return json.load(f)
		except json.JSONDecodeError as e:
			raise RuntimeError(f"Invalid JSON in {path}: {e}") from e


def write_deps(path: str, deps: dict) -> None:
	# Keep deterministic ordering for clean diffs
	with open(path, "w", encoding="utf-8", newline="\n") as f:
		json.dump(deps, f, indent=2, sort_keys=True)
		f.write("\n")


def main() -> int:
	current = read_current_deps(DEPS_JSON_PATH)
	updated = dict(current)
	changes = []

	for name in TRACKED_PACKAGES:
		try:
			latest = fetch_latest_version(name)
		except Exception as e:
			print(f"[ERROR] Failed to fetch latest for {name}: {e}", file=sys.stderr)
			continue

		prev = current.get(name)
		if prev != latest:
			changes.append((name, prev, latest))
			updated[name] = latest
			print(f"[INFO] {name}: {prev or 'none'} -> {latest}")
		else:
			print(f"[INFO] {name} is up-to-date at {latest}")

	if not changes and current:
		print("[INFO] No dependency updates found.")
		return 0

	# Ensure keys for all tracked packages exist even if fetch failed
	for name in TRACKED_PACKAGES:
		if name not in updated:
			# If we couldn't fetch, keep previous value if present, else skip setting
			if name in current:
				updated[name] = current[name]

	write_deps(DEPS_JSON_PATH, updated)

	# Optional: emit a simple summary for logs
	if changes:
		summary = "; ".join(f"{n} {o or 'none'} -> {nv}" for n, o, nv in changes)
		print(f"[SUMMARY] Updated: {summary}")
	else:
		print("[SUMMARY] Initialized deps.json")

	# Exit 0 so the workflow proceeds to commit if there are file changes;
	# if no changes, the auto-commit step will noop.
	return 0


if __name__ == "__main__":
	sys.exit(main())


