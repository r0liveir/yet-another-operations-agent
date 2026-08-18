---
id: telemetry-investigation
title: Telemetry investigation guide
type: runbook
service: platform
source: synthetic-learning-doc
---

# Telemetry investigation guide

Use a narrow time range first, preferably the previous 15 minutes. Start with Prometheus for rate, error, and latency changes. Then use Jaeger to inspect representative slow or failed traces. Use logs only to explain an already identified span or request.

Prometheus answers aggregate questions such as “did error rate rise?” Jaeger answers causal questions such as “which downstream call made checkout fail?” PostgreSQL answers state questions such as “does a product exist?”

Record evidence with the query, time range, service, and trace ID. An answer based on telemetry must identify it as live evidence, not as a documentation citation.

If no telemetry supports the claim, say `needs_more_data`. Never invent metric values, trace IDs, or log lines.
