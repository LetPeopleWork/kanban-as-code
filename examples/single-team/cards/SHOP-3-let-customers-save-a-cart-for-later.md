---
id: SHOP-3
title: Let customers save a cart for later
status: live
transitions:
  - { to: next, at: 2026-10-26T09:20:00+01:00, by: mia }
  - { to: build, at: 2026-10-29T09:00:00+01:00, by: ali }
  - { to: review, at: 2026-11-03T14:00:00+01:00, by: ali }
  - { to: build, at: 2026-11-04T10:30:00+01:00, by: ali }
  - { to: review, at: 2026-11-05T16:10:00+01:00, by: ali }
  - { to: test, at: 2026-11-06T13:00:00+01:00, by: jonas }
  - { to: live, at: 2026-11-10T09:00:00+01:00, by: jonas }
---

Review found that saved carts were not cleared after checkout, so the card went back to Build once.
