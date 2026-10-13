# AI Agent Change Review Workbench

An independent proof-of-work prototype for reviewing AI-agent changes. It combines a FastAPI backend with a browser-based HTML/CSS/JavaScript workbench to demonstrate change review, evaluation gates, and release decisions using synthetic data.

This project was built to demonstrate product thinking, backend/API development, workflow validation, and testing. It is not an official BentoLabs product, is not affiliated with BentoLabs, and does not connect to BentoLabs or any other external system.

## What it demonstrates

- A review queue with change summaries, diffs, and supporting evidence.
- Deterministic, simulated evaluation gates using seeded synthetic fixtures.
- Release decisions gated on evaluation results.
- A local, in-memory audit history for the current server process.
- REST API design, request validation, error handling, and API tests.

All companies, traces, reviews, events, and metrics are illustrative synthetic data. The evaluation action does not run an AI agent or represent measured performance. A promotion is only a local demo decision; it does not deploy or change anything in production.

## Run locally

Requirements: Python 3.10+

```powershell
git clone https://github.com/yeahiam-sridhar/Bento_intern.git
cd Bento_intern
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000 in your browser. Interactive API documentation is available at http://127.0.0.1:8000/docs.

On Windows, you can also start the app using `run_windows.bat`.

## API routes

- `GET /api/health` — reports local-demo mode and confirms there is no BentoLabs connection.
- `GET /api/reviews` — lists synthetic review candidates.
- `GET /api/reviews/{review_id}` — returns a candidate's details, diff, evidence, and fixture metrics.
- `POST /api/reviews/{review_id}/evaluate` — simulates release gates using seeded synthetic values.
- `POST /api/reviews/{review_id}/decision` — records a local `promote`, `request-changes`, or `dismiss` decision. Promotion requires a passing demo evaluation.
- `GET /api/audit` — returns the in-memory audit trail for the current server process.

## Run tests

```powershell
pip install -r requirements-dev.txt
pytest -q
```

The tests cover the health contract, review list and detail endpoints, promotion gating, successful local demo promotion after a passing evaluation, and blocking promotion when a critical regression gate fails.

## Project files

- `app.py` — FastAPI backend and synthetic fixtures.
- `frontend/index.html` — browser-based workbench.
- `tests/test_api.py` — API workflow tests.
- `BentoLabs_AI_Proof_of_Work.pdf` — accompanying concept report.

## Limitations

This is a local concept prototype, not production software. It has no authentication or RBAC, durable storage, tenant isolation, real agent or evaluation connectors, background jobs, production deployment, or persistent audit retention. A production implementation would also need appropriate telemetry, secret management, CSRF/CORS policy, pagination, rate limiting, and integration tests against an authorized staging environment.
