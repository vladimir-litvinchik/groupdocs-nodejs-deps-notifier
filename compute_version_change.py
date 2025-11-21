#!/usr/bin/env python3
import json
import sys
import argparse


def main() -> int:
	parser = argparse.ArgumentParser(description="Compute dependency version changes between two deps.json files")
	parser.add_argument("--old", required=True, help="Path to old deps.json")
	parser.add_argument("--new", required=True, help="Path to new deps.json")
	parser.add_argument("--title-out", required=True, help="Path to output title file")
	parser.add_argument("--body-out", required=True, help="Path to output body markdown file")
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
		# Write empty files to indicate no updates
		with open(args.title_out, "w", encoding="utf-8") as f:
			pass
		with open(args.body_out, "w", encoding="utf-8") as f:
			pass
		return 0

	# Generate title
	if len(updates) == 1:
		u = updates[0]
		title = f"Dependency update: {u['name']} {u['from'] or 'none'} -> {u['to']}"
	else:
		summary = ", ".join(f"{u['name']} {u['from'] or 'none'} -> {u['to']}" for u in updates)
		title = f"Dependency updates: {summary}"

	# Generate body
	lines = []
	for u in updates:
		from_str = u['from'] or 'none'
		lines.append(f"- {u['name']}: {from_str} -> {u['to']} (https://www.npmjs.com/package/{u['name']})")
	body = "\n".join(lines)

	# Write outputs
	with open(args.title_out, "w", encoding="utf-8") as f:
		f.write(title)
	with open(args.body_out, "w", encoding="utf-8") as f:
		f.write(body)

	return 0


if __name__ == "__main__":
	sys.exit(main())

