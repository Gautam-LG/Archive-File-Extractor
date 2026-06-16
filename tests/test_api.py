import time
from app.routes import *

def test_health(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json == {"status": "ok"}

def test_post_extraction_missing_file(client):
    resp = client.post("/extractions", data={"pattern": "*.json"})
    assert resp.status_code == 400

def test_post_extraction_missing_pattern(client, sample_zip):
    with open(sample_zip, "rb") as f:
        resp = client.post("/extractions", data={"archive": (f, "sample.zip")})
    assert resp.status_code == 400

def test_get_extraction_not_found(client):
    resp = client.get("/extractions/999")
    assert resp.status_code == 404

def test_full_flow(client, sample_zip):
    with open(sample_zip, "rb") as f:
        resp = client.post(
            "/extractions",
            data={"archive":(f,"sample.zip"), "pattern": "*.json"},
            content_type="multipart/form-data"
        )
    assert resp.status_code == 202
    job_id = resp.get_json()["job_id"]

    for _ in range(20):
        status_resp = client.get(f"/extractions/{job_id}")
        if status_resp.get_json()["status"] in ("completed", "failed"):
            break
        time.sleep(0.5)

    data = status_resp.get_json()
    assert data["status"] == "completed"
    assert data["match_count"] == 2

    result_resp = client.get(f"/extractions/{job_id}/results")
    results = result_resp.get_json()
    assert results["total"] == 2
    names = {r["file_name"] for r in results["results"]}
    assert names == {"b.json", "c.json"}
