# ============================================================
# CHAPTER 16: SENIOR BEHAVIORAL & NEGOTIATION (AI roles)
# Read as: VS Code (Markdown-in-Python) — a preparation workbook.
# At 100-150 LPA, technical skill gets you in the room; behavioral,
# leveling, and negotiation decide your NUMBER. Most lost lakhs
# (and down-leveling) happen HERE, not in the coding round.
# ============================================================
"""
HOW TO USE: fill the templates with YOUR real stories, rehearse
out loud, and time each to 2-3 minutes. Quantify every outcome.
"""

# ============================================================
# SECTION 1: WHAT SENIOR/STAFF AI BEHAVIORAL TESTS
# ------------------------------------------------------------
#   * AMBIGUITY: owned a vague AI problem end-to-end.
#   * IMPACT at scale: shipped a model/system that moved a metric.
#   * JUDGEMENT: chose an approach and can defend the alternative
#     (build vs buy, fine-tune vs RAG, ship vs keep iterating).
#   * INFLUENCE: aligned PMs/leadership/research without authority.
#   * ML MATURITY: handled a model failure / drift / bias incident.
#   * COLLABORATION: worked across research, data, product, infra.
#   * MENTORSHIP: leveled up others; set standards.
# Map each to 1-2 stories BEFORE the loop.
# ============================================================

# ============================================================
# SECTION 2: STAR-L FRAMEWORK (senior upgrade of STAR)
# ------------------------------------------------------------
# S Situation (context + stakes, $/scale) | T Task (what YOU owned)
# A Action (2-3 decisions + WHY, the trade-off you weighed)
# R Result (quantified: latency -40%, +3% engagement, $2M saved)
# L Learning (what you'd change / how it changed you)
# Keep A longest. Interviewers score YOUR decisions, not the team's.
STORY_TEMPLATE = """
COMPETENCY:
S:
T:
A: (decision 1 + why) ... (decision 2 + why) ... (trade-off weighed)
R: (metric moved from X to Y, worth $___ / ___% / ___x)
L:
"""

# ============================================================
# SECTION 3: 8 STORIES EVERY 10-YOE AI ENGINEER NEEDS
# ------------------------------------------------------------
STORY_BANK = """
1. BIGGEST ML IMPACT — a model/system that changed a business metric.
2. AMBIGUOUS PROBLEM — "improve X with ML" from a blank page.
3. ML FAILURE / INCIDENT — model degraded / drifted / biased in prod;
   how you detected, mitigated, and prevented recurrence.
4. HARD TRADE-OFF — fine-tune vs RAG, build vs buy, accuracy vs latency/cost;
   how you decided and what you gave up.
5. INFLUENCED WITHOUT AUTHORITY — changed a PM's/leader's/research direction with data.
6. SHIPPED UNDER CONSTRAINTS — latency/cost/compute budget; how you optimized.
7. DISAGREE & COMMIT — pushed back, then committed once decided.
8. MENTORSHIP / RAISED THE BAR — leveled up juniors, set an eval/quality standard.
"""

# ============================================================
# SECTION 4: WORKED EXAMPLE (model the quantified senior answer)
# ------------------------------------------------------------
WORKED_EXAMPLE = """
COMPETENCY: Impact + hard trade-off (fine-tune vs RAG)

S: Support deflection was stalling; leadership wanted to fine-tune a
   model on 2 years of tickets (a costly, slow bet).
T: As lead AI engineer I owned the approach and the recommendation.
A: I reframed it: the problem was KNOWLEDGE (policies change monthly),
   not BEHAVIOR — so RAG, not fine-tuning. I built a hybrid-retrieval
   RAG with reranking + RAGAS eval, added guardrails for PII and
   injection, and set an offline eval gate in CI. I ran an A/B test
   rather than trusting offline numbers, and chose gpt-4o-mini with
   routing to keep cost sane.
R: Deflection +22%, answer faithfulness 0.94 on the eval set, and
   ~70% lower cost than the fine-tuning plan — shipped in 6 weeks,
   not 6 months.
L: I learned to diagnose knowledge-vs-behavior first; it saved a
   quarter of wasted fine-tuning and made the system maintainable.
"""

# ============================================================
# SECTION 5: AI-SPECIFIC BEHAVIORAL PROBES (prep crisp answers)
# ------------------------------------------------------------
AI_PROBES = """
- "A model you shipped made a harmful/wrong prediction — what did you do?"
  -> Detection (monitoring), containment (rollback/guardrail), root cause,
     prevention (eval + data fix), and the stakeholder comms. Show ownership.
- "How do you keep up with a field that moves weekly?"
  -> Concrete routine: papers (arXiv/Papers with Code), reproducing results,
     a shipped side project, internal reading group.
- "Tell me about a time you were wrong about an ML approach."
  -> Own it fully, show the data that changed your mind, the correction.
- "How do you balance research quality vs shipping?"
  -> Baselines + iteration + eval gates; ship the simplest thing that beats
     the baseline, then improve — with a clear success metric.
- "Responsible AI concern you caught?" -> bias/PII/safety story + the fix.
"""

# ============================================================
# SECTION 6: QUESTIONS YOU ASK THEM (senior candidates interview back)
# ------------------------------------------------------------
ASK_THEM = """
* "How do you measure success for AI here — offline metrics, A/B, or business KPIs?"
* "What's the split between research, applied ML, and infra for this role?"
* "How mature is your eval + observability + guardrail stack?"
* "How are model/prompt changes shipped and rolled back?"
* "What's the biggest unsolved AI problem you'd want me to own in 6 months?"
Great questions signal you operate at their level and evaluate fit.
"""

# ============================================================
# SECTION 7: COMPENSATION NEGOTIATION (this section IS the money)
# ------------------------------------------------------------
NEGOTIATION = """
The best technical prep is wasted if you under-negotiate. For AI roles
at product companies / labs, TOTAL COMP is dominated by EQUITY — that's
where 100 becomes 150.

1. NEVER give the first number. Anchor on LEVEL, not current salary:
   "I'm targeting a market-competitive package for a senior/staff AI
   engineer; what's the band for this level?"
2. GET LEVELED RIGHT FIRST — comp follows level. A level bump (Senior->
   Staff) is worth more than any base haggling. Interview at the highest
   level you can defend; push back on down-leveling with evidence.
3. TOTAL COMP, not base: base + bonus + EQUITY (RSUs/options) + sign-on.
   At top companies/labs equity is 40-60%+ of the number. Understand
   vesting (4-yr, cliff), refreshers, and (for startups) strike price,
   dilution, preference, and the 409A vs preferred price.
4. LEVERAGE = ALTERNATIVES. Run processes in parallel; a competing offer
   is the single strongest lever. Use levels.fyi / market data.
5. Don't accept on the call. "I'm excited — let me review the full
   package and revert." Then ONE reasoned counter, justified by VALUE +
   market + competing offers, not personal need.
6. Negotiate the WHOLE package: if base is capped, push equity, sign-on,
   level, an early (6-mo) review, or start date. Everything is a lever.
7. For startups vs big-tech: weigh cash vs upside, stage/runway, and the
   realistic value of equity — model a few outcome scenarios.

MINDSET: by the offer stage they've DECIDED they want you. Asking
professionally does not rescind offers. A calm counter + silence are
your strongest tools. This one conversation is often worth 20-40 LPA —
prepare for it like a technical round.
"""

# ============================================================
# SECTION 8: 48-HOUR PRE-LOOP CHECKLIST
# ------------------------------------------------------------
CHECKLIST = """
[ ] 8 STAR-L stories written + rehearsed, each < 3 min, quantified.
[ ] One ML-failure and one hard-trade-off story you can tell without flinching.
[ ] Researched their AI products, recent papers/blog posts, and stack.
[ ] Can whiteboard: RAG system, LLM serving to an SLA, an eval strategy.
[ ] Level + target total-comp range decided, with market data + a competing process.
[ ] 5 sharp questions per interviewer; a crisp 2-min background arc.
"""

if __name__ == "__main__":
    for name, text in [("STORY TEMPLATE", STORY_TEMPLATE),
                       ("8 CORE STORIES", STORY_BANK),
                       ("WORKED EXAMPLE", WORKED_EXAMPLE),
                       ("AI BEHAVIORAL PROBES", AI_PROBES),
                       ("QUESTIONS TO ASK THEM", ASK_THEM),
                       ("NEGOTIATION", NEGOTIATION),
                       ("48-HOUR CHECKLIST", CHECKLIST)]:
        print(f"\n{'='*60}\n{name}\n{'='*60}{text}")
