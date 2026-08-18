---
id: architecture-overview
title: Astronomy Shop architecture overview
type: architecture
service: platform
source: opentelemetry-demo/compose.yaml
---

# Astronomy Shop architecture overview

Astronomy Shop is a microservice demo application instrumented with OpenTelemetry. The user-facing request path enters through `frontend-proxy` and `frontend`. Common downstream services include cart, checkout, product-catalog, recommendation, ad, payment, shipping, currency, and email.

The demo exports telemetry to the OpenTelemetry Collector. With the observability Compose overlay enabled, traces are queryable in Jaeger and metrics are queryable in Prometheus and Grafana.

For investigation, start from the failing user-facing service, then follow one trace to the downstream service with errors or elevated duration. Do not assume a service is the root cause only because it is the first service with an error span.

The project labels service criticality in Compose. Checkout, frontend, frontend-proxy, and payment are marked critical; cart, product-catalog, and shipping are high criticality.
