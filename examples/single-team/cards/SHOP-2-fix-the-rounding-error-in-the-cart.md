---
id: SHOP-2
title: Fix the rounding error in the cart total
status: live
type: bug
transitions:
  - { to: next, at: 2026-10-27T08:45:00+01:00, by: sara }
  - { to: build, at: 2026-10-27T09:00:00+01:00, by: sara }
  - { to: review, at: 2026-10-27T16:40:00+01:00, by: sara }
  - { to: live, at: 2026-10-28T10:15:00+01:00, by: ali }
---

Totals with three items at CHF 9.95 show one cent too much. Found by a customer.
