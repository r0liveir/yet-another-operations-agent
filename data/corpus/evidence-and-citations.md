---
id: evidence-and-citations
title: Evidence and citation policy
type: policy
service: platform
source: synthetic-learning-doc
---

# Evidence and citation policy

Every answer must separate static corpus citations from live investigation evidence.

- Corpus citation: document ID, title, and chunk reference.
- Metric evidence: PromQL query and exact time range.
- Trace evidence: trace ID, service, operation, and time range.
- Database evidence: approved query-template ID and parameters; never include credentials.

Use `answered` only when evidence supports conclusion. Use `needs_more_data` when documents or live tools cannot establish answer. Use `failed` when a required dependency fails after retry/timeout handling.

The agent may summarize evidence but must not fabricate citations, tool calls, values, or incident timelines.
