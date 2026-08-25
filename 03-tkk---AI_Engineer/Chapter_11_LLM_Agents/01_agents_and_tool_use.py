# ============================================================
# CHAPTER 11: LLM AGENTS & TOOL USE
# Practice in: VS Code (runnable ReAct loop — no API keys)
# "Agentic AI" is the hottest 2025-26 hiring area. Product
# companies want engineers who can build RELIABLE agents, not
# demos. This chapter covers tool calling, ReAct, planning,
# multi-agent, memory, MCP, and — critically — failure modes.
# ============================================================

import re
import json
import math

# ============================================================
# SECTION 1: WHAT IS AN AGENT? (crisp definition)
# ------------------------------------------------------------
# An agent = an LLM in a LOOP with:
#   - TOOLS   (functions it can call to act/observe the world)
#   - MEMORY  (short-term scratchpad + long-term store)
#   - PLANNING(decide next action toward a goal)
#   - a STOP condition
# Chatbot = one turn in, one turn out. Agent = perceive -> decide
# -> act -> observe -> repeat until the goal is met.
# ============================================================


# ============================================================
# SECTION 2: TOOLS / FUNCTION CALLING (the foundation)
# ------------------------------------------------------------
# Modern LLMs emit a STRUCTURED tool call (name + JSON args)
# against a schema you provide. Your runtime executes the tool
# and feeds the result back. Below we define real tools + JSON
# schemas exactly like an OpenAI/Anthropic function-calling spec.
# ============================================================

def calculator(expression: str) -> str:
    """Safely evaluate a basic arithmetic expression."""
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expression):
        return "Error: invalid characters"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"

KNOWLEDGE = {
    "revenue_2024": "Company revenue in 2024 was 500 crore.",
    "employee_count": "The company has 1200 employees.",
}
def knowledge_lookup(key: str) -> str:
    return KNOWLEDGE.get(key, "No entry found.")

TOOLS = {
    "calculator": {
        "fn": calculator,
        "schema": {
            "name": "calculator",
            "description": "Evaluate an arithmetic expression.",
            "parameters": {"type": "object",
                           "properties": {"expression": {"type": "string"}},
                           "required": ["expression"]},
        },
    },
    "knowledge_lookup": {
        "fn": knowledge_lookup,
        "schema": {
            "name": "knowledge_lookup",
            "description": "Look up a fact by key: revenue_2024, employee_count.",
            "parameters": {"type": "object",
                           "properties": {"key": {"type": "string"}},
                           "required": ["key"]},
        },
    },
}


# ============================================================
# SECTION 3: A ReAct AGENT (Reason + Act) — runnable
# ------------------------------------------------------------
# ReAct interleaves THOUGHT -> ACTION -> OBSERVATION until it can
# answer. We simulate the "LLM policy" with a rule-based planner
# so it runs offline; in prod the LLM emits these tool calls.
# The loop, tool dispatch, memory, and stop logic are REAL.
# ============================================================

class ReActAgent:
    def __init__(self, tools, max_steps=6):
        self.tools = tools
        self.max_steps = max_steps
        self.trace = []          # short-term memory / scratchpad

    def _policy(self, goal, observations):
        """Return the next (thought, action). Real system = LLM call."""
        # Multi-hop example: "revenue per employee"
        if "revenue per employee" in goal:
            if "last_result" in observations:          # computation done -> stop
                return ("I have the answer.", ("finish", {}))
            if "revenue_2024" not in observations:
                return ("I need the revenue.",
                        ("knowledge_lookup", {"key": "revenue_2024"}))
            if "employee_count" not in observations:
                return ("I need the employee count.",
                        ("knowledge_lookup", {"key": "employee_count"}))
            # both facts known -> compute
            rev = 500e7            # 500 crore
            emp = 1200
            return ("I can compute now.",
                    ("calculator", {"expression": f"{rev}/{emp}"}))
        return ("I can answer directly.", ("finish", {}))

    def run(self, goal):
        observations = {}
        for step in range(self.max_steps):
            thought, (action, args) = self._policy(goal, observations)
            self.trace.append(("thought", thought))
            if action == "finish":
                break
            # ACT: dispatch the tool
            result = self.tools[action]["fn"](**args)
            self.trace.append(("action", f"{action}({args})"))
            self.trace.append(("observation", result))
            # remember by semantic key
            if action == "knowledge_lookup":
                observations[args["key"]] = result
            else:
                observations["last_result"] = result
        return observations.get("last_result", "no answer")


print("=== ReAct agent: multi-hop 'revenue per employee' ===")
agent = ReActAgent(TOOLS)
answer = agent.run("compute revenue per employee")
for role, content in agent.trace:
    print(f"  {role.upper():12}: {content}")
print(f"  FINAL ANSWER : {float(answer):,.0f} per employee")
assert abs(float(answer) - (500e7 / 1200)) < 1
print("[PASS] agent chained 2 lookups + a calculation to answer\n")


# ============================================================
# SECTION 4: PLANNING PATTERNS (name these)
# ------------------------------------------------------------
# - ReAct        : interleave reason+act each step (default).
# - Plan-and-Execute: make a full plan first, then execute steps
#                   (fewer LLM calls, better for long tasks).
# - Reflexion    : agent critiques its own failed attempt and
#                   retries with the lesson in memory.
# - Tree-of-Thoughts: explore multiple reasoning branches, pick best.
# - Router       : classify the query, dispatch to the right
#                   tool/sub-agent (cheap + reliable).
# ============================================================


# ============================================================
# SECTION 5: MEMORY
# ------------------------------------------------------------
# SHORT-TERM: the scratchpad / message history in the context
#   window (bounded -> summarize or truncate old turns).
# LONG-TERM : persist facts/embeddings in a vector store; retrieve
#   relevant memories per turn (this is RAG applied to memory).
# EPISODIC  : remember past task outcomes to improve future runs.
# Interview point: context windows are finite -> memory management
# (summarize + retrieve) is a core agent design problem.
# ============================================================


# ============================================================
# SECTION 6: MULTI-AGENT ORCHESTRATION
# ------------------------------------------------------------
# Split a hard task across specialized agents:
#   Supervisor/Orchestrator -> {Researcher, Coder, Critic}
# Patterns: supervisor-worker, debate, blackboard.
# Frameworks: LangGraph (stateful graph), CrewAI, AutoGen, OpenAI
#   Swarm. LangGraph models the agent as a GRAPH with nodes
#   (steps) + edges (transitions) + shared state — the current
#   production-favored way to build controllable agents.
# Trade-off: multi-agent adds capability BUT also latency, cost,
#   and new failure modes (agents looping, disagreeing). Start
#   with ONE agent + good tools; add agents only when needed.
# ============================================================

class Supervisor:
    """Route a task to the right worker (a cheap, reliable pattern)."""
    def __init__(self):
        self.workers = {
            "math":   lambda q: calculator(re.sub(r"[^0-9+\-*/(). ]", "", q)),
            "facts":  lambda q: knowledge_lookup("revenue_2024" if "revenue" in q
                                                 else "employee_count"),
        }
    def route(self, query):
        if any(c.isdigit() for c in query) and any(op in query for op in "+-*/"):
            return "math"
        return "facts"
    def handle(self, query):
        w = self.route(query)
        return w, self.workers[w](query)

print("=== Multi-agent supervisor routing ===")
sup = Supervisor()
for q in ["what is 128 * 4", "what was revenue"]:
    worker, out = sup.handle(q)
    print(f"  '{q}' -> [{worker}] -> {out}")
assert sup.handle("what is 128 * 4")[1] == "512"
print("[PASS] supervisor dispatched each query to the right worker\n")


# ============================================================
# SECTION 7: MCP (Model Context Protocol) — the 2025 standard
# ------------------------------------------------------------
# MCP (Anthropic, now broadly adopted) is an OPEN protocol that
# standardizes how agents connect to tools/data sources. Instead
# of bespoke integrations per app, a tool exposes an MCP SERVER;
# any MCP-compatible CLIENT (Claude, IDEs, agents) can use it.
# Primitives: TOOLS (actions), RESOURCES (data), PROMPTS (templates).
# Why it matters: "USB-C for AI tools" — write a tool once, use it
# everywhere; decouples agents from integrations. Mention MCP when
# asked how you'd scale tool integrations across many agents.
# ============================================================


# ============================================================
# SECTION 8: AGENT FAILURE MODES + EVALUATION (senior signal)
# ------------------------------------------------------------
# Failure modes to volunteer:
#   - Infinite loops / not terminating  -> max steps + loop detection
#   - Tool errors / bad args            -> validate args, retries, fallbacks
#   - Hallucinated tool calls           -> strict schemas + validation
#   - Context overflow                  -> summarize/trim memory
#   - Cascading errors in multi-agent   -> a Critic/verifier step
#   - Cost/latency blowups              -> step budgets, cheaper models for routing
#   - Prompt injection via tool output  -> treat tool output as untrusted (Ch14)
# Evaluation: task success rate, steps-to-completion, tool-call
#   accuracy, cost per task, and TRAJECTORY eval (was each step
#   sensible?) — not just final-answer correctness.
# ============================================================

def guarded_run(agent, goal, hard_step_cap=10):
    """Wrap an agent with a loop guard + step budget (reliability)."""
    seen_actions = []
    agent.max_steps = min(agent.max_steps, hard_step_cap)
    result = agent.run(goal)
    # loop detection: same action repeated 3x in a row = abort
    actions = [c for r, c in agent.trace if r == "action"]
    for i in range(len(actions) - 2):
        if actions[i] == actions[i + 1] == actions[i + 2]:
            return "ABORTED: loop detected"
    return result

print("=== Agent reliability guard ===")
guarded = guarded_run(ReActAgent(TOOLS), "compute revenue per employee")
print(f"  guarded result: {float(guarded):,.0f} per employee (with loop/step guards)")
print("[PASS] production agents need step budgets + loop detection\n")

# ============================================================
# 30-SECOND ANSWER TO 'BUILD A RELIABLE AGENT':
# ------------------------------------------------------------
# "Start with ONE agent: strict tool schemas + function calling,
#  a ReAct loop with a STEP BUDGET and loop detection, memory via
#  summarize+retrieve, and a Critic/verifier step. Expose tools
#  over MCP for reuse. Treat tool output as untrusted. Evaluate on
#  task success rate, tool-call accuracy, and cost per task — add
#  multi-agent only when a single agent provably can't cope."
# ============================================================

if __name__ == "__main__":
    print("Chapter 11 complete: agents, tools, MCP, and reliability. ✅")
