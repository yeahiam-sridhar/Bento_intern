"""BentoLabs AI proof-of-work concept demo.

Local-only FastAPI demo seeded with synthetic agent-review data.
It does not connect to BentoLabs systems, customer data, LLM APIs, or production agents.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
app = FastAPI(
    title="Change Review Workbench - proof of work",
    version="0.1.0",
    description="An independent, local-only concept using synthetic data. Not affiliated with or connected to BentoLabs production systems.",
)
app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")

# Intentionally synthetic demo fixtures. All numbers below are illustrative.
REVIEWS = [
    {
        "id": "REV-0248",
        "title": "Repository context guard",
        "agent": "Codebase Navigator",
        "artifact": "skill · repository-inspector",
        "change": "Add a safe fallback when repository context is absent",
        "status": "Ready to evaluate",
        "severity": "High",
        "signal": "Tool selection drifts when project context is empty",
        "observed": "The agent selects a generic search tool after a missing project_id field.",
        "hypothesis": "A validated context guard could route the run to a clarification step instead of a broad search.",
        "affected": 28,
        "traces": 1842,
        "owner": "S. Patel",
        "updated": "11 min ago",
        "baseline": {"pass": 47, "total": 52, "latency": 4.8, "cost": 0.084},
        "candidate": {"pass": 49, "total": 52, "latency": 4.6, "cost": 0.081},
        "critical_regressions": 0,
        "evidence": [
            {"label": "Failure signature", "value": "project_id missing → broad tool search", "kind": "warn"},
            {"label": "Trace sample", "value": "trace_demo_8f31 · span 04 · tool_router", "kind": "neutral"},
            {"label": "Observed cohort", "value": "28 matching synthetic cases across 1,842 sample traces", "kind": "neutral"},
        ],
        "diff": [
            {"kind": "remove", "text": "project = context['project_id']"},
            {"kind": "add", "text": "project = context.get('project_id')"},
            {"kind": "add", "text": "if not project: return request_clarification()"},
        ],
        "checks": ["No critical fixture regression", "Candidate pass rate >= baseline", "Failure cohort is represented in evaluation fixtures", "Rollback target is recorded"],
    },
    {
        "id": "REV-0247",
        "title": "Timeout recovery policy",
        "agent": "Research Assistant",
        "artifact": "tool · web_fetch",
        "change": "Bound retries and preserve the original error context",
        "status": "Needs review",
        "severity": "Medium",
        "signal": "Retry loop repeats after upstream timeout",
        "observed": "Several runs repeat the same request without retaining timeout metadata.",
        "hypothesis": "A bounded retry policy with jitter and trace-linked error context could reduce loops.",
        "affected": 17,
        "traces": 963,
        "owner": "A. Rao",
        "updated": "38 min ago",
        "baseline": {"pass": 43, "total": 50, "latency": 6.2, "cost": 0.112},
        "candidate": {"pass": 44, "total": 50, "latency": 5.8, "cost": 0.109},
        "critical_regressions": 1,
        "evidence": [
            {"label": "Failure signature", "value": "timeout → same request repeated", "kind": "warn"},
            {"label": "Trace sample", "value": "trace_demo_2a17 · span 08 · web_fetch", "kind": "neutral"},
            {"label": "Observed cohort", "value": "17 matching synthetic cases across 963 sample traces", "kind": "neutral"},
        ],
        "diff": [
            {"kind": "remove", "text": "retry while request_failed: fetch(url)"},
            {"kind": "add", "text": "for attempt in range(MAX_RETRIES):"},
            {"kind": "add", "text": "attach_original_error_context(result)"},
        ],
        "checks": ["No critical fixture regression", "Candidate pass rate >= baseline", "Failure cohort is represented in evaluation fixtures", "Rollback target is recorded"],
    },
    {
        "id": "REV-0246",
        "title": "Tool contract validation",
        "agent": "Data Operations Agent",
        "artifact": "tool schema · write_record",
        "change": "Validate required fields before tool execution",
        "status": "Validated",
        "severity": "Low",
        "signal": "Invalid payload reaches downstream tool",
        "observed": "A required field is omitted in a small sample of tool calls.",
        "hypothesis": "Schema validation before dispatch should surface a clear corrective action.",
        "affected": 9,
        "traces": 721,
        "owner": "K. Nair",
        "updated": "2 hr ago",
        "baseline": {"pass": 46, "total": 50, "latency": 3.9, "cost": 0.071},
        "candidate": {"pass": 48, "total": 50, "latency": 4.0, "cost": 0.072},
        "critical_regressions": 0,
        "evidence": [
            {"label": "Failure signature", "value": "required field missing before write_record", "kind": "warn"},
            {"label": "Trace sample", "value": "trace_demo_0d4e · span 02 · write_record", "kind": "neutral"},
            {"label": "Observed cohort", "value": "9 matching synthetic cases across 721 sample traces", "kind": "neutral"},
        ],
        "diff": [
            {"kind": "add", "text": "payload = validate_payload(payload, schema)"},
            {"kind": "add", "text": "if invalid: return actionable_error(payload)"},
        ],
        "checks": ["No critical fixture regression", "Candidate pass rate >= baseline", "Failure cohort is represented in evaluation fixtures", "Rollback target is recorded"],
    },
]

STATES: dict[str, dict] = {r["id"]: {"decision": "", "evaluation": None} for r in REVIEWS}
AUDIT: list[dict] = []


class DecisionRequest(BaseModel):
    decision: Literal["promote", "request_changes", "dismiss"]
    note: str = Field(default="", max_length=500)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def percent(pass_count: int, total: int) -> float:
    return round(pass_count / total * 100, 1) if total else 0.0


def public_review(review: dict) -> dict:
    state = STATES[review["id"]]
    return {
        "id": review["id"], "title": review["title"], "agent": review["agent"],
        "artifact": review["artifact"], "change": review["change"],
        "status": "Promoted (demo)" if state["decision"] == "promote" else ("Changes requested" if state["decision"] == "request_changes" else ("Dismissed" if state["decision"] == "dismiss" else ("Evaluation passed (demo)" if state["evaluation"] and state["evaluation"]["gate_passed"] else review["status"]))),
        "severity": review["severity"], "affected": review["affected"], "traces": review["traces"],
        "owner": review["owner"], "updated": review["updated"],
        "baseline_pass_rate": percent(review["baseline"]["pass"], review["baseline"]["total"]),
        "candidate_pass_rate": percent(review["candidate"]["pass"], review["candidate"]["total"]),
        "decision": state["decision"], "evaluation": state["evaluation"],
    }


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.get("/api/health")
def health():
    return {"ok": True, "mode": "local-demo", "data": "synthetic", "connected_to_bentolabs": False}


@app.get("/api/reviews")
def list_reviews():
    return {"items": [public_review(r) for r in REVIEWS], "mode": "synthetic-demo"}


@app.get("/api/reviews/{review_id}")
def get_review(review_id: str):
    review = next((r for r in REVIEWS if r["id"] == review_id), None)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    result = dict(review)
    result["baseline"] = {**review["baseline"], "pass_rate": percent(review["baseline"]["pass"], review["baseline"]["total"])}
    result["candidate"] = {**review["candidate"], "pass_rate": percent(review["candidate"]["pass"], review["candidate"]["total"])}
    result["state"] = STATES[review_id]
    result["mode"] = "synthetic-demo"
    return result


@app.post("/api/reviews/{review_id}/evaluate")
def evaluate_review(review_id: str):
    review = next((r for r in REVIEWS if r["id"] == review_id), None)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    baseline = review["baseline"]
    candidate = review["candidate"]
    baseline_rate = percent(baseline["pass"], baseline["total"])
    candidate_rate = percent(candidate["pass"], candidate["total"])
    critical = review["critical_regressions"]
    gates = [
        {"name": "No critical fixture regressions", "passed": critical == 0, "detail": f"{critical} critical regression(s) in synthetic fixture set"},
        {"name": "Pass rate does not decrease", "passed": candidate_rate >= baseline_rate, "detail": f"{baseline_rate:.1f}% baseline → {candidate_rate:.1f}% candidate"},
        {"name": "Historical failure cohort included", "passed": review["affected"] > 0, "detail": f"{review['affected']} affected sample cases represented"},
        {"name": "Rollback target recorded", "passed": True, "detail": "Previous version v1.8.3 recorded in demo fixture"},
    ]
    gate_passed = all(g["passed"] for g in gates)
    evaluation = {
        "run_id": f"EVAL-DEMO-{review_id[-4:]}-{len(AUDIT)+1:02d}",
        "ran_at": now_iso(), "mode": "SIMULATED — synthetic fixture data; no agent was executed",
        "baseline_pass_rate": baseline_rate, "candidate_pass_rate": candidate_rate,
        "delta_points": round(candidate_rate - baseline_rate, 1),
        "baseline_latency_s": baseline["latency"], "candidate_latency_s": candidate["latency"],
        "baseline_cost_usd": baseline["cost"], "candidate_cost_usd": candidate["cost"],
        "critical_regressions": critical, "gates": gates, "gate_passed": gate_passed,
        "fixtures_passed": candidate["pass"], "fixtures_total": candidate["total"],
    }
    STATES[review_id]["evaluation"] = evaluation
    STATES[review_id]["decision"] = ""
    AUDIT.insert(0, {"at": now_iso(), "review_id": review_id, "event": "evaluation_simulated", "message": f"Synthetic evaluation run {evaluation['run_id']}; gate {'passed' if gate_passed else 'blocked'}."})
    return evaluation


@app.post("/api/reviews/{review_id}/decision")
def decide_review(review_id: str, body: DecisionRequest):
    review = next((r for r in REVIEWS if r["id"] == review_id), None)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    state = STATES[review_id]
    if body.decision == "promote":
        if not state["evaluation"]:
            raise HTTPException(status_code=409, detail="Run the synthetic evaluation before attempting promotion.")
        if not state["evaluation"]["gate_passed"]:
            raise HTTPException(status_code=409, detail="Promotion blocked: one or more demo release gates failed.")
    state["decision"] = body.decision
    event = {"at": now_iso(), "review_id": review_id, "event": body.decision, "message": body.note or f"Decision recorded in local demo: {body.decision.replace('_', ' ')}."}
    AUDIT.insert(0, event)
    return {"ok": True, "review": public_review(review), "audit_event": event, "mode": "local-demo-only"}


@app.get("/api/audit")
def audit_log():
    return {"items": AUDIT[:30], "mode": "local-demo-only"}
