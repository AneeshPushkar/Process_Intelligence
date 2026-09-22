def test_strict_user_data_isolation(client):
    """
    Verify complete tenant isolation between User A and User B:
    User B must NOT be able to list, retrieve, delete, analyze, or see
    User A's processes in history or dashboard metrics.
    """
    # 1. Register User A and User B
    client.post("/api/auth/register", json={
        "full_name": "User Alpha",
        "email": "alpha@tenant.com",
        "password": "PasswordAlpha123!",
        "organization": "Alpha Inc"
    })
    client.post("/api/auth/register", json={
        "full_name": "User Beta",
        "email": "beta@tenant.com",
        "password": "PasswordBeta123!",
        "organization": "Beta Corp"
    })

    # Login User A
    token_a = client.post("/api/auth/login", json={
        "email": "alpha@tenant.com",
        "password": "PasswordAlpha123!"
    }).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Login User B
    token_b = client.post("/api/auth/login", json={
        "email": "beta@tenant.com",
        "password": "PasswordBeta123!"
    }).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 2. User A creates Process A
    proc_a_res = client.post("/api/processes", headers=headers_a, json={
        "name": "Alpha Confidential Workflow",
        "description": "HR verifies credentials. Security issues security clearance badge."
    })
    assert proc_a_res.status_code == 201
    proc_a_id = proc_a_res.json()["id"]

    # Analyze Process A under User A
    analyze_res = client.post(f"/api/processes/{proc_a_id}/analyze", headers=headers_a)
    assert analyze_res.status_code == 200

    # 3. User B tries to list processes -> Must NOT see Process A
    list_b_res = client.get("/api/processes", headers=headers_b)
    assert list_b_res.status_code == 200
    user_b_processes = list_b_res.json()
    assert len(user_b_processes) == 0
    assert not any(p["id"] == proc_a_id for p in user_b_processes)

    # 4. User B tries to retrieve Process A by ID -> Must return 404
    get_b_res = client.get(f"/api/processes/{proc_a_id}", headers=headers_b)
    assert get_b_res.status_code == 404

    # 5. User B tries to analyze Process A -> Must return 404
    analyze_b_res = client.post(f"/api/processes/{proc_a_id}/analyze", headers=headers_b)
    assert analyze_b_res.status_code == 404

    # 6. User B tries to delete Process A -> Must return 404
    del_b_res = client.delete(f"/api/processes/{proc_a_id}", headers=headers_b)
    assert del_b_res.status_code == 404

    # 7. User B's dashboard stats must be completely empty (0 processes, 0 confidence)
    stats_b_res = client.get("/api/dashboard/stats", headers=headers_b)
    assert stats_b_res.status_code == 200
    stats_b = stats_b_res.json()
    assert stats_b["total_processes"] == 0
    assert stats_b["average_confidence"] == 0.0
    assert len(stats_b["recent_processes"]) == 0

    # 8. Confirm Process A is still alive and accessible for User A
    get_a_res = client.get(f"/api/processes/{proc_a_id}", headers=headers_a)
    assert get_a_res.status_code == 200
    assert get_a_res.json()["name"] == "Alpha Confidential Workflow"

    # User A's dashboard stats reflect 1 process
    stats_a = client.get("/api/dashboard/stats", headers=headers_a).json()
    assert stats_a["total_processes"] == 1
    assert stats_a["average_confidence"] > 0.0
