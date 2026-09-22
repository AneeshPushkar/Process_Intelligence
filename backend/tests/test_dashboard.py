def test_dashboard_stats_metrics(client):
    # Register and login
    client.post("/api/auth/register", json={
        "full_name": "Metrics User",
        "email": "metrics@processiq.ai",
        "password": "Password123!",
        "organization": "Metrics Org"
    })
    token = client.post("/api/auth/login", json={
        "email": "metrics@processiq.ai",
        "password": "Password123!"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Initial stats
    empty_stats = client.get("/api/dashboard/stats", headers=headers).json()
    assert empty_stats["total_processes"] == 0
    assert empty_stats["average_confidence"] == 0.0

    # Create and analyze 2 processes
    p1 = client.post("/api/processes", headers=headers, json={
        "name": "Process 1",
        "description": "User submits form. Admin reviews submission."
    }).json()["id"]
    client.post(f"/api/processes/{p1}/analyze", headers=headers)

    p2 = client.post("/api/processes", headers=headers, json={
        "name": "Process 2",
        "description": "Customer buys product. Finance approves payment. Warehouse ships item."
    }).json()["id"]
    client.post(f"/api/processes/{p2}/analyze", headers=headers)

    # Fetch updated stats
    stats = client.get("/api/dashboard/stats", headers=headers).json()
    assert stats["total_processes"] == 2
    assert stats["average_confidence"] > 0
    assert stats["insights_generated_count"] > 0
    assert len(stats["recent_processes"]) == 2
    assert len(stats["confidence_trend"]) == 2
