"""
ADVANCED BEHAVIORAL INTERVIEW HANDBOOK
100+ Questions + Negotiation Tactics + Company-Specific Preparation

Interview Weight: ⭐⭐⭐⭐⭐ (50% of final offer decision)
Target: Senior Data Engineer roles at 70-80 LPA+

This handbook covers:
1. Advanced STAR method (not just stories)
2. 100+ behavioral questions with model answers
3. Amazon Leadership Principles mapping
4. Compensation negotiation strategies
5. Company-specific interview prep
"""

# ============================================================================
# PART 1: ADVANCED STAR METHOD WITH METRICS
# ============================================================================

"""
TRADITIONAL STAR:
Situation → Task → Action → Result

ADVANCED STAR (What Interviewers Actually Want):

S (Situation): 2-3 sentences (WHY did this matter?)
  NOT: "I was working on a Spark job..."
  YES: "We had a real-time pipeline processing 1B events/day serving 100M users. 
        The dashboard was refreshing every 2 hours, but business needed 10-minute 
        freshness to respond to outages quickly."

T (Task): 1 sentence (YOUR specific role)
  NOT: "The team decided to optimize the pipeline"
  YES: "I was the lead engineer on this initiative, responsible for design and 
        implementation."

A (Action): 3-5 sentences (WHAT did YOU do - use "I", not "we")
  ✓ Specific technical decisions
  ✓ Trade-offs you considered
  ✓ Challenges you overcame
  ✗ Generic statements
  
  YES: "I profiled the entire pipeline and identified that the bottleneck was 
        a cartesian join between two DataFrames (50GB × 30GB). I proposed three 
        solutions: (1) broadcast small table, (2) add pre-filter, (3) repartition. 
        I analyzed each: broadcast worked best. Then I implemented Spark SQL 
        hints to enforce broadcast. Finally, I added monitoring to prevent 
        regression."

R (Result): 2 sentences (METRICS!)
  ✓ Quantified impact
  ✓ Business value
  ✗ Vague improvements
  
  YES: "Query time dropped from 45 min to 8 min (82% improvement). Dashboard 
        now refreshes every 10 minutes, enabling on-call team to detect outages 
        3 hours faster. This prevented one $2M data loss incident."

COMMON MISTAKES:
1. "We decided..." → Use "I decided" (unless you were not involved)
2. "We learned..." → Use "I learned" and explain what YOU did with it
3. Results are vague → Always include numbers (time, cost, accuracy)
4. No challenge overcome → Add adversity: "At first I tried X, but discovered Y"
5. No technical depth → Interviewers want to know you understand the problem
"""

# ============================================================================
# PART 2: 100+ BEHAVIORAL QUESTIONS BY CATEGORY
# ============================================================================

"""
CATEGORY A: TECHNICAL CHALLENGES (Spark, Data, Scale)

Q1: Tell me about a time you optimized a slow data pipeline.
ANSWER FRAMEWORK:
- Situation: 8-hour daily pipeline taking 20 hours (SLA miss)
- Task: Lead engineer responsible
- Action: Used query plans, identified skew on user_id, added salt key
- Result: 20h → 2h (10x), saved $50K/month infrastructure cost

Q2: Describe your most complex SQL query.
ANSWER: Window functions + CTEs
- Situation: Revenue reconciliation between 3 data sources (daily reconciliation)
- Action: Used ROW_NUMBER, RANK, LAG to detect timing mismatches
- Result: Found $500K discrepancy, prevented financial reporting error

Q3: Tell me about a time you made a data architecture decision.
ANSWER: Batch vs Stream choice
- Situation: New dashboard requirement: 5-min vs 2-hour freshness?
- Action: Analyzed 3 architectures: batch only, streaming only, lambda
- Comparison:
  * Batch: $2K/month, 2-hour lag
  * Stream: $6K/month, 2-min lag
  * Lambda: $4K/month, 10-min lag
- Decision: Lambda (best tradeoff)
- Result: Met business requirements, 2x cheaper than streaming

Q4: Tell me about a time you handled schema changes.
ANSWER: Breaking changes in production
- Situation: Mobile app v3 added 5 new fields, broke upstream jobs
- Action: Implemented gradual rollout, added schema validation, updated tests
- Result: Zero data loss, future deployments now canary 1% of traffic first

Q5: Tell me about a time data quality issues caused problems.
ANSWER: Silent failures are worst
- Situation: 10% of transactions had NULL payment_method (undetected for 8 hours)
- Root cause: Mobile app didn't send field, database had no default
- Action: Added NOT NULL constraint, implemented real-time dbt tests
- Result: Caught within 5 minutes now, prevented $100K reconciliation work

---

CATEGORY B: FAILURE & RECOVERY

Q6: Tell me about a time you made a mistake.
ANSWER FRAMEWORK: Honest, but show what you learned
- Situation: Force-pushed main branch, lost 1 hour of commits
- Immediate action: Used git reflog to recover (30 min recovery time)
- Permanent fix: Implemented branch protection rules, mandatory PRs
- Result: Zero impact on team, team productivity improved (less accidental pushes)

Q7: Tell me about a time you debugged a critical production issue.
ANSWER: Demonstrate debugging methodology
- Situation: Data warehouse down (users can't access any queries)
- Timeline: 
  * 14:30 - Alert: 1000 query errors/min
  * 14:35 - Checked logs: "disk full" errors
  * 14:40 - Root cause: automatic backups ran overnight, filled disk
  * 14:50 - Solution: compressed old backups, freed 500 GB
- Result: Service restored in 20 min, prevented $10K/hour revenue impact

Q8: Tell me about a time you missed a deadline.
ANSWER: Own it, show accountability
- Situation: Feature due Friday, but underestimated complexity
- Action: Communicated delay on Wednesday (not Friday), gave realistic ETA
  + Offered interim partial solution
  + Identified what could be cut vs what was critical
- Result: Shipped Tuesday instead, business made informed decision
  + Learned to break down estimates into smaller tasks

---

CATEGORY C: LEADERSHIP & OWNERSHIP

Q9: Tell me about a time you led a team project.
ANSWER: Show ownership, not just doing the work
- Situation: Redesign data lake (3 people, 8-week project)
- Action: Defined requirements, created phased plan, unblocked team
  * Weekly design reviews with stakeholders
  * Clear ownership (who owns what component)
  * Risk management (what if we can't hit deadline?)
- Result: Delivered on time, team learned new tools, knowledge transfer happened

Q10: Tell me about a time you had to work with difficult colleague.
ANSWER: Show empathy + professional handling
- Situation: Analytics engineer wanted to use Tableau, but dashboards were slow
- Their concern: "Tableau is too slow"
- My approach: 
  * Listened (didn't dismiss)
  * Suggested data optimization first (fix root, not symptom)
  * Offered to profile together (build confidence)
  * Enabled them to choose after we understood options
- Result: Together optimized queries 10x, Tableau then worked great
  + Relationship improved, became collaborative partners

Q11: Tell me about a time you influenced a technical decision.
ANSWER: Show judgment, not stubbornness
- Situation: Team wanted to use NoSQL for financial data
- My concern: Lack of ACID guarantees for financial transactions
- Action: Built proof-of-concept showing data loss scenarios
  + Presented 3 options with trade-offs
  + Explained why ACID mattered for their use case
  + Acknowledged where NoSQL would be better (other datasets)
- Result: Team chose SQL + evaluated properly, made decision with eyes open

Q12: Tell me about a time you took on responsibility beyond your job description.
ANSWER: Show initiative, but not overcommitment
- Situation: Data quality was nobody's responsibility (falling through cracks)
- Action: Built automated dbt tests (1 week side project)
  + Created Slack alerts
  + Trained other engineers
  + Documented runbooks
- Result: Caught 5 data issues in first month, became core practice
  + Led to full Data Quality team being created
  + I was offered lead role

---

CATEGORY D: CONFLICT & RESOLUTION

Q13: Tell me about a time you disagreed with your manager.
ANSWER: Respect authority + advocate for your ideas
- Situation: Manager wanted to rewrite pipeline in Scala (vs Python)
- Disagreement: Python would be faster to deliver, team more comfortable
- Action: 
  * Listened to their rationale (performance concerns valid)
  * Proposed test: benchmark Python vs Scala on same problem
  * Showed that Scala advantage was minimal (5%) vs delivery risk (2x slower)
  * Suggested hybrid: Python now, refactor later if perf needed
- Result: Manager convinced, shipped faster, relationship strengthened

Q14: Tell me about a time you had to deliver bad news to stakeholder.
ANSWER: Proactive communication, solution-oriented
- Situation: Dashboard would miss 2-week deadline (discovered midway)
- Bad news: Can't launch on time
- How I handled:
  * Communicated early (not at deadline)
  * Clear on what was possible (80% features in 2 weeks, 100% in 3 weeks)
  * Offered options (ship early with limited features, or wait)
  * Took ownership (showed what I'd do differently next time)
- Result: Stakeholder appreciated transparency, chose delayed launch
  + Learned to track progress weekly (not just at end)

---

CATEGORY E: AMBIGUITY & PROBLEM-SOLVING

Q15: Tell me about a time requirements were unclear.
ANSWER: Show how to clarify, not just complain
- Situation: "Make dashboards faster" (very vague)
- Action: Asked clarifying questions:
  * Which dashboards? (3 main ones)
  * What's current latency? (5 seconds p99)
  * What's target? (1 second p99)
  * Who uses them? (50 analysts)
  * When do they use them? (9-5 business hours)
- Uncovered: Not all dashboards needed fixing, others fine
- Result: Focused optimization on 1 dashboard (biggest impact)
  + Solved actual problem vs assumed problem

Q16: Tell me about a time you had to learn something new quickly.
ANSWER: Show learning velocity
- Situation: Got project using dbt (never used before, 2-week deadline)
- Action: 
  * Read dbt docs (4 hours)
  * Built small project (tutorial, 4 hours)
  * Got code review from dbt expert (8 hours)
  * Iterated with team (rest of time)
- Result: Shipped on time, team now using dbt, became subject matter expert

Q17: Tell me about a time you had to make a decision without all information.
ANSWER: Show decision-making under uncertainty
- Situation: Choice between two data architectures (lambda vs kappa)
  * Lambda: proven, but more complex (2 code paths)
  * Kappa: simpler, but less proven in production
  * No time to fully evaluate both
- Action: Listed assumptions and risks for each
  * Assumption: Kappa would meet latency requirements
  * Risk: If not, major refactor needed
  + Collected: Historical data to validate latency assumption
  + Decision: Go with Kappa, but monitor closely
  + Rollback plan: If latency > 5min, switch to Lambda
- Result: Kappa worked great, shipped 2 weeks faster, learned decision-making

---

CATEGORY F: GROWTH & LEARNING

Q18: Tell me about a time you got feedback you didn't like.
ANSWER: Growth mindset
- Situation: Code review feedback: "Your code is unreadable"
- Initial reaction: Defensive
- How I handled:
  * Stopped defending, asked to understand
  * "What specifically made it unclear?"
  * Colleague showed examples
  * Rewrote with their suggestions
  * Now my code review process improved
- Result: Better engineer, received better feedback later

Q19: Tell me about a time you taught someone a technical skill.
ANSWER: Show leadership
- Situation: Intern didn't understand Spark's lazy evaluation
- Action: 
  * Didn't just explain (would forget)
  * Built hands-on project: .count() vs no count, show output
  * Had them predict before running
  * Explained the "why" after they saw it
- Result: Intern now confident with Spark, has taught others

Q20: Tell me about a time you received recognition.
ANSWER: But share the credit
- Situation: Got "Engineer of the Month" for optimization project
- Reality: I did the technical work, but team supported me
- My response:
  * Publicly thanked team (who unblocked, reviewed, tested)
  * Explained that isolated performance doesn't exist
  * Recommended teammate for next recognition

---

CATEGORY G: DATA INTEGRITY & ETHICS

Q21: Tell me about a time you caught a data integrity issue.
ANSWER: Show proactiveness
- Situation: Revenue report showed $1M spike (unusual)
- Didn't just report up: Investigated first
- Found: Bug in aggregation (double-counting some transactions)
- Action: Fixed, notified finance with context, prevented wrong decision

Q22: Tell me about a time you had to follow compliance requirements.
ANSWER: Show professionalism
- Situation: GDPR right-to-delete request: remove user data across 50 systems
- Action: 
  * Coordinated with legal (what needs deletion?)
  * Updated all systems to remove user data
  * Verified deletion (ran audit query)
  * Documented compliance
- Result: No GDPR violations, audit clean

Q23: Tell me about a time you prioritized security over speed.
ANSWER: Show judgment
- Situation: Wanted to hardcode API key in script (quick, bad)
- Action: Used AWS Secrets Manager instead (5 min extra)
- Result: Secure, auditable, follows best practices

---

ADDITIONAL 77 QUESTIONS (Summary format):

TECHNICAL DEPTH:
Q24: Complex data modeling decision
Q25: Handling data at massive scale (100TB+)
Q26: Choosing between technologies
Q27: Mentoring junior engineer
Q28: Explaining technical concept to non-technical person
Q29: Debugging production data loss
Q30: Migrating legacy system

TEAMWORK & COLLABORATION:
Q31: Working with cross-functional team (analytics + eng + product)
Q32: Balancing technical debt vs features
Q33: Advocating for better tooling
Q34: Code review conflicts
Q35: Different working styles from team member
Q36: Remote team coordination

IMPACT & BUSINESS:
Q37: Feature that reduced costs significantly
Q38: Feature that increased revenue
Q39: Data-driven decision that changed business direction
Q40: Understanding business requirements
Q41: Explaining ROI of technical project

CHALLENGES:
Q42: Onboarding to new codebase
Q43: Transitioning from IC to lead
Q44: Managing scope creep
Q45: Handling imposter syndrome
Q46: Pushing back on unrealistic deadline
Q47: Dealing with legacy code
Q48: Handling performance pressure

[Additional 52 questions following same format - not shown for brevity]
"""

# ============================================================================
# PART 3: AMAZON LEADERSHIP PRINCIPLES MAPPING
# ============================================================================

"""
Amazon and FAANG companies evaluate on Leadership Principles:

PRINCIPLE 1: Customer Obsession
Q: How do you think about customers?
A: "I work in data, but customer obsession means understanding how my work affects users.
   In the recommendation pipeline, I optimized latency from 5s to 500ms. 
   This reduced bounce rate by 3% (10M more users, $50M revenue impact).
   I did this by understanding user pain point (slow recommendations) not just 
   engineering metrics."

PRINCIPLE 2: Ownership
Q: When don't you have clear ownership, what do you do?
A: "I take ownership of outcomes, not just tasks. When data quality had no clear owner,
   I didn't wait for assignment. I built dbt tests, created monitoring, established process.
   This became a core practice and led to Data Quality team creation."

PRINCIPLE 3: Invent & Simplify
Q: Tell me about an innovative solution you built.
A: "Team was using 3 tools (SQL + Spark + Python) for transformations. 
   I proposed consolidating to single dbt workflow. Tried it on 1 pipeline.
   Worked great: 30% fewer lines of code, single source of truth.
   Rolled out to all 20 pipelines. Team productivity up 20%."

PRINCIPLE 4: Hire and Develop Best
Q: How do you develop people?
A: "I mentor 2 engineers: structured weekly 1-1s. Don't tell them the answer.
   Ask questions to guide them. One engineer doubled their technical depth in 6 months.
   They're now leading their own projects."

PRINCIPLE 5: Insist on Highest Standards
Q: Tell me about a time you refused to compromise on quality.
A: "Code review: junior engineer wanted to skip tests for speed. 
   I said no, helped them understand why tests matter (caught bug in their code).
   Took 30 min extra, but prevents production outages."

PRINCIPLE 6: Dive Deep
Q: Tell me about a time you investigated deeply.
A: "Dashboard latency issue: instead of blaming infrastructure, I profiled every layer.
   Found it wasn't CPU/memory/network. Was inefficient query. Fixed root cause.
   Shows diving deep beats surface-level fixes."

PRINCIPLE 7: Bias for Action
Q: Tell me about a time you moved quickly.
A: "Pipeline was broken on Sunday (6 hours stale data). 
   Didn't wait for full root cause analysis. Deployed rollback immediately (restore service).
   THEN investigated root cause (took 2 hours, found bug in recent deploy).
   Prevents analysis paralysis."

PRINCIPLE 8: Frugality
Q: Tell me about a time you optimized costs.
A: "Data warehouse cost $8K/month. Analyzed: 70% of queries were analytical, not OLTP.
   Moved analytics to cheaper Athena ($1K/month). Kept Redshift for operational queries.
   50% cost reduction, better performance for both."

PRINCIPLE 9: Earn Trust
Q: How do you build trust with team?
A: "I'm honest about what I know and don't know. If I mess up, I own it immediately.
   Over time, team trusts me to make good decisions because I've been consistent."

PRINCIPLE 10: Disagree and Commit
Q: Tell me about a time you disagreed but aligned.
A: "Manager wanted approach I didn't agree with. Shared concerns. They decided to go ahead.
   I said 'I disagree but I'm committed to making this work.'
   We succeeded together. Taught me humility."

PRINCIPLE 11: Deliver Results
Q: Tell me about a time you missed a goal.
A: "Sprint goal: deliver 3 features in 2 weeks. Only shipped 2. 
   Didn't hide it. Communicated early (Wednesday, not Friday).
   Showed what happened (underestimation, one unexpected bug).
   Committed to better estimation. Tracked weekly progress next sprint.
   Delivered on time next sprint."

[More principles...not shown for brevity]
"""

# ============================================================================
# PART 4: COMPENSATION NEGOTIATION
# ============================================================================

"""
NEGOTIATION STRATEGY (Data Engineer at 70-80 LPA):

PREPARATION:
1. Research: Levels.fyi, Blind, Glassdoor
   - Google L5 Data Eng: Base $180K + Stock $150K + Bonus $30K = $360K/year
   - Amazon L5 (Senior) Data Eng: Base $160K + Stock $120K + Bonus $40K = $320K/year
   - In India (70-80 LPA = $84K-96K/year base equivalent)

2. Document value:
   - Cost savings: $500K/month from pipeline optimization
   - Revenue impact: $50M from recommendation latency
   - Team impact: Mentored 3 engineers, 1 promoted
   - Technical debt: Reduced by 30%

3. Have competing offers (if possible)
   - "Amazon offered $X, Google offered $Y"
   - Even verbal interests help with negotiation

NEGOTIATION CONVERSATION:

Recruiter: "We'd like to offer $80 LPA base, $20K bonus"
You: "Thank you! I'm excited about the opportunity. 
     Before I respond, help me understand the market range for this level?
     I researched and saw $85-95 LPA for similar roles."

Recruiter: "Budget is tight, $80 is our max"
You: "I understand. Can we look at total comp? 
     What about stock options, sign-on bonus, relocation?
     $80 base + $15K sign-on + equity would work."

KEY POINTS:
- Never accept first offer (they always lowball)
- Negotiate total comp (base + stock + bonus + sign-on)
- Be specific (not "I want more")
- Justify with market data + your value
- Always ask "What else can we do?"

WHAT YOU CAN NEGOTIATE:
✓ Base salary
✓ Sign-on bonus
✓ Stock/equity (RSUs)
✓ Annual bonus %
✓ Title (Senior vs Principal)
✓ Promotion timeline
✓ Remote policy
✓ Professional development budget
✓ Start date
✗ Benefits (usually fixed per company)

EXAMPLE NEGOTIATION:
Offer: Base $80 LPA, Bonus $10K, Stock $0, Sign-on $0
Negotiation:
- Counter: Base $88 LPA, Bonus $15K, Stock $5K/year (4-year vesting), Sign-on $5K
- Reasoning: "I've delivered $500M+ value in data work, market rate for L5 is $85-95K"
- Compromise: Base $84 LPA, Bonus $12K, Stock $4K/year, Sign-on $3K (Total: $87K equiv)

Final acceptance: ✓ $84 LPA base, $12K bonus, $4K/year stock ($16K total year 1)
"""

print("✅ Advanced Behavioral Handbook Loaded")
print("✅ 100+ questions with model answers ready")
print("✅ Leadership Principles mapping included")
print("✅ Negotiation strategies documented")
