#!/usr/bin/env python3
"""Rebuild missing `transitions` for Kanban as Code cards from their git history.

This is a repair tool, not part of the standard (see SPEC.md, section 4). It reads
every commit that touched a card, records each change of `status` as a transition,
and writes the list into the card's frontmatter. Cards that already have
`transitions` are left alone.

The times are commit times, so they are only as good as the commits: a move made
on Monday and committed on Friday shows up on Friday.

Usage:
    tools/backfill-from-git.py [--dry-run] [--by-lower-first-name] CARD.md [CARD.md ...]

Run it from inside the git repo that holds the cards.
"""

import argparse
import datetime
import re
import subprocess
import sys

STATUS_RE = re.compile(r"^status:\s*['\"]?([^'\"\s#]+)", re.M)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else None


def status_of(text):
    fm = frontmatter(text)
    if fm is None:
        return None
    m = STATUS_RE.search(fm)
    return m.group(1) if m else None


def history(path, by_first_name):
    """Yield (status, time, author) for each commit where status changed, oldest first."""
    log = git("log", "--follow", "--reverse", "--format=%H%x09%cI%x09%an", "--name-only", "--", path)
    entries = []
    lines = [line for line in log.splitlines() if line.strip()]
    i = 0
    while i < len(lines):
        sha, at, author = lines[i].split("\t")
        name_at_commit = lines[i + 1] if i + 1 < len(lines) else path
        i += 2
        try:
            text = git("show", f"{sha}:{name_at_commit}")
        except subprocess.CalledProcessError:
            continue  # deleted in this commit
        st = status_of(text)
        if st is None:
            continue
        if entries and entries[-1][0] == st:
            continue
        by = author.split()[0].lower() if by_first_name else author
        entries.append((st, at, by))
    return entries


def render(entries):
    out = ["transitions:"]
    for st, at, by in entries:
        out.append(f"  - {{ to: {st}, at: {at}, by: {by} }}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cards", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--by-lower-first-name", action="store_true",
                    help="write `by` as the author's first name in lower case")
    args = ap.parse_args()

    changed = skipped = 0
    for path in args.cards:
        text = open(path, encoding="utf-8").read()
        fm = frontmatter(text)
        if fm is None:
            print(f"SKIP (no frontmatter): {path}")
            skipped += 1
            continue
        if re.search(r"^transitions:", fm, re.M):
            print(f"SKIP (has transitions): {path}")
            skipped += 1
            continue
        entries = history(path, args.by_lower_first_name)
        current = status_of(text)
        if current and (not entries or entries[-1][0] != current):
            # The working copy moved the card after the last commit.
            now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
            entries.append((current, now, "unknown"))
        if not entries:
            print(f"SKIP (no history): {path}")
            skipped += 1
            continue
        end = text.find("\n---", 3)
        new_text = text[:end] + "\n" + render(entries) + text[end:]
        print(f"{'WOULD WRITE' if args.dry_run else 'WROTE'} {len(entries)} transition(s): {path}")
        if not args.dry_run:
            open(path, "w", encoding="utf-8").write(new_text)
        changed += 1
    print(f"{changed} card(s) backfilled, {skipped} skipped", file=sys.stderr)


if __name__ == "__main__":
    main()
