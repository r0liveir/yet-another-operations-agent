---
id: load-generator
title: Synthetic traffic generator
type: runbook
service: load-generator
source: opentelemetry-demo/src/load-generator/README.md
---

# Synthetic traffic generator

The `load-generator` service uses k6 to continuously make synthetic requests to Astronomy Shop. It creates traces and emits k6 metrics through OpenTelemetry.

Default traffic has five HTTP virtual users. Its workload randomly mixes index pages, product browsing, recommendations, ads, cart reads, cart writes, checkout, multi-item checkout, and homepage flooding. Browsing has much greater weight than checkout.

`loadGeneratorTraffic` controls whether synthetic traffic runs. `loadGeneratorVUs` offers 5, 10, 25, and 50 concurrent virtual-user variants. The wrapper restarts k6 when that flag changes. Do not set k6's reserved `K6_VUS` environment variable: it replaces the scripted scenarios.

Use generated traffic for local experiments. Increase virtual users gradually and watch service error rate and latency before changing feature flags.
