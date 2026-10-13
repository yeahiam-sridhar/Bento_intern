from fastapi.testclient import TestClient
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app, STATES, AUDIT

client = TestClient(app)

def reset_demo_state():
    for key in STATES:
        STATES[key]["decision"] = ""
        STATES[key]["evaluation"] = None
    AUDIT.clear()

def test_health_marks_synthetic_and_disconnected():
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['data'] == 'synthetic'
    assert r.json()['connected_to_bentolabs'] is False

def test_review_detail_exists_and_has_diff():
    r = client.get('/api/reviews/REV-0248')
    assert r.status_code == 200
    assert r.json()['mode'] == 'synthetic-demo'
    assert len(r.json()['diff']) >= 2

def test_promote_is_blocked_until_eval():
    reset_demo_state()
    r = client.post('/api/reviews/REV-0248/decision', json={'decision':'promote','note':'test'})
    assert r.status_code == 409

def test_passing_eval_allows_local_demo_promotion():
    reset_demo_state()
    ev = client.post('/api/reviews/REV-0248/evaluate')
    assert ev.status_code == 200 and ev.json()['gate_passed'] is True
    decision = client.post('/api/reviews/REV-0248/decision', json={'decision':'promote','note':'test'})
    assert decision.status_code == 200
    assert decision.json()['review']['decision'] == 'promote'

def test_failed_gate_blocks_promotion():
    reset_demo_state()
    ev = client.post('/api/reviews/REV-0247/evaluate')
    assert ev.status_code == 200 and ev.json()['gate_passed'] is False
    decision = client.post('/api/reviews/REV-0247/decision', json={'decision':'promote'})
    assert decision.status_code == 409
