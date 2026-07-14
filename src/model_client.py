import os, time, logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class ModelClient:
    """Real LLM client via OpenAI-compatible API. Reads .env for config."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        self.model = os.getenv("MODEL_NAME", "deepseek-chat-flash")
        self.max_cost = float(os.getenv("MAX_COST_YUAN", "1.0"))
        self.total_cost = 0.0
        self.client = None
        if self.api_key and self.api_key != "sk-your-key-here":
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def is_ready(self) -> bool:
        return self.client is not None

    def chat(self, messages: list, max_tokens=1024, temperature=0.7) -> dict:
        if not self.client:
            return {"content": "[Model not configured]", "usage": {}, "cost": 0.0, "elapsed": 0.0}
        start = time.perf_counter()
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages,
            max_tokens=max_tokens, temperature=temperature)
        elapsed = time.perf_counter() - start
        content = resp.choices[0].message.content
        u = resp.usage
        usage = {"prompt": u.prompt_tokens, "completion": u.completion_tokens,
                 "total": u.total_tokens} if u else {}
        cost = usage.get("total", 0) * 0.00000015  # ~$0.15/1M tokens
        self.total_cost += cost
        logger.info("LLM call: model=%s tokens=%d cost=%.6f elapsed=%.2fs",
                     self.model, usage.get("total"), cost, elapsed)
        return {"content": content, "usage": usage, "cost": cost, "elapsed": elapsed}

    def check_model(self) -> dict:
        if not self.client:
            return {"status": "not_configured", "model": self.model}
        try:
            r = self.chat([{"role": "user", "content": "OK"}], max_tokens=5)
            return {"status": "ok", "model": self.model,
                    "tokens": r["usage"], "cost": r["cost"], "elapsed": r["elapsed"]}
        except Exception as e:
            return {"status": "error", "model": self.model, "message": str(e)}
