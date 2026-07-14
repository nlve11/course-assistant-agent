#!/usr/bin/env python3
"""Course Assistant Agent - Entry point"""
import sys, json, logging
from src.model_client import ModelClient
from src.token_tracker import TokenTracker
from src.workflow import Workflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

def cmd_check_model():
    mc = ModelClient()
    result = mc.check_model()
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_run_agent(goal: str):
    mc = ModelClient()
    tt = TokenTracker()
    wf = Workflow(mc, tt)
    result = wf.run(goal)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    if "--check-model" in sys.argv:
        cmd_check_model()
    elif "--goal" in sys.argv:
        idx = sys.argv.index("--goal")
        goal = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        cmd_run_agent(goal)
    else:
        print("Usage:")
        print("  python main.py --check-model")
        print('  python main.py --goal "your question here"')
        sys.exit(1)
