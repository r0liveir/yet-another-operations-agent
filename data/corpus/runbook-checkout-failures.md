---
id: runbook-checkout-failures
title: Runbook - checkout failures
type: runbook
service: checkout
source: synthetic-learning-doc
---

# Runbook: checkout failures

## Symptoms

Users can browse products and add items to cart, but checkout requests fail or end with payment errors.

## Investigation

1. Check checkout request/error rate in Prometheus for the incident window.
2. Find failed checkout traces in Jaeger and inspect child spans for payment, shipping, cart, and email.
3. Check feature flag evaluations in the same traces. `paymentFailure` injects charge failures at selected percentages; `paymentUnreachable` makes payment unavailable.
4. If payment spans succeed, inspect shipping and cart calls before calling payment the root cause.

## Safe mitigation for a lab

Turn the relevant demo failure flag off, confirm errors return to baseline, then record the flag state and evidence. Do not claim a mitigation worked without a post-change metric or trace check.
