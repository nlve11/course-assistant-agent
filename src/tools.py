import os, glob
NOTE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "note")

def search_notes(query: str, top_k: int = 3) -> dict:
    if not query or not query.strip():
        return {"status": "validation_error", "error": "query is empty"}
    if not os.path.isdir(NOTE_DIR):
        return {"status": "knowledge_base_missing", "error": "data/note directory not found"}
    top_k = max(1, min(top_k, 5))
    q = query.lower()
    results = []
    for fpath in sorted(glob.glob(os.path.join(NOTE_DIR, "*.txt"))):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        title = os.path.splitext(os.path.basename(fpath))[0]
        if q in content.lower() or q in title.lower():
            snippet = content[:300].replace("\n", " ")
            results.append({"title": title, "snippet": snippet, "source": fpath})
    return {"status": "ok", "items": results[:top_k], "total": len(results)}

def evaluate_answer(question: str, answer: str, rubric: str = "") -> dict:
    if not answer or not answer.strip():
        return {"status": "validation_error", "error": "answer is empty"}
    score = 0; feedback = []
    if len(answer) >= 10: score += 2
    else: feedback.append("Too short")
    if rubric and rubric.lower() in answer.lower():
        score += 3; feedback.append("Covers rubric")
    else: feedback.append("No rubric coverage")
    if "." in answer: score += 2; feedback.append("Complete sentences")
    if any(kw in answer.lower() for kw in ["because","example","therefore"]):
        score += 3; feedback.append("Has reasoning")
    return {"status":"ok","score":min(score,10),"feedback":feedback,"max_score":10}

def code_check(code: str, language: str = "python") -> dict:
    if not code or not code.strip():
        return {"status":"validation_error","error":"code is empty"}
    issues = []
    if language == "python":
        if "import " not in code and "def " not in code:
            issues.append("No imports or function defs")
        if code.count("(") != code.count(")"):
            issues.append("Unmatched parentheses")
        if len(code.split("\n")) > 50:
            issues.append("Code exceeds 50 lines")
    return {"status":"ok","issues":issues,"issue_count":len(issues),"line_count":len(code.split("\n"))}
