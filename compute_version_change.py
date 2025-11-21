#!/usr/bin/env python3
import json
import sys
import argparse


def main() -> int:
	parser = argparse.ArgumentParser(description="Compute dependency version changes between two deps.json files")
	parser.add_argument("--old", required=True, help="Path to old deps.json")
	parser.add_argument("--new", required=True, help="Path to new deps.json")
	parser.add_argument("--out", required=True, help="Path to output markdown file")
	args = parser.parse_args()

	try:
		with open(args.old, "r", encoding="utf-8") as f:
			prev_deps = json.load(f)
	except FileNotFoundError:
		prev_deps = {}
	except json.JSONDecodeError as e:
		print(f"[ERROR] Invalid JSON in {args.old}: {e}", file=sys.stderr)
		return 1

	try:
		with open(args.new, "r", encoding="utf-8") as f:
			curr_deps = json.load(f)
	except FileNotFoundError:
		print(f"[ERROR] New deps file not found: {args.new}", file=sys.stderr)
		return 1
	except json.JSONDecodeError as e:
		print(f"[ERROR] Invalid JSON in {args.new}: {e}", file=sys.stderr)
		return 1

	updates = []
	for name in sorted(curr_deps.keys()):
		from_version = prev_deps.get(name)
		to_version = curr_deps.get(name)
		if to_version and from_version != to_version:
			updates.append({"name": name, "from": from_version, "to": to_version})

	if not updates:
		# Write empty file to indicate no updates
		with open(args.out, "w", encoding="utf-8") as f:
			pass
		return 0

	# Generate markdown summary
	with open(args.out, "w", encoding="utf-8") as f:
		f.write("### Dependency Updates\n\n")
		for u in updates:
			from_str = u['from'] or 'none'
			f.write(f"- **{u['name']}**: {from_str} -> {u['to']}\n")
			f.write(f"  - https://www.npmjs.com/package/{u['name']}\n")

	return 0


if __name__ == "__main__":
	sys.exit(main())

