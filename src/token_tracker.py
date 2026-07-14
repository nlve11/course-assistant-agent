import json, os, time

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

class TokenTracker:
    """Track token usage and cost per session."""

    def __init__(self):
        self.entries = []
        self.total_prompt = 0
        self.total_completion = 0
        self.total_cost = 0.0

    def record(self, action: str, usage: dict, cost: float):
        entry = {
            "action": action,
            "prompt_tokens": usage.get("prompt", 0),
            "completion_tokens": usage.get("completion", 0),
            "total_tokens": usage.get("total", 0),
            "cost": round(cost, 8),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.entries.append(entry)
        self.total_prompt += entry["prompt_tokens"]
        self.total_completion += entry["completion_tokens"]
        self.total_cost += cost

    def summary(self) -> dict:
        return {
            "total_entries": len(self.entries),
            "total_prompt_tokens": self.total_prompt,
            "total_completion_tokens": self.total_completion,
            "total_tokens": self.total_prompt + self.total_completion,
            "total_cost_yuan": round(self.total_cost * 7.2, 4),  # approximate CNY
            "total_cost_usd": round(self.total_cost, 6),
        }

    def dump_log(self, session_id: str):
        os.makedirs(LOG_DIR, exist_ok=True)
        path = os.path.join(LOG_DIR, f"session_{session_id}.json")
        data = {"session_id": session_id, "entries": self.entries, "summary": self.summary()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def budget_remaining(self) -> float:
        return max(0.0, 1.0 - self.total_cost * 7.2)
    
    def budget_exceeded(self) -> bool:
        return self.total_cost * 7.2 >= 1.0
