# Change Review Workbench — BentoLabs AI proof-of-work concept

A small, local-only full-stack concept demonstrating a change-review workflow for AI-agent reliability. It is an independent work sample based only on BentoLabs' public product descriptions.

**Important boundaries**
- This is not an official BentoLabs product, not affiliated with BentoLabs, and not connected to its systems.
- Every company, trace, review, evaluation metric, and event shown in the demo is illustrative synthetic data.
- The “Run evaluation” action simulates results from seeded fixtures. It does not run an AI agent or claim measured performance.
- “Promote” records a local demo decision only; it does not deploy or change anything in production.

## Run locally

Requirements: Python 3.10+

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000. The API docs are at http://127.0.0.1:8000/docs.

## Main API routes

- `GET /api/health` — indicates local-demo mode and confirms there is no BentoLabs connection.
- `GET /api/reviews` — list of synthetic review candidates.
- `GET /api/reviews/{review_id}` — candidate details, diff, evidence and fixture metrics.
- `POST /api/reviews/{review_id}/evaluate` — deterministic simulation of release gates using seeded synthetic values.
- `POST /api/reviews/{review_id}/decision` — records a local promote/request-changes/dismiss decision, with promotion blocked until a passing demo evaluation exists.
- `GET /api/audit` — local in-memory audit trail for the current server process.

## Stack

- Backend: Python, FastAPI, Pydantic, typed REST endpoints.
- Frontend: semantic HTML, CSS and JavaScript; responsive layout; async API calls; busy/error states; accessible button labels.
- Runtime: in-memory seeded fixtures for clarity and zero setup dependencies.

## What this proves

- Backend/API design and validation, HTTP status handling, typed request bodies, workflow gates and audit events.
- Frontend implementation of review selection, evidence views, diff rendering, simulated evaluation, decision gating and error states.
- Product thinking around traceability, regression risk, reversible changes, and human review.

## Known limitations / next steps

This is a concept prototype, not production software. A production version would require authentication and RBAC, durable storage, tenant isolation, real trace/evaluation connectors, background jobs, idempotency, telemetry, secret management, CSRF/CORS policy, pagination, rate limiting, robust audit retention, and integration tests against an authorized staging environment.

## Run tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

The included tests verify the health contract, list/detail API, blocked promotion without an evaluation, allowed local demo promotion after a passing evaluation, and blocked promotion when a critical regression gate fails.
