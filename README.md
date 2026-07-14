# Course Assistant Agent (课程助手智能体)

CLI-based AI agent for course Q&A with RAG, tools, and guardrails.

## Quick Start
\\\
cp .env.example .env
pip install -r requirements.txt
python main.py --check-model
python main.py --goal "search RAG notes"
python -m pytest -q
\\\

## Structure
- src/ - core modules (model_client, tools, guardrails, token_tracker, workflow)
- data/note/ - RAG knowledge base
- prompts/ - agent instructions
- docs/ - MCP tool contract
- tests/ - automated tests (10 test cases)

## Features
- Real LLM via OpenAI-compatible API
- Agent workflow: goal -> plan -> tools -> response
- RAG over local course notes
- Safety guardrails with input validation, path restriction, log sanitization
- Token cost tracking with budget limit
- MCP-style tool contract documentation

## Environments
conda env create -f environment.yml
docker build -t creative-agent-project .
