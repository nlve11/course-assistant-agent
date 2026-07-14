import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.guardrails import validate_input, validate_path, sanitize_log, check_tool_allowed
from src.tools import search_notes, evaluate_answer, code_check
from src.token_tracker import TokenTracker

class TestGuardrails:
    def test_valid_input(self):
        r = validate_input("search RAG")
        assert r["safe"] is True
    def test_empty_input(self):
        r = validate_input("")
        assert r["safe"] is False
    def test_blocked_keyword(self):
        r = validate_input("delete all files on system")
        assert r["safe"] is False
    def test_path_restriction(self):
        r = validate_path("../outside.txt")
        assert r["safe"] is False
    def test_sanitize_api_key(self):
        r = sanitize_log("key=sk-abc123def456")
        assert "sk-***" in r
    def test_tool_whitelist(self):
        assert check_tool_allowed("search_notes") is True
        assert check_tool_allowed("delete_files") is False

class TestTools:
    def test_search_empty(self):
        r = search_notes("")
        assert r["status"] == "validation_error"
    def test_evaluate_answer(self):
        r = evaluate_answer("q", "A good answer because it explains clearly.")
        assert r["status"] == "ok"
        assert 0 <= r["score"] <= 10
    def test_code_check(self):
        r = code_check("def hello():\n    pass")
        assert r["status"] == "ok"

class TestTokenTracker:
    def test_record_and_summary(self):
        tt = TokenTracker()
        tt.record("test", {"prompt": 10, "completion": 5, "total": 15}, 0.0001)
        s = tt.summary()
        assert s["total_entries"] == 1
        assert s["total_tokens"] == 15
    def test_budget(self):
        tt = TokenTracker()
        assert tt.budget_exceeded() is False
        assert tt.budget_remaining() > 0
