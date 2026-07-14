import logging, uuid
from .model_client import ModelClient
from .tools import search_notes, evaluate_answer, code_check
from .guardrails import validate_input, check_tool_allowed, sanitize_log
from .token_tracker import TokenTracker

logger = logging.getLogger(__name__)
TOOL_MAP = {"search_notes": search_notes, "evaluate_answer": evaluate_answer, "code_check": code_check}

class Workflow:
    def __init__(self, model_client: ModelClient, token_tracker: TokenTracker):
        self.model = model_client
        self.tracker = token_tracker

    def run(self, goal: str) -> dict:
        sid = uuid.uuid4().hex[:8]
        steps = []
        guard = validate_input(goal)
        if not guard["safe"]:
            return {"session_id": sid, "status": "rejected", "reason": guard["reason"],
                    "steps": steps, "token_summary": self.tracker.summary()}
        steps.append({"step": "validated", "goal": sanitize_log(goal)})

        gl = goal.lower()
        tools = []
        if any(k in gl for k in ["search", "查找", "搜索", "note", "rag"]):
            tools.append("search_notes")
        if any(k in gl for k in ["eval", "评估", "评价", "评分"]):
            tools.append("evaluate_answer")
        if any(k in gl for k in ["check", "检查", "code", "代码"]):
            tools.append("code_check")
        if not tools: tools = ["search_notes"]
        steps.append({"step": "plan", "tools": tools})

        results = {}
        for tname in tools:
            if not check_tool_allowed(tname):
                steps.append({"step": "blocked", "tool": tname}); continue
            fn = TOOL_MAP.get(tname)
            if not fn: continue
            try:
                if tname == "search_notes": r = fn(goal)
                elif tname == "evaluate_answer": r = fn(goal, f"Answer about: {goal}")
                else: r = fn("def foo(): pass")
                results[tname] = {"status": r.get("status")}
                steps.append({"step": "tool_ok", "tool": tname, "status": r.get("status")})
            except Exception as e:
                results[tname] = {"status": "error"}
                steps.append({"step": "tool_error", "tool": tname, "error": str(e)})

        msgs = [
            {"role": "system", "content": "Summarize tool results for the user."},
            {"role": "user", "content": f"Goal: {goal}\nResults: {results}"},
        ]
        llm = self.model.chat(msgs)
        if llm["usage"]:
            self.tracker.record("response", llm["usage"], llm["cost"])
        steps.append({"step": "responded", "tokens": llm["usage"].get("total", 0)})
        self.tracker.dump_log(sid)
        if self.tracker.budget_exceeded():
            return {"session_id": sid, "status": "budget_exceeded", "steps": steps,
                    "token_summary": self.tracker.summary()}
        return {"session_id": sid, "status": "completed", "answer": llm["content"],
                "steps": steps, "tool_results": results, "token_summary": self.tracker.summary()}
