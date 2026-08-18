---
id: runbook-ad-cpu
title: Runbook: ad service CPU pressure
type: runbook
service: ad
source: synthetic-learning-doc
---

# Runbook: ad service CPU pressure

`adHighCpu` injects high CPU load in the ad service. `adManualGc` triggers full manual garbage collection, and `adFailure` makes the ad service fail.

When the homepage or advertising requests are slow, first separate latency from failure rate. Check ad-service metrics, then traces from frontend to ad. A downstream ad issue can degrade page composition without necessarily breaking checkout.

For a lab experiment, enable one flag at a time. Keep the time window and selected variant in the incident note so an evaluation can distinguish intentional fault injection from an unknown regression.
