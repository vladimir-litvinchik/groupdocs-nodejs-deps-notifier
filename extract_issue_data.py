#!/usr/bin/env python3
import os
import re
import sys


def main() -> int:
	if len(sys.argv) < 2:
		print("Usage: extract_issue_data.py <markdown_file>", file=sys.stderr)
		return 1

	markdown_file = sys.argv[1]

	try:
		with open(markdown_file, 'r') as f:
			content = f.read()
	except FileNotFoundError:
		return 0

	# Extract updates from markdown
	pattern = r'- \*\*([^*]+)\*\*: ([^ ]+) -> ([^\n]+)'
	matches = re.findall(pattern, content)

	if not matches:
		return 0

	updates = [{'name': m[0], 'from': m[1], 'to': m[2]} for m in matches]

	# Generate title
	if len(updates) == 1:
		u = updates[0]
		title = f"Dependency update: {u['name']} {u['from']} -> {u['to']}"
	else:
		summary = ", ".join(f"{u['name']} {u['from']} -> {u['to']}" for u in updates)
		title = f"Dependency updates: {summary}"

	# Generate body (remove markdown formatting)
	body_lines = []
	for u in updates:
		body_lines.append(f"- {u['name']}: {u['from']} -> {u['to']} (https://www.npmjs.com/package/{u['name']})")
	body = "\n".join(body_lines)

	# Write to GitHub Actions outputs
	with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
		f.write(f"title<<DELIMITER\n{title}\nDELIMITER\n")
		f.write(f"body<<DELIMITER\n{body}\nDELIMITER\n")

	return 0


if __name__ == "__main__":
	sys.exit(main())

