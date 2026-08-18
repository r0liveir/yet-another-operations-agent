---
id: incident-payment-outage-001
title: Incident 001: simulated payment outage
type: incident
service: payment
date: 2026-08-18
source: synthetic-learning-doc
---

# Incident 001: simulated payment outage

## Summary

During a local fault-injection exercise, checkout failures rose after `paymentUnreachable` was enabled. Product browsing and cart operations continued.

## Evidence to collect

- Prometheus: checkout error rate during the fault window.
- Jaeger: failed checkout traces with a payment child span.
- Feature-flag evaluation: `paymentUnreachable` returned `on`.

## Resolution

Set `paymentUnreachable` to `off`. Confirm new checkout traces reach payment successfully and checkout errors fall. This is a synthetic incident; it is intended as retrieval and evaluation ground truth, not a historical production event.
