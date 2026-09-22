def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "ProcessIQ"
    assert "version" in data
    assert data["analysis_mode"] == "Local Fallback"
