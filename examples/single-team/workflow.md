---
key: SHOP
states:
  - { id: next, name: Next, category: todo }
  - { id: build, name: Build, category: doing }
  - { id: review, name: Review, category: doing }
  - { id: test, name: Test, category: doing }
  - { id: live, name: Live, category: done }
sle: { days: 10, probability: 85 }
---

# Web shop team

A made-up team of four that runs a small web shop. The files are an example, not real data.

## How we control WIP

At most two items per person in Build, Review and Test together. When a card is blocked, we swarm on it before
we pull anything new.

## Policies

- Next: the card says what we want and why. The team orders the top five every Monday.
- Build: someone pulled the card. The change is on a branch.
- Review: another person reads the change before it is merged.
- Test: the change runs on the staging shop, and someone who did not build it has tried it.
- Live: the change is in production.

## Service level expectation

85% of items are live within 10 days of entering Build.
