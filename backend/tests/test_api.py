from app.utils.formatting import risk_band


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": True, "retrieval_ready": True}


def test_claims_listing_and_filters(client):
    response = client.get("/api/v1/claims?limit=5&risk_band=HIGH")
    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total"] >= len(payload["items"])
    assert payload["pagination"]["limit"] == 5
    assert all(item["risk_band"] == "HIGH" for item in payload["items"])


def test_claim_detail_contains_prediction_and_anomaly(client):
    first = client.get("/api/v1/claims?limit=1").json()["items"][0]
    response = client.get(f"/api/v1/claims/{first['claim_id']}")
    assert response.status_code == 200
    payload = response.json()
    assert "claim" in payload
    assert 0 <= payload["prediction"]["denial_probability"] <= 1
    assert payload["prediction"]["risk_band"] in {"LOW", "MEDIUM", "HIGH"}
    assert payload["prediction"]["top_factors"]
    assert "anomaly_score" in payload["anomaly"]


def test_claim_not_found_error(client):
    response = client.get("/api/v1/claims/NO_SUCH_CLAIM")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "CLAIM_NOT_FOUND"


def test_analytics_and_model_metrics(client):
    summary = client.get("/api/v1/analytics/summary")
    assert summary.status_code == 200
    assert summary.json()["total_claims"] > 0

    drivers = client.get("/api/v1/analytics/drivers?limit=10")
    assert drivers.status_code == 200
    assert len(drivers.json()["items"]) == 10

    metrics = client.get("/api/v1/model/metrics")
    assert metrics.status_code == 200
    payload = metrics.json()
    assert payload["model_name"] == "xgboost"
    assert "roc_auc" in payload["test"]
    assert "precision_at_top_10pct" in payload["test"]


def test_risk_band_mapping_uses_selected_threshold():
    assert risk_band(0.1, 0.2729) == "LOW"
    assert risk_band(0.4, 0.2729) == "MEDIUM"
    assert risk_band(0.8, 0.2729) == "HIGH"

