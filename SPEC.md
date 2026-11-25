# Kanban as Code

Version 0.1, draft for comment. Nothing here is stable yet.

Kanban as Code describes how to keep a Kanban system in plain markdown files, usually in git. It defines the files only. Boards, charts and forecasts are the job of whatever tool reads them, and any tool can.

The words MUST, SHOULD and MAY have their usual meaning from RFC 2119.

This spec builds on [The Kanban Guide](https://kanbanguides.org/the-kanban-guide/) (May 2025). Read the guide for what a Kanban system is and why. This document only says where each part goes in the files.

## 1. Overview

There are two kinds of file:

- A **workflow file** defines one workflow: its states, where its cards live and how the team runs it.
- A **card** is one work item, one markdown file with frontmatter.

A card holds its current state and every transition that led there: which state it entered, when, and optionally who moved it. A tool needs nothing but the files. It does not have to read git, and squash merges, rebases and shallow clones lose nothing.

```
kanban/
├── workflow.md
└── cards/
    ├── KAC-1-write-v0-1-spec.md
    └── KAC-2-render-spec-on-site.md
```

This repo uses that layout and tracks its own work that way. See [`kanban/`](kanban/).

## 2. Workflow file

A workflow file is markdown with YAML frontmatter. By default it is `kanban/workflow.md`, but it MAY live anywhere, and a repo MAY hold any number of them.

```markdown
---
key: PAY
sources:
  - { repo: acme/payments, branch: kanban, paths: [cards/] }
states:
  - { id: ready, name: Ready, category: todo }
  - { id: build, name: Build, category: doing }
  - { id: test, name: Test, category: doing }
  - { id: live, name: Live, category: done }
sle: { days: 8, probability: 85 }
---

## How we control WIP
Two items per person, and we swarm on anything blocked.

## Policies
Test: someone other than the author has run it.
```

| Field | Required | Meaning |
| --- | --- | --- |
| `key` | yes | Short name of the workflow. It starts every card ID, and it MUST be unique across the workflows a tool reads. |
| `states` | yes | The states in board order. See below. |
| `sources` | no | Where the cards live. See section 5. Default: `cards/` next to the workflow file. |
| `sle` | no | Service level expectation: `days` and `probability` in percent. |

Each state has these fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Stable identifier. Cards and history use it. It MUST NOT change. |
| `name` | no | Display name. Change it whenever you like. Default: the `id`. |
| `category` | yes | `todo`, `doing` or `done`. |
| `retired` | no | `true` when the team no longer uses the state. |

The categories carry the start and finish points. An item is started when it first enters a `doing` state, and finished when it enters a `done` state. A workflow MAY have several states in each category, so it can have more than one way to start or finish.

A state MUST NOT be deleted while any history refers to it. Mark it `retired` instead, so old transitions keep their meaning. To rename a state, change `name`.

The body of the workflow file is free text. It MUST say how the team controls WIP and what its policies for each state are. These are text because the Kanban Guide leaves the method open: a number per column is one way to control WIP, and there are many others.

The `sle` field is optional because a tool MAY calculate an SLE from history. A team still needs one to run a Kanban system, and keeping it here means it survives a change of tool.

## 3. Cards

A card is a markdown file with YAML frontmatter. The body is free text.

```markdown
---
id: PAY-42
title: Export the report
status: build
transitions:
  - { to: ready, at: 2026-11-02T09:00:00Z }
  - { to: build, at: 2026-11-04T14:30:00+01:00, by: alice }
---

What we want and why.
```

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Unique within the workflow, and it starts with the workflow's `key` and a hyphen. |
| `title` | yes | What the work is. |
| `status` | yes | The `id` of the current state. |
| `transitions` | yes | The card's history. See section 4. |

Tools recognize these optional fields:

| Field | Meaning |
| --- | --- |
| `type` | The kind of work, for example `bug`. |
| `labels` | A list of tags. |
| `assignee` | Who is on it. A list when people pair. |
| `parent_task_id` | The `id` of the parent card. It MAY be in another workflow or repo. |
| `dependencies` | A list of card `id`s this card waits for. |
| `order` | Position among the cards in the same state. Lower comes first. |
| `blocked` | `true` while the card is blocked. |
| `url` | A link to the same item somewhere else. |

Teams MAY add any other field. Tools MUST keep fields they do not know when they rewrite a card.

After the key, an ID is any string, so a team can choose. A plain counter is fine when all cards live on one branch. When cards are created on several branches, two branches can take the same number, so use something that cannot collide, such as a date and a slug.

## 4. History

A tool needs every transition of a card: the state it entered, and when. Every card carries them in `transitions`, so the files are the only source.

```yaml
status: build
transitions:
  - { to: ready, at: 2026-11-02T09:00:00Z }
  - { to: build, at: 2026-11-04T14:30:00+01:00, by: alice }
```

Each entry has these fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `to` | yes | The `id` of the state the card entered. |
| `at` | yes | When, as an ISO 8601 date and time with a time zone offset or `Z`. |
| `by` | no | Who moved the card. |

The rules:

- The first entry is the card's creation, and its `to` is the state the card started in.
- The list MUST be in time order, and the `to` of its last entry MUST equal `status`.
- A move is one change to the file: set `status` and add an entry. A skill or a hook SHOULD do it, because people forget.
- Entries are only added, never changed or removed. A person MAY correct an obvious mistake by hand.

The history lives in the file, not in a version control system, so that any tool can read it. Git still matters: it stores the files, records who changed them, and does the locking in section 6. But no reader has to speak git.

### When status and history disagree

If `status` is not the `to` of the last entry, or `transitions` is missing, the card is invalid. A tool SHOULD report it and MUST NOT invent the missing entries silently.

A tool MAY offer a repair, for example by rebuilding the entries from the git history of the file, and it SHOULD show which entries it added that way. How such a repair works is not part of this standard.

### Derived dates

Tools work these out from the history, and they are not stored:

| Date | Rule |
| --- | --- |
| Created | The first transition. |
| Started | The first time the card enters a `doing` state. |
| Finished | The last time it enters a `done` state, as long as it is still in one. |

If a card goes back from `done`, it is no longer finished.

## 5. Where cards live

Each entry in `sources` has these fields:

| Field | Default | Meaning |
| --- | --- | --- |
| `repo` | This repo | The repository, for example `acme/payments`. |
| `branch` | The default branch | The branch that holds the cards. |
| `paths` | `[cards/]` | Folders with card files. Every `.md` file with an `id` in its frontmatter is a card. |

The rule behind all setups: the declared location is the truth. A card on any other branch does not count.

| Setup | How to do it |
| --- | --- |
| Trunk-based | Cards on `main`, next to the code. No `sources` needed. |
| Feature branches | A dedicated `kanban` branch in the same repo. See below. |
| One team, many repos | One repo holds the board, or `sources` lists several repos. |
| One org, one repo | One workflow file per team, each with its own folder and `key`. |
| Portfolio | A workflow of its own, whose cards are parents of cards in other workflows. |

### The dedicated branch

If a team works on feature branches, a move on a feature branch is invisible to everyone until it merges. The history survives the merge, even a squash merge, because it is in the file. But until then the board is out of date, and two people can pull the same card without noticing. Teams who want the board current at all times can keep the cards on a `kanban` branch that shares no history with the code and is never merged:

```sh
git worktree add --orphan -b kanban .kanban
echo .kanban >> .git/info/exclude
```

Moves are commits to that branch, pushed straight away. Code branches and merges do not touch it. A move can't be part of a code pull request, so a skill or hook should take care of it. The branch MUST allow direct pushes.

## 6. Pulling work

Pulling a card is a move like any other: change `status` to a `doing` state, add the transition, commit and push. There is no separate claim.

Git does the locking. If two people or agents pull the same card, the second push is refused and the rebase conflicts on the `status` line and the new entry. Whoever lost picks another card. This only works when everyone pushes to the same branch, which is another reason for the rule in section 5.

## 7. References across repos

A card is referred to by its `id`, for example `PORT-7`. Keys make these unique, so `parent_task_id: PORT-7` works across repos. A tool is told which workflows to read, and it finds the card by its key.

Commits SHOULD mention the card `id` in their message. Then `git log --grep PAY-42` gives the trail of a piece of work in a repo, and the same search in each repo covers the rest.

## 8. How this maps to the Kanban Guide

| The guide asks for | Here |
| --- | --- |
| Work items | Cards |
| When items start and finish | State categories |
| States between start and finish | `states` |
| How WIP is controlled | Workflow body |
| Policies for each state | Workflow body |
| Service level expectation | `sle`, or a tool |
| More than one workflow where needed | One workflow file each |
| WIP, throughput, work item age, cycle time | Calculated by tools from history |
| Visualization | Any tool. We define none. |

The guide also expects people to manage items actively and improve their workflow. No file format does that for you. Changes to the workflow file are in git too, so the team can see what it changed and when.

## 9. Use cases

### See the work

Any board tool can show the cards in columns from `states` and `status`. Teams can pick the board they like, or use more than one, because the files stay the same. A dashboard for managers and a terminal view for developers can read the same repo.

### Know how the work flows

From the transitions a tool can draw a cycle time scatterplot, a work item age chart, a throughput run chart and a cumulative flow diagram. Time per state shows where work waits. All of this needs the individual transitions, which is why start and finish dates alone are not enough.

### Forecast

Monte Carlo forecasting needs finished items per day and how many items remain. Both come from the files. With `parent_task_id` and `order`, a tool can forecast features and portfolios too.

### Let agents do the work

Agents already work in the repo, so the board is right there for them. They read the policies in the workflow file, pull a card, and git keeps them from taking the same one. A skill can do the moving, so developers keep working the way they like. The standard is built so that agents can keep the board true; whether they do is something each team should check in its own history.

### Audit what happened

Every move is an entry with a time and, if given, a person. In git each move is also a commit, so the version history confirms the entries, and code commits point to their card.

### Plan above the team

A portfolio workflow lives in its own repo or folder, and its cards are parents of cards in team workflows. A tool that reads all of them can roll progress up, whatever the repo layout.

### Change tools

The work and its whole history stay in the repo when a tool goes away.

## 10. Open questions

- A card that goes from `todo` straight to `done` has no start. Should it have no cycle time, or should tools fall back to the creation date?
- Cycle time in whole days or exact time? Should it count the first day? The guide doesn't say, and without a rule two tools can show different numbers for the same files.
- Does a tool need a shared way to find workflows, or is telling it enough?
- How do we split or merge a state, beyond retiring it?
- Should `at` also accept a plain date, for teams that only track days?
- Should the standard name one way to mark entries that a tool rebuilt, for example from git?
- How does a team discard a card it will not do? Delete the file, or move it to a `done` state with a reason?
- What is the right file layout when a team wants one board across many repos?
