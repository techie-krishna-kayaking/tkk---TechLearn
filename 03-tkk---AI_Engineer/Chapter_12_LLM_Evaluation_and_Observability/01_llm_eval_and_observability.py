# ============================================================
# CHAPTER 12: LLM EVALUATION & OBSERVABILITY (LLMOps)
# Practice in: VS Code (runnable eval harness — no API keys)
# "How do you know your LLM app is GOOD, and not silently
# regressing?" is the question that separates people who build
# demos from people who ship. This is a top senior differentiator.
# ============================================================

import re
import math
from dataclasses import dataclass, field
from collections import defaultdict

# ============================================================
# SECTION 1: WHY LLM EVAL IS HARD (say this)
# ------------------------------------------------------------
# Outputs are open-ended, non-deterministic, and correctness is
# often subjective. You can't unit-test "is this a good answer"
# with ==. So we build LAYERED eval:
#   1. Deterministic checks (format, schema, contains, regex)
#   2. Reference-based metrics (exact match, F1, BLEU/ROUGE, sim)
#   3. LLM-as-judge (rubric scoring, pairwise preference)
#   4. Task metrics (RAGAS for RAG, tool-accuracy for agents)
#   5. ONLINE eval (A/B, human feedback, guardrail hits)
# ============================================================


# ============================================================
# SECTION 2: AN OFFLINE EVAL HARNESS (runnable)
# ------------------------------------------------------------
# Golden dataset of (input, expected) + a set of scorers.
# This is exactly what you'd run in CI to block regressions.
# ============================================================

@dataclass
class EvalCase:
    input: str
    expected: str
    must_contain: list = field(default_factory=list)

def token_f1(pred, gold):
    """Reference-based overlap metric (like SQuAD F1)."""
    p = re.findall(r"\w+", pred.lower())
    g = re.findall(r"\w+", gold.lower())
    if not p or not g:
        return 0.0
    common = 0
    gp = list(p)
    for tok in set(g):
        common += min(gp.count(tok), g.count(tok))
    if common == 0:
        return 0.0
    precision = common / len(p)
    recall = common / len(g)
    return 2 * precision * recall / (precision + recall)

def contains_check(pred, must_contain):
    return all(term.lower() in pred.lower() for term in must_contain)

# A tiny "system under test" (stub for your LLM app)
def my_llm_app(query):
    responses = {
        "capital of france": "The capital of France is Paris.",
        "2+2": "2 + 2 = 4.",
        "refund window": "Refunds are allowed within 30 days.",
    }
    return responses.get(query, "I don't know.")

GOLDEN = [
    EvalCase("capital of france", "Paris is the capital of France.", ["Paris"]),
    EvalCase("2+2", "The answer is 4.", ["4"]),
    EvalCase("refund window", "You can refund within 30 days.", ["30 days"]),
]

def run_eval(app, dataset):
    rows = []
    for case in dataset:
        pred = app(case.input)
        rows.append({
            "input": case.input,
            "f1": round(token_f1(pred, case.expected), 2),
            "contains": contains_check(pred, case.must_contain),
        })
    avg_f1 = sum(r["f1"] for r in rows) / len(rows)
    pass_rate = sum(r["contains"] for r in rows) / len(rows)
    return rows, avg_f1, pass_rate

print("=== Offline eval harness (golden dataset) ===")
rows, avg_f1, pass_rate = run_eval(my_llm_app, GOLDEN)
for r in rows:
    print(f"  {r['input']:20} f1={r['f1']:.2f}  contains={r['contains']}")
print(f"avg_f1={avg_f1:.2f}  contains_pass_rate={pass_rate:.0%}")
assert pass_rate == 1.0
print("[PASS] all golden cases pass the containment gate\n")


# ============================================================
# SECTION 3: REGRESSION TESTING / CI GATE
# ------------------------------------------------------------
# Every prompt/model/config change must beat the last baseline.
# Gate the deploy on it — same discipline as software tests.
# ============================================================
BASELINE_F1 = 0.30
def ci_gate(app, dataset, baseline):
    _, avg_f1, pass_rate = run_eval(app, dataset)
    ok = avg_f1 >= baseline and pass_rate >= 0.9
    print(f"CI GATE: avg_f1={avg_f1:.2f} vs baseline {baseline} | "
          f"pass_rate={pass_rate:.0%} -> {'GREEN' if ok else 'RED (block deploy)'}")
    return ok
assert ci_gate(my_llm_app, GOLDEN, BASELINE_F1)
print("[PASS] regression gate prevents shipping a worse prompt/model\n")


# ============================================================
# SECTION 4: LLM-AS-JUDGE (rubric + pairwise)
# ------------------------------------------------------------
# When there's no single reference answer, use a STRONG model to
# score outputs against a rubric, or to pick the better of two.
# Best practices interviewers want to hear:
#   - Give a clear RUBRIC + scale (1-5) and require a rationale.
#   - Use PAIRWISE comparison (A vs B) — more reliable than
#     absolute scores.
#   - Mitigate biases: POSITION bias (randomize order), VERBOSITY
#     bias (longer != better), self-preference (judge != generator).
#   - Calibrate the judge against human labels; report agreement.
# Below: a stubbed judge to show the harness (prod = real LLM call).
# ============================================================
def llm_judge(question, answer_a, answer_b):
    """Return 'A' or 'B'. Stub scores by groundedness + brevity."""
    def score(ans):
        grounded = 1.0 if any(w in ans.lower() for w in question.lower().split()) else 0
        brevity = 1.0 / (1 + abs(len(ans.split()) - 12) / 12)  # prefer ~concise
        return grounded + brevity
    return "A" if score(answer_a) >= score(answer_b) else "B"

def pairwise_eval(question, a, b, trials=2):
    """Randomize order across trials to reduce position bias."""
    wins = defaultdict(int)
    orders = [(a, b, "A", "B"), (b, a, "B", "A")]   # swap positions
    for x, y, lx, ly in orders[:trials]:
        winner = llm_judge(question, x, y)
        wins[lx if winner == "A" else ly] += 1
    return dict(wins)

print("=== LLM-as-judge (pairwise, position-debiased) ===")
q = "what is the refund window"
good = "Refunds are allowed within 30 days of purchase."
bad = "Our company has many policies about various things and processes."
result = pairwise_eval(q, good, bad)
print(f"  wins: {result}  -> winner: {'A(good)' if result.get('A',0) >= result.get('B',0) else 'B(bad)'}")
assert result.get("A", 0) >= result.get("B", 0)
print("[PASS] judge prefers the grounded, concise answer across positions\n")


# ============================================================
# SECTION 5: OBSERVABILITY / TRACING (production LLMOps)
# ------------------------------------------------------------
# You must SEE every request: the full trace (prompt, retrieved
# context, tool calls, model output), plus tokens, cost, latency,
# and user feedback. Tools: LangSmith, Langfuse, Arize Phoenix,
# Helicone, W&B Weave. Trace spans nest like distributed tracing.
# ============================================================

# Token-based cost model (USD per 1K tokens) — know how to compute $
PRICES = {  # illustrative
    "gpt-4o":       {"in": 0.0025, "out": 0.010},
    "gpt-4o-mini":  {"in": 0.00015, "out": 0.0006},
    "claude-haiku": {"in": 0.00025, "out": 0.00125},
}

@dataclass
class Trace:
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    def cost_usd(self):
        p = PRICES[self.model]
        return (self.prompt_tokens/1000)*p["in"] + (self.completion_tokens/1000)*p["out"]

traces = [
    Trace("gpt-4o", 1200, 300, 1800),
    Trace("gpt-4o", 800, 150, 1200),
    Trace("gpt-4o-mini", 1500, 400, 600),
]
print("=== Observability: cost + latency rollup ===")
total_cost = sum(t.cost_usd() for t in traces)
p95 = sorted(t.latency_ms for t in traces)[int(0.95 * (len(traces)-1))]
for t in traces:
    print(f"  {t.model:12} ${t.cost_usd():.5f}  {t.latency_ms:.0f}ms")
print(f"TOTAL cost=${total_cost:.5f}  p95_latency={p95:.0f}ms")
# Cost-routing insight: mini is ~10x cheaper — route easy queries to it
cost_4o = Trace("gpt-4o", 1500, 400, 600).cost_usd()
cost_mini = Trace("gpt-4o-mini", 1500, 400, 600).cost_usd()
print(f"Same request: gpt-4o=${cost_4o:.5f} vs mini=${cost_mini:.5f} "
      f"({cost_4o/cost_mini:.0f}x) -> route by difficulty")
assert cost_mini < cost_4o
print("[PASS] tracing enables cost routing + latency SLOs\n")


# ============================================================
# SECTION 6: ONLINE EVALUATION (after you ship)
# ------------------------------------------------------------
# Offline eval is necessary but not sufficient. In production:
#   - A/B test prompt/model variants on real traffic (Ch: stats).
#   - Collect human feedback (thumbs up/down, edits) as labels.
#   - Guardrail-hit rate, refusal rate, tool-error rate (Ch14).
#   - Business metrics: task completion, deflection, CSAT, revenue.
#   - Drift monitors on inputs (new topics) and outputs (quality).
# Close the loop: mine failures -> add to the golden set -> re-eval.
# ============================================================

# ============================================================
# 30-SECOND ANSWER TO 'HOW DO YOU EVALUATE AN LLM APP?':
# ------------------------------------------------------------
# "A layered eval: deterministic + reference metrics + LLM-as-judge
#  (pairwise, debiased) on a versioned golden set, gated in CI so a
#  prompt/model change can't regress. In prod, full tracing (cost,
#  latency, tokens), A/B tests, human feedback, guardrail metrics,
#  and a failure->golden-set feedback loop."
# ============================================================

if __name__ == "__main__":
    print("Chapter 12 complete: LLM eval + observability + cost. ✅")
