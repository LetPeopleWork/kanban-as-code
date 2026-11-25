---
id: KAC-6
title: Backfill transitions from git history
status: review
transitions:
  - { to: next, at: 2026-11-07T15:13:29+01:00, by: benjamin }
  - { to: doing, at: 2026-11-25T16:46:01+01:00, by: benjamin }
  - { to: review, at: 2026-11-25T16:46:01+01:00, by: benjamin }
---

Since the history moved into the card files, a git reader is no longer part of the standard. It became a repair tool: `tools/backfill-from-git.py` rebuilds missing `transitions` from the git history of a card. We used it for this repo's own cards and for the obAIa cards.
