---
id: incident-product-catalog-002
title: Incident 002 - targeted product catalog fault
type: incident
service: product-catalog
date: 2026-08-18
source: synthetic-learning-doc
---

# Incident 002: targeted product catalog fault

## Summary

The `productCatalogFailure` flag targets product ID `OLJCESPC7Z`, National Park Foundation Explorascope. Other products can continue to load normally.

## Diagnosis

Query `catalog.products` by product ID to establish the product exists. Compare traces for the affected product with a different product. Look for a product-catalog error and the feature-flag evaluation; do not diagnose this as missing database data solely from a failed product request.

## Resolution

Set `productCatalogFailure` to `off` after collecting before-state evidence. Retry the exact product ID and record a successful trace.
