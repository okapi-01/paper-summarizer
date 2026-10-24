#!/usr/bin/env python3
"""Append a paper summary section to the user's running notes file.

Usage: python3 append_notes.py <target_file_path> <summary_markdown_text>

Creates the file (with a top-level header) if it doesn't exist yet.
Never overwrites or reorders existing content — always appends at the end.
"""
import sys
import os


def main():
    if len(sys.argv) < 3:
        print("Usage: append_notes.py <target_file_path> <summary_markdown_text>",
              file=sys.stderr)
        sys.exit(1)

    target_path = os.path.expanduser(sys.argv[1])
    summary_text = sys.argv[2]

    os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)

    with open(target_path, "a", encoding="utf-8") as f:
        f.write(summary_text.rstrip() + "\n\n")

    print(f"OK: appended to {target_path}")


if __name__ == "__main__":
    main()
