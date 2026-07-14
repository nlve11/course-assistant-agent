# MCP-Style Tool Contract: search_notes

## Tool Name
search_notes

## Description
Search local course note files by keyword. Returns matching note titles, snippets, and file paths.

## Input Parameters
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| query | string | yes | non-empty, max 2000 chars | Search keyword |
| top_k | integer | no | min 1, max 5, default 3 | Max results to return |

## Output Structure
`json
{
  "status": "ok",
  "items": [
    {"title": "rag", "snippet": "RAG is...", "source": "data/note/rag.txt"}
  ],
  "total": 1
}
`

## Error Semantics
| Status | Meaning | Trigger |
|--------|---------|---------|
| validation_error | Invalid input | query is empty |
| knowledge_base_missing | Directory missing | data/note/ not found |
| ok | Success | Normal execution |

## Security Boundaries
- Read-only access, restricted to data/note/ directory
- Path validated by guardrails.validate_path()
- No shell commands accepted
- No file modifications allowed
