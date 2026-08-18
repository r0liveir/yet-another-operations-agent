---
id: ticket-recommendation-cache-003
title: Ticket 003: investigate recommendation degradation
type: ticket
service: recommendation
source: synthetic-learning-doc
---

# Ticket 003: investigate recommendation degradation

**Request:** Product pages sometimes show recommendation errors or slower recommendations. Determine whether cache failure injection is active.

`recommendationCacheFailure` simulates cache failure in the recommendation service. Inspect recommendation traces and the feature-flag evaluation. Compare recommendation requests with ordinary product-detail requests: product detail can succeed while recommendations fail.

Expected answer shape: state evidence, identify whether the flag is observed, list affected request path, and include trace or metric references. Do not recommend changing unrelated product-catalog data.
