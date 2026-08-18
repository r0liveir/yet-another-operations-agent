---
id: runbook-slow-images
title: Runbook: slow product images
type: runbook
service: frontend
source: synthetic-learning-doc
---

# Runbook: slow product images

## Symptoms

Product pages load slowly while product and checkout APIs may remain healthy. Browser-oriented telemetry can show slow page navigation or image requests.

## Investigation

1. Compare frontend and image-provider duration before and during the suspected window.
2. Inspect frontend traces for image-provider child spans or slow resource requests.
3. Check the `imageSlowLoad` feature flag. Its variants simulate five- or ten-second image delays.
4. Verify product API latency separately; a slow image is not proof that product-catalog is slow.

## Lab remediation

Return `imageSlowLoad` to `off`, wait for fresh synthetic traffic, and compare a new trace with the earlier slow trace.
