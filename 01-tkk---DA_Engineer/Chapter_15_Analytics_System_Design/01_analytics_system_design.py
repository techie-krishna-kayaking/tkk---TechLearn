# ============================================================
# CHAPTER 15: ANALYTICS SYSTEM DESIGN (Staff-level round)
# Read as: VS Code (Markdown-in-Python) — a talk-track, not code.
# At 75-80 LPA you get an OPEN-ENDED design question:
#   "Design the analytics/experimentation/metrics system for X."
# This chapter gives you the FRAMEWORKS to structure that answer.
# ============================================================
"""
HOW TO RUN THIS CHAPTER
-----------------------
There's nothing to execute — read each design and rehearse saying
it out loud in 5-7 minutes. System-design rounds grade STRUCTURE
and TRADE-OFFS, not code. Always: clarify -> requirements -> design
-> trade-offs -> failure modes -> metrics of success.
"""

# ============================================================
# SECTION 0: UNIVERSAL DESIGN FRAMEWORK (open EVERY answer with this)
# ------------------------------------------------------------
# 1. CLARIFY   : scale, users, latency (real-time vs daily), budget.
# 2. REQS      : functional (what it must do) + non-functional
#                (freshness, reliability, cost, governance).
# 3. HIGH LEVEL: draw the pipeline boxes L->R.
# 4. DEEP DIVE : the 1-2 hardest components.
# 5. TRADE-OFFS: name at least two, with your recommendation.
# 6. FAILURE   : what breaks, how you detect + recover.
# 7. SUCCESS   : how you'd measure the system is working.
# ============================================================


# ============================================================
# DESIGN 1: END-TO-END ANALYTICS PIPELINE ("design our data platform")
# ------------------------------------------------------------
DESIGN_1 = """
FLOW (say it L->R):
  Sources (app events, prod DB, 3rd-party APIs)
    -> Ingestion: streaming (Kafka/Kinesis) for events,
                  batch CDC (Fivetran/Airbyte/Debezium) for DB tables
    -> Lake/Warehouse landing (S3/GCS + Snowflake/BigQuery)  [BRONZE]
    -> Transform: dbt models, tested + documented             [SILVER]
    -> Marts: star schemas, semantic layer                    [GOLD]
    -> Consumption: BI (Looker), notebooks, reverse-ETL, ML.

KEY DECISIONS + TRADE-OFFS:
  * ELT over ETL: load raw first, transform in-warehouse. Cheaper
    compute, full replay-ability, SQL-based transforms in dbt.
  * Batch vs streaming: default batch (hourly/daily); add streaming
    ONLY where latency has real $ value (fraud, ops dashboards).
  * Build vs buy: buy ingestion (Fivetran), own transformation (dbt)
    — that's where business logic + differentiation lives.

FAILURE MODES + GUARDRAILS:
  * Source schema change -> dbt tests + source freshness alerts.
  * Late/duplicate events -> idempotent MERGE on natural keys.
  * Backfills -> partitioned, incremental models you can replay.
SUCCESS METRICS: data freshness SLA %, test pass rate, pipeline
  uptime, cost per TB, time-to-answer for a new metric.
"""

# ============================================================
# DESIGN 2: EXPERIMENTATION PLATFORM (Meta/Uber/Booking favorite)
# ------------------------------------------------------------
DESIGN_2 = """
GOAL: let any PM safely run trustworthy A/B tests at scale.

COMPONENTS:
  1. Assignment service: deterministic hash(user_id + exp_id) -> bucket
     => sticky, uniform, independent across experiments.
  2. Config/registry: experiment metadata, hypotheses, guardrail
     metrics, start/stop, mutual-exclusion groups (layers).
  3. Exposure logging: log WHO was actually exposed (not just eligible)
     — analyze on exposure to avoid dilution.
  4. Metrics/stats engine: precomputed metric pipelines, CUPED
     variance reduction, sequential/always-valid tests, CIs.
  5. Guardrails + health: Sample Ratio Mismatch (SRM) check, novelty
     detection, automatic alerting, scorecard UI.

TRADE-OFFS:
  * Fixed-horizon (simple, no peeking) vs always-valid (can peek,
    slightly less power). Offer both; default fixed for most PMs.
  * Client-side vs server-side assignment: server-side avoids
    flicker + leakage but needs a call in the request path.

FAILURE MODES:
  * SRM (e.g. 55/45 split when 50/50 expected) => STOP, don't trust.
  * Interference/network effects => switchback or cluster randomization.
  * Multiple comparisons across many metrics => control FDR.
SUCCESS: # trustworthy experiments/quarter, false-positive rate at
  target alpha, time-to-readout, % decisions backed by experiments.
"""

# ============================================================
# DESIGN 3: METRICS FRAMEWORK & NORTH STAR TREE
# ------------------------------------------------------------
DESIGN_3 = """
Build the metric TREE, not a pile of KPIs:

  NORTH STAR (one): e.g. "weekly active buyers" (value delivered).
    = Acquisition x Activation x Retention x Monetization
  Each branch decomposes into INPUT metrics teams can move:
    Retention = f(order frequency, delivery reliability, app quality)

PRINCIPLES:
  * North Star must reflect CUSTOMER VALUE, not vanity (not 'signups').
  * Pair every 'growth' metric with a GUARDRAIL (quality/cost) to
    prevent gaming (e.g. GMV up but refunds/complaints up = bad).
  * Every metric has an OWNER, definition, grain, and caveats
    (the metric dictionary) — governed in the semantic layer.
  * Distinguish INPUT (controllable, leading) vs OUTPUT (lagging).

WORKED TREE (food delivery):
  North Star: Weekly Active Eaters
   ├─ New eaters      = traffic x signup CVR x first-order CVR
   ├─ Retained eaters = f(delivery time, order accuracy, promos)
   └─ Frequency       = f(selection, price, subscription)
  Guardrails: refund rate, avg delivery time, unit economics.
"""

# ============================================================
# DESIGN 4: EVENT TRACKING / TAXONOMY (data-quality-at-source)
# ------------------------------------------------------------
DESIGN_4 = """
Bad analytics usually starts with bad EVENTS. Design the contract:

  * Naming convention: object_action, snake_case
    (e.g. checkout_started, order_placed, payment_failed).
  * Standard property schema on EVERY event: user_id, session_id,
    device, app_version, ts (UTC), source, plus event-specific props.
  * A TRACKING PLAN (Segment/Avo style): the schema is code-reviewed;
    events are validated against it BEFORE they land (schema registry).
  * Identity resolution: stitch anonymous_id -> user_id on login so
    pre/post-signup journeys join correctly.
  * Versioning: additive changes only; never silently repurpose a
    field. Breaking change => new event name.

WHY SENIOR: garbage-in means every downstream metric lies. Owning the
tracking plan = owning data trust at the source. Data CONTRACTS between
producers (engineers) and consumers (analysts) prevent silent breakage.
"""

# ============================================================
# DESIGN 5: DATA QUALITY & OBSERVABILITY
# ------------------------------------------------------------
DESIGN_5 = """
Trust is the analyst's product. Layer the defenses:
  * Tests (dbt): unique, not_null, relationships, accepted_values,
    accepted_range — run in CI on every PR + on each production run.
  * Freshness SLAs: alert if a source/table is stale beyond threshold.
  * Anomaly detection: volume, null-rate, and metric-value monitors
    (Monte Carlo / Elementary / custom) to catch silent drift.
  * The 6 data-quality dimensions to name: accuracy, completeness,
    consistency, timeliness, validity, uniqueness.
  * Incident response: severity levels, on-call, blameless postmortems,
    and a status page for 'is the revenue dashboard trustworthy today?'.
SUCCESS: mean-time-to-detect / -to-resolve, # incidents reaching
  stakeholders, % tables with tests + owners.
"""

# ============================================================
# DESIGN 6: REAL-TIME vs BATCH (Lambda/Kappa) — when asked
# ------------------------------------------------------------
DESIGN_6 = """
  * Batch: cheap, simple, replayable — default for reporting/finance.
  * Streaming: Kafka + Flink/Spark Streaming for sub-minute needs
    (live ops, fraud, personalization).
  * Lambda architecture: batch layer (accurate, slow) + speed layer
    (fast, approximate) merged at serve time. Kappa: streaming-only,
    reprocess by replaying the log — simpler if your stack allows.
  * Decide by the COST OF STALENESS: if a 1-hour-old number costs
    real money, stream; otherwise batch. Don't over-engineer latency.
"""

# ============================================================
# CLOSING LINE FOR ANY SYSTEM-DESIGN ROUND
# ------------------------------------------------------------
CLOSE = """
"I'd start simple and batch, make it TRUSTWORTHY with tests,
 freshness, and clear ownership, and only add real-time or ML
 complexity where the business value clearly pays for it. I'd
 measure the system by decisions enabled and trust maintained,
 not by pipelines built."
"""

if __name__ == "__main__":
    for name, text in [("PIPELINE", DESIGN_1), ("EXPERIMENTATION", DESIGN_2),
                       ("METRICS TREE", DESIGN_3), ("EVENT TAXONOMY", DESIGN_4),
                       ("DATA QUALITY", DESIGN_5), ("REAL-TIME vs BATCH", DESIGN_6)]:
        print(f"\n{'='*60}\n{name}\n{'='*60}{text}")
    print(CLOSE)
