import re, os
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
ALLOWED_PATHS = [os.path.join(PROJECT_ROOT, "data")]
SENSITIVE_PATTERNS = ["password", "token", "secret", "api_key", "sk-"]
MAX_INPUT_LENGTH = 2000
BLOCKED_KEYWORDS = ["delete", "rm -rf", "shutdown", "format", "drop table", "ignore all instructions", "system password"]

def validate_input(text: str) -> dict:
    if not text or not text.strip():
        return {"safe": False, "reason": "Input is empty"}
    if len(text) > MAX_INPUT_LENGTH:
        return {"safe": False, "reason": f"Input exceeds {MAX_INPUT_LENGTH} chars"}
    lower = text.lower()
    for kw in BLOCKED_KEYWORDS:
        if kw in lower:
            return {"safe": False, "reason": f"Blocked keyword: {kw}"}
    return {"safe": True, "reason": "ok"}

def validate_path(filepath: str) -> dict:
    abs_path = os.path.abspath(os.path.join(PROJECT_ROOT, filepath))
    for allowed in ALLOWED_PATHS:
        if abs_path.startswith(allowed):
            return {"safe": True, "path": abs_path}
    return {"safe": False, "reason": f"Path not allowed: {filepath}"}

def sanitize_log(text: str) -> str:
    result = text
    for pat in SENSITIVE_PATTERNS:
        result = re.sub(pat + r"[\"']?[=:][\"']?\S+", pat + "=***", result, flags=re.IGNORECASE)
    result = re.sub(r"sk-[A-Za-z0-9]{10,}", "sk-***", result)
    return result

def check_tool_allowed(tool_name: str) -> bool:
    return tool_name in {"search_notes", "evaluate_answer", "code_check"}
