---
key: KAC
history: git
states:
  - { id: next, name: Next, category: todo }
  - { id: doing, name: Doing, category: doing }
  - { id: review, name: Review, category: doing }
  - { id: done, name: Done, category: done }
sle: { days: 7, probability: 85 }
---

# Kanban as Code workflow

This repo tracks its own work with the standard it defines. We work trunk-based on `main`, so the cards live on `main` and git holds the history.

A work item is one change to the standard, the site or its tooling that someone can read and react to.

## How we control WIP

We finish what is in Review before we pull anything new, and we keep one item in Doing per person.

## Policies

- Next: the card says what we want and why. Anyone can add one.
- Doing: someone is working on it. Pulling a card means moving it here and pushing that commit.
- Review: the other founder has to read it. Nothing moves to Done without that.
- Done: merged to `main`, and the site is updated if the change affects it.

## Service level expectation

The `sle` above is a best guess until we have history.
