---
id: database-catalog
title: Astronomy Shop PostgreSQL catalog
type: reference
service: astronomy-db
source: opentelemetry-demo/src/postgresql/init.sql
---

# Astronomy Shop PostgreSQL catalog

The demo PostgreSQL instance contains database `astronomy_db`. `catalog.products` holds product ID, name, description, picture, price currency, price units, price nanos, and category text.

The `accounting` schema holds `order`, `shipping`, and `orderitem` tables. Accounting records are useful when investigating completed checkout activity.

The application role is `astronomy_user`. A `monitoring_user` has the `pg_monitor` role for visibility. The investigation agent must use a dedicated read-only connection and allowlisted query templates. It must never issue inserts, updates, deletes, DDL, or free-form SQL.

Known product `OLJCESPC7Z` is the National Park Foundation Explorascope and is used by the product catalog failure flag's targeting rule.
