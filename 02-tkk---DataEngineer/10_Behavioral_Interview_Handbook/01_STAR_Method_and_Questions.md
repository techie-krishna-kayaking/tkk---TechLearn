# 10 — Behavioral Interview Handbook

> Technical rounds + behavioral rounds = the interview. Many candidates with strong
> technical skills lose offers because they give vague, unstructured behavioral answers.
> This handbook gives you the STAR framework + 50 questions with model answers.

---

## 🌟 The STAR Framework

Every behavioral answer should follow STAR:

```
S — Situation  → Context: what was the project, team, challenge? (2-3 sentences)
T — Task       → Your specific responsibility in that situation. (1-2 sentences)
A — Action     → What YOU did. Use "I", not "we". Be specific. (3-5 sentences)
R — Result     → Measurable outcome. Quantify where possible. (2-3 sentences)
```

**Timing:** Each answer should be 2-3 minutes max.
**Do:** Prepare 6-8 strong stories. Each story can answer multiple questions.
**Don't:** Say "we did" — interviewers want to know what YOU specifically did.

---

## 📊 Your Story Bank (Fill These In)

Prepare a story for each of these themes before your interview:

| Theme | What to Describe |
|---|---|
| **Technical Challenge** | Complex problem you solved (data quality, performance, pipeline design) |
| **Failure / Mistake** | Something you broke or got wrong, what you learned |
| **Conflict** | Disagreement with a teammate or stakeholder |
| **Leadership** | Time you led without authority, mentored someone |
| **Deadline Pressure** | Tight timeline, how you prioritised |
| **Ambiguity** | Requirements unclear, how you navigated |
| **Stakeholder Management** | Business person wanted X, you pushed back or aligned |
| **Data Quality Issue** | Bad data impacted business, how you handled it |

---

## 💬 50 Common Behavioral Questions + Model Answers

### 🔧 Technical Problem-Solving

**Q1: Tell me about a technically challenging data engineering problem you solved.**

```
Situation: At [Company], our main analytics pipeline was running 6+ hours daily.
           The business needed data by 7 AM; it was finishing at 1 PM.

Task: I owned the pipeline performance and had 3 weeks to fix it before Q4 peak.

Action: I profiled the Spark job using the Spark UI and found 3 root causes:
        (1) A join was creating a massive shuffle because one table had 500M rows
            and the join key was user_id, which was heavily skewed (top 100 users
            had 40% of all events).
        (2) We were writing 50,000 tiny Parquet files (small file problem).
        (3) spark.sql.shuffle.partitions was set to 200 for a 2TB dataset — too few.

        I applied:
        (1) Salting for the skewed join + AQE enabled to auto-handle future skew.
        (2) coalesce(200) before the write + OPTIMIZE on the Delta table weekly.
        (3) Set shuffle.partitions to 800 to match the dataset size.

Result: Pipeline dropped from 6.5 hours to 47 minutes. Data available at 6:30 AM.
        The team saved ~$800/month in EMR cluster idle time.
```

---

**Q2: Describe a time you improved data quality in a pipeline.**

```
Situation: Our sales dashboard was showing revenue numbers 8% higher than
           what the finance team was reporting. This was causing weekly arguments
           between Sales and Finance.

Task: I was asked to investigate and align both numbers.

Action: I traced the lineage from the raw source tables to the final dashboard.
        Found the issue: our pipeline was double-counting orders that were
        split into multiple shipments. The sales_id was duplicated in the raw table
        with different shipment_ids, and we were summing without deduplication.

        I added a deduplication step using window functions:
        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY created_at ASC) = 1
        to keep only the first record per sale.

        Then I added a dbt test:
        - custom singular test checking that SUM(revenue) in our pipeline
          matches SUM(revenue) from the source within 0.1% tolerance.
        - unique test on sale_id

Result: Revenue discrepancy dropped from 8% to 0.02% (rounding).
        Finance and Sales now use the same dashboard. Test runs daily and alerts
        immediately if the gap exceeds 0.5%.
```

---

**Q3: Tell me about a time you had to learn a new technology quickly.**

```
Situation: Our team was migrating from a legacy Informatica pipeline to Spark on Databricks.
           I had worked with Spark, but had no Databricks-specific knowledge,
           and the migration had a 6-week deadline.

Task: I was responsible for migrating 15 critical pipelines to Databricks.

Action: I spent the first week on Databricks Academy courses and built a small
        proof-of-concept replicating our most complex pipeline in a sandbox.
        I found that Delta Lake's MERGE statement replaced our complex CDC logic
        with about 1/3 of the code.

        I documented a "migration playbook" for each Informatica pattern → Spark equivalent.
        I used this to complete 12 pipelines in weeks 2-5, and paired with a junior
        engineer on the remaining 3 to accelerate their learning simultaneously.

Result: Completed all 15 pipelines in 5.5 weeks (0.5 weeks early).
        The playbook is now used for all new Databricks onboarding.
```

---

### 🤝 Teamwork & Conflict

**Q4: Tell me about a conflict with a stakeholder and how you resolved it.**

```
Situation: A business analyst asked me to add a column to the dashboard that showed
           "yesterday's revenue" but wanted it done by Monday (2 days).
           Technically easy — but the column would require a schema change
           to a table that 7 downstream pipelines depended on.

Task: My job was to deliver the feature without breaking anything.

Action: Instead of just saying "no" or rushing it, I scheduled a 30-minute call.
        I showed the analyst the dependency graph and explained the risk:
        changing the schema without proper testing could break the Finance pipeline
        and delay the month-end close by a day.

        I proposed two options:
        Option A: 2 days — add the column to only the dashboard query (no schema change)
                  but no historical data, just from today forward.
        Option B: 1 week — proper schema change, all downstream pipelines tested,
                  full historical data available.

        I let them choose. They chose Option A for the immediate need,
        with Option B scheduled for the next sprint.

Result: Dashboard was updated Monday. No pipelines broke.
        The analyst said they appreciated being shown the trade-offs rather than
        just being told it was complicated.
```

---

**Q5: Describe a time you disagreed with your team's technical decision.**

```
Situation: My team was planning to use Spark with a very large number of small CSV files
           as the data format for our new data lake, because "everyone knows CSV."

Task: I believed this was the wrong choice and needed to advocate for Parquet without
      creating friction.

Action: Instead of saying "CSV is wrong," I ran a benchmark on our actual data.
        I processed the same dataset (500GB) using CSV vs Parquet and measured:
        - Query time: CSV 4.2 min vs Parquet 28 sec
        - Storage: CSV 500GB vs Parquet 85GB (snappy compressed)
        - Schema handling: CSV needed manual casting; Parquet had schema embedded

        I shared these numbers in our design review with a simple slide.
        I acknowledged CSV is familiar and is fine for small data, but at our scale,
        Parquet would save 83% storage cost and 11x query time.

Result: Team voted unanimously to use Parquet. Decision took 15 minutes.
        The benchmark slide became part of our data engineering onboarding.
```

---

### 📅 Deadlines & Pressure

**Q6: Tell me about a time you worked under significant pressure or a tight deadline.**

```
Situation: At [Company], our data pipeline went down at 11 PM on a Sunday before
           the Monday morning board presentation. The CEO needed revenue numbers
           by 9 AM Monday.

Task: I was on-call. I had to diagnose and fix the pipeline in under 8 hours.

Action: I first identified the failure point using Airflow logs and Spark UI.
        A schema change in the source database had broken our ingestion job
        (a new column was added with a non-null constraint that our schema didn't expect).

        I applied a targeted fix: add `mode="PERMISSIVE"` to handle the schema mismatch,
        re-ran the failed jobs, and monitored through completion.

        Then I wrote a post-mortem explaining the root cause and proposed a fix:
        adding schema drift detection (Great Expectations) that would alert
        before a schema change reaches the pipeline.

Result: Pipeline completed at 4:30 AM. Dashboard ready by 7 AM.
        Board presentation went ahead. Schema drift alerts were implemented the next week.
        We've had zero schema-break incidents in the 8 months since.
```

---

**Q7: Tell me about a time you had to prioritise multiple competing projects.**

```
Situation: I had three simultaneous requests: (1) urgent production bug fix,
           (2) new feature for Sales reporting (promised for Friday),
           (3) a long-running technical debt item my manager wanted this week.

Task: I had to make a clear prioritisation call and communicate it.

Action: I assessed impact and urgency:
        (1) Production bug = revenue impact → immediate, top priority
        (2) Sales feature = committed deliverable, stakeholder expectation
        (3) Tech debt = important but no external commitment

        I communicated clearly: fixed the production bug first (took 3 hours).
        Then emailed my manager explaining the tech debt would slip by 1 week.
        I delivered the Sales feature on Friday as promised.

Result: Bug fixed same day. Sales feature on time. Manager appreciated the
        proactive communication on the tech debt slip rather than finding out Friday.
```

---

### 🎯 Leadership & Ownership

**Q8: Describe a time you took ownership of something outside your role.**

```
Situation: Our team had no documentation for our data pipelines.
           Every time a new engineer joined, senior engineers spent 3-4 days
           explaining the architecture. This was also a risk — if a key person left,
           tribal knowledge would be lost.

Task: This wasn't in my OKRs, but I saw it as a systemic problem.

Action: I started a "Data Engineering Runbook" — a wiki with:
        - Architecture diagram for each pipeline
        - Common failure modes and how to fix them
        - Dependency map (which tables feed which)
        - Contact for each pipeline (who owns what)

        I spent ~2 hours per week on this for 6 weeks. I also made it a PR
        requirement: every code PR must update the runbook if it changes architecture.

Result: New engineer onboarding time dropped from 4 days to 1.5 days.
        During my vacation, a critical pipeline failed and a junior engineer fixed it
        solo in 2 hours using the runbook — something that would have required
        escalating to a senior previously.
```

---

### 💡 Ambiguity & Initiative

**Q9: Tell me about a time you had to work with unclear or incomplete requirements.**

```
Situation: I was asked to "build a report for the marketing team." No further specification.
           The timeline was 2 weeks.

Task: My job was to deliver something useful, not to wait for perfect requirements.

Action: Instead of asking for a 20-page requirements doc, I scheduled a 1-hour session
        with the marketing lead and asked three questions:
        1. What decision will this report help you make?
        2. If you could see ONE number to make that decision, what would it be?
        3. How often do you need this refreshed?

        From those answers: they needed campaign ROI by channel, updated weekly.
        I built a prototype in 3 days using existing data, shared it, got feedback,
        iterated twice in week 2.

Result: Marketing team adopted the report immediately. In 3 months they were using it
        in every weekly sync. Total build time: 9 days including 2 iterations.
        The "requirements-last" approach they'd been stuck on for 2 months was solved in 9 days.
```

---

**Q10: Tell me about a mistake you made and what you learned from it.**

```
Situation: I ran a `git push --force` on our team's main branch thinking I was
           on a feature branch. I overwrote 3 of my teammates' commits at 3 PM Friday.

Task: I needed to fix it immediately and prevent it from happening again.

Action: I immediately checked git reflog, recovered all 3 commits, and force-pushed
        the restored state back. Total downtime: 22 minutes.
        I told the affected teammates immediately and apologized directly.

        Then I proposed two safeguards:
        1. Branch protection on GitHub: disallow force-push to main for everyone
           (even admins must request a bypass)
        2. Team convention: feature branches always named feature/*, never just words
           that could be confused with main/develop.

Result: Both safeguards were implemented. We've had zero force-push incidents since.
        Teammates appreciated the transparency and quick fix.
        Lesson: Communicate mistakes immediately. Fix first, postmortem second.
```

---

## 🏢 Amazon Leadership Principles — Data Engineering Answers

Amazon, Flipkart, Meesho, and many Indian tech companies use LP-based interviews.

| Principle | Question Style | Key Points |
|---|---|---|
| Customer Obsession | "Tell me about a time you put the customer first" | Business impact > technical elegance |
| Ownership | "Tell me about going beyond your role" | Initiative, no "that's not my job" |
| Invent and Simplify | "Tell me about simplifying a process" | Reduced complexity, novel solution |
| Dive Deep | "Tell me about getting into details" | Root cause analysis, metrics |
| Deliver Results | "Tell me about hitting a tough goal" | Measurable outcome, on time |
| Bias for Action | "Tell me about acting with incomplete info" | Speed + calculated risk |
| Have Backbone | "Tell me about disagreeing with leadership" | Data-driven, respectful push back |
| Learn and Be Curious | "Tell me about learning something new" | Self-taught, applied it |

---

## 📋 30 More Questions to Prepare For

### Technical
- How do you handle schema drift in production pipelines?
- Tell me about a time a query/pipeline was unexpectedly slow. How did you fix it?
- Describe your approach to data quality monitoring.
- Tell me about a time you chose simplicity over a technically superior solution.
- How do you decide when to use streaming vs batch?

### Process & Collaboration
- How do you handle disagreements during code review?
- Tell me about a time you had to explain a technical concept to a non-technical stakeholder.
- How do you manage your own workload when the team is understaffed?
- Tell me about a time you mentored or helped a junior team member.
- Describe a time you received critical feedback. How did you respond?

### Problem-Solving
- Tell me about a time you found a critical bug in production. What happened?
- Describe a situation where you had to make a decision with incomplete data.
- Tell me about a time you proactively identified a problem before it became critical.
- How do you balance technical debt against new feature development?
- Tell me about a project that failed. What did you learn?

### Goals & Growth
- Why do you want to leave your current role?
- Where do you see yourself in 3 years?
- What is the most important thing you've learned in the last year?
- What kind of engineering culture do you thrive in?
- What would your current manager say is your biggest area of improvement?

---

## 💡 Key Tips

1. **Quantify everything.** "I improved it" < "I reduced runtime from 6h to 47min."
2. **Use "I" not "we."** Interviewer wants YOUR contribution.
3. **Show reflection.** Especially for mistakes — what did you learn?
4. **Stay positive.** Even on conflict/failure questions, don't badmouth colleagues.
5. **Have 3 levels of depth.** Start high-level. Go deeper only if they ask.
6. **Prepare your "why us" story.** Research the company. Mention specific things.
7. **Ask smart questions.** "What does success look like for this role in 90 days?"
