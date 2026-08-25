# 17 — Data Modeling & Warehousing Handbook

> **The single most under-prepared topic in DE interviews.** Every product company
> (Amazon, Uber, Airbnb, Swiggy, Flipkart, Atlassian) makes you model a schema on a
> whiteboard. "Design the data model for X" separates a coder from a data engineer.
> Target: 80–120 LPA senior/staff/principal roles.

---

## 🎯 Why This Handbook Exists

You can write perfect PySpark and still fail the loop if you can't answer:
*"Model the data warehouse for a food-delivery / ride-hailing / e-commerce business."*
This is a **design** round, not a coding round. Interviewers grade: correct **grain**,
right **fact/dimension split**, **SCD** handling, and the **trade-offs** you name.

---

## 📐 SECTION 1: The Two Schools (know when to use each)

| Approach | Author | Idea | Best for |
|---|---|---|---|
| **Dimensional (Star)** | Kimball | Denormalized facts + dimensions, business-process centric | BI, analytics, 90% of interviews |
| **Normalized (3NF)** | Inmon | Enterprise-wide normalized core, marts built on top | Large enterprises, single source of truth |
| **Data Vault 2.0** | Linstedt | Hubs/Links/Satellites, insert-only, auditable | Regulated, fast-changing, many sources |
| **One Big Table (OBT)** | Modern | Fully denormalized wide table | Columnar warehouses (BigQuery), dashboards |

**Interview line:** *"I default to Kimball dimensional modeling for analytics because it's
intuitive for the business and performant on columnar warehouses. I'd reach for Data
Vault only when auditability and many changing sources dominate."*

---

## ⭐ SECTION 2: Star Schema (the core skill)

```
                 ┌───────────────┐
                 │  dim_customer │
                 └───────┬───────┘
┌──────────────┐         │          ┌──────────────┐
│  dim_date    ├───┐  ┌──┴───────┐  │  dim_product │
└──────────────┘   └──┤ fct_sales├──┘──────────────┘
                      └──┬───────┘
                 ┌───────┴───────┐
                 │  dim_store    │
                 └───────────────┘
```

- **Fact table** = the business PROCESS event (a sale, a click, a ride). Contains
  **foreign keys** to dimensions + **numeric, additive measures** (amount, quantity).
- **Dimension table** = the descriptive CONTEXT (who, what, where, when). Wide, textual,
  relatively small, denormalized.

**Snowflake schema** = a star where dimensions are further normalized into sub-dimensions
(e.g. `dim_product → dim_category`). Saves space, costs joins. *Prefer star for analytics.*

---

## 🎯 SECTION 3: GRAIN — the #1 thing interviewers probe

> **Declare the grain FIRST, before columns.** "One row per ______."

- Grain of `fct_orders` = **one row per order**.
- Grain of `fct_order_items` = **one row per line item** (finer).
- Never mix grains in one fact table — it causes double counting.

**Interview trap:** *"You joined orders (1) to items (many) and summed order_amount →
you multiplied revenue by item count."* Naming the grain prevents this.

### Three fact-table types
| Type | Description | Example |
|---|---|---|
| **Transaction** | One row per event, additive | Each sale, each click |
| **Periodic snapshot** | State at regular intervals | Daily account balance |
| **Accumulating snapshot** | One row per process, updated as it moves | Order lifecycle (placed→shipped→delivered) with milestone dates |

### Additivity of measures
- **Additive**: sum across ALL dimensions (revenue, quantity).
- **Semi-additive**: sum across some, not time (account balance, inventory).
- **Non-additive**: never sum (ratios, %, unit price) — store components, compute at query time.

---

## 🕰️ SECTION 4: Slowly Changing Dimensions (SCD) — asked constantly

A customer moves city. How do you store history?

| Type | Behavior | When |
|---|---|---|
| **SCD 0** | Never changes (retain original) | birth_date, signup_source |
| **SCD 1** | Overwrite, no history | fix a typo; current-state only |
| **SCD 2** | New row per change + validity dates | **the default for history** |
| **SCD 3** | Add a "previous value" column | limited, one prior value |
| **SCD 4** | Current table + history mini-dimension | rapidly changing attrs |
| **SCD 6** | 1+2+3 hybrid (current + rows + prior col) | need both current and historical views |

### SCD Type 2 pattern (know this cold)
```sql
-- dim_customer with SCD2
customer_sk   -- surrogate key (PK, per-version)
customer_id   -- natural/business key (stable)
city
effective_from   TIMESTAMP
effective_to     TIMESTAMP   -- '9999-12-31' for current
is_current       BOOLEAN
```
```sql
-- MERGE to apply an SCD2 change (Delta/Snowflake style)
MERGE INTO dim_customer t
USING staged_changes s
  ON t.customer_id = s.customer_id AND t.is_current = TRUE
WHEN MATCHED AND t.city <> s.city THEN
  UPDATE SET is_current = FALSE, effective_to = current_timestamp();
-- then INSERT the new current version in a second step (or use a stream/dbt snapshot)
```
**Interview line:** *"Surrogate key per version, natural key stable, effective_from/to +
is_current. A fact joins to the surrogate key valid at the event time — that's how you
get point-in-time-correct history."*

---

## 🔑 SECTION 5: Keys

- **Natural / business key**: from the source (email, order_id). Can change/reuse.
- **Surrogate key**: warehouse-generated integer/hash, meaningless, stable. **Use these
  as fact FKs** so SCD2 versioning and source changes don't break facts.
- **Degenerate dimension**: a dimension key with no dimension table (e.g. `order_id`
  stored on the fact for drill-through).
- **Conformed dimension**: ONE `dim_date`/`dim_customer` shared across many facts, so
  metrics are comparable across business processes. *Key enterprise concept.*
- **Junk dimension**: bundle low-cardinality flags (is_gift, channel) into one small dim.

---

## 🏛️ SECTION 6: Data Vault 2.0 (mention for staff/principal)

Insert-only, audit-friendly, source-agnostic core:
- **Hub** = unique list of business keys (Hub_Customer: customer_id + load metadata).
- **Link** = relationship between hubs (Link_Order: customer ↔ product).
- **Satellite** = descriptive, time-stamped attributes hanging off hubs/links (history).

**Why:** parallel loads, full lineage/audit, absorb schema change from many sources.
**Cost:** many joins → you build **star-schema marts on top** for consumption.
*Say:* "Vault for the integration layer, star marts for the presentation layer."

---

## 🧱 SECTION 7: Modeling for Modern Columnar Warehouses

- Columnar stores (BigQuery, Snowflake, Redshift, Delta) make **wide denormalized
  tables** (OBT) cheap to scan → sometimes beat classic star for dashboards.
- **Nested/repeated** types (STRUCT/ARRAY) let you model 1:many without a join
  (BigQuery events). Trade-off: harder to update, tooling support varies.
- **Partition** on the date you filter; **cluster/sort** on high-cardinality join/filter
  keys. Modeling and physical layout are inseparable at scale (see Handbook 19).

---

## 🧩 SECTION 8: The 4-Step Kimball Design Process (use it live)

1. **Pick the business process** (orders, shipments, page views).
2. **Declare the grain** ("one row per order line").
3. **Identify the dimensions** (who/what/where/when → customer, product, store, date).
4. **Identify the facts** (numeric measures at that grain → quantity, amount, discount).

Do these four out loud and you've structured 80% of any modeling interview.

---

## 🏢 SECTION 9: Worked Example — Ride-Hailing (Uber-style)

**Process:** completed trips. **Grain:** one row per completed trip.

```
fct_trips (grain: 1 trip)
  trip_id (degenerate)          rider_sk  → dim_rider (SCD2)
  driver_sk → dim_driver (SCD2) city_sk   → dim_city
  date_sk   → dim_date          payment_sk→ dim_payment_type (junk dim)
  -- measures:
  fare_amount, surge_multiplier(non-add), distance_km,
  duration_sec, tip_amount, driver_payout, platform_fee
```
Design talking points to volunteer:
- **surge_multiplier is non-additive** → store fare components, derive ratios at query time.
- **driver location change** → SCD2 on dim_driver so historical trips keep the right city.
- **cancelled trips** → separate fact or a status; don't pollute completed-trip grain.
- **accumulating snapshot** `fct_trip_lifecycle` (requested→matched→started→ended times)
  to analyze funnel latencies.

---

## ❓ SECTION 10: Rapid-Fire Interview Q&A

**Q: Star vs snowflake?** Star = denormalized dims, fewer joins, faster BI. Snowflake =
normalized dims, less storage, more joins. Prefer star for analytics.

**Q: How do you handle a late-arriving dimension?** Insert an inferred ("unknown") member
with the natural key, fact points to it, backfill attributes when the dim row arrives.

**Q: Fact vs dimension — how do you decide?** Numeric + measured at an event → fact.
Descriptive context you filter/group by → dimension.

**Q: How to prevent double counting?** One grain per fact; keep additive measures on their
native grain; use fan-out-safe joins or pre-aggregation.

**Q: What is a factless fact table?** A fact with only keys, no measures — records that an
event happened (student attended class, promotion was eligible). Count rows.

**Q: How do you model many-to-many (student↔course)?** A bridge table (associative fact)
at the pair grain, optionally with an allocation/weight factor.

**Q: 3NF vs dimensional?** 3NF removes redundancy for OLTP writes; dimensional optimizes
reads/analytics. Warehouses read-heavy → dimensional.

**Q: What is a conformed dimension and why care?** A shared dimension used across facts so
metrics are comparable enterprise-wide (same `dim_date`, same `dim_customer`).

---

## ✅ Mastery Checklist
- [ ] Declare grain before columns, every time
- [ ] Implement SCD2 with surrogate keys + effective dates from memory
- [ ] Explain additive / semi-additive / non-additive with examples
- [ ] Run the 4-step Kimball process live on any business
- [ ] Know when Data Vault beats a plain star (and that you'd still build star marts)
- [ ] Model a nested/OBT variant for a columnar warehouse and state the trade-off

---

## 🧪 Hands-On Practice (runnable)

Run the companion file to BUILD a star schema, apply an SCD Type 2 change, and prove
point-in-time-correct joins + the fan-out trap — all self-checking with assertions:

```bash
pip install -r ../requirements_practice.txt      # duckdb
python3 02_Practice_SCD2_and_Star_Schema.py
```
Covers: SCD2 (surrogate keys + effective dates), additive vs non-additive measures,
and the double-counting fan-out bug with its fix.
