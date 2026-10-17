"""Lightweight tool-using research agent for retrieval-augmented generation.

Workflow: plan search -> retrieve evidence -> assess coverage -> refine retrieval
when needed -> synthesize an answer grounded in retrieved passages.
"""
import re
from evidora.search import search, tokens
from evidora.ai import answer


def _query_plan(question):
    question = re.sub(r"\s+", " ", question).strip()
    # A concise keyword query helps when the original is phrased as a full question.
    cleaned = re.sub(r"\b(what|which|who|when|where|why|how|does|do|is|are|was|were|the|a|an|for|in|on|of|to|with|and|or)\b", " ", question, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ?.,")
    plan = [question]
    if cleaned and cleaned.lower() != question.lower():
        plan.append(cleaned)
    # Avoid redundant searches while keeping a deterministic, local workflow.
    return list(dict.fromkeys(plan))[:2]


def research_agent(question, use_ai=False):
    """Run a small agent loop using local paper search as its retrieval tool."""
    queries = _query_plan(question)
    steps = [f"Plan: search the uploaded paper library for '{queries[0]}'."]
    gathered, seen = [], set()
    for index, query in enumerate(queries):
        hits = search(query, limit=8)
        steps.append(f"Retrieve: query {index + 1} returned {len(hits)} passage(s).")
        for hit in hits:
            key = (hit["filename"], hit["page_number"], hit["snippet"][:120])
            if key not in seen:
                seen.add(key); gathered.append(hit)
        if len(gathered) >= 5:
            break
    gathered.sort(key=lambda x: x.get("score", 0), reverse=True)
    gathered = gathered[:8]
    if not gathered and len(queries) == 1:
        steps.append("Assess: no evidence found; no unsupported answer will be generated.")
    elif len(gathered) < 3:
        steps.append("Assess: limited evidence found; attempted a refined keyword query when available.")
    else:
        steps.append(f"Assess: {len(gathered)} distinct passages available for grounding.")
    response = answer(question, gathered, use_ai)
    steps.append("Synthesize: produce an evidence-grounded response with source titles and page references.")
    return {"response": response, "results": gathered, "steps": steps}
