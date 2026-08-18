---
id: runbook-cart-readiness
title: Runbook: cart readiness and failures
type: runbook
service: cart
source: synthetic-learning-doc
---

# Runbook: cart readiness and failures

`failedReadinessProbe` simulates a cart-service readiness-probe failure. `cartFailure` injects cart failures at configured percentages from 10% through 100%.

Cart failures can affect add-to-cart, cart viewing, and checkout. Compare these request paths before assuming checkout itself is broken. Search traces for cart spans and feature-flag evaluation spans. The user-facing error may originate in cart even when the top-level operation is checkout.

For a lab, turn off the fault flag after capturing evidence. Confirm recovery with new cart and checkout requests rather than relying on container health alone.
