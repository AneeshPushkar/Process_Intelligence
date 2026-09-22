def test_process_lifecycle(client):
    # Register and login
    client.post("/api/auth/register", json={
        "full_name": "Dev User",
        "email": "dev@processiq.ai",
        "password": "DevPassword123!",
        "organization": "Dev Team"
    })
    token = client.post("/api/auth/login", json={
        "email": "dev@processiq.ai",
        "password": "DevPassword123!"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Process
    create_res = client.post("/api/processes", headers=headers, json={
        "name": "Procurement Request",
        "description": "Employee submits request. Manager reviews request. If approved, Finance issues payment."
    })
    assert create_res.status_code == 201
    proc_data = create_res.json()
    proc_id = proc_data["id"]
    assert proc_data["status"] == "Draft"
    assert proc_data["name"] == "Procurement Request"

    # List Processes
    list_res = client.get("/api/processes", headers=headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1
    assert any(p["id"] == proc_id for p in items)

    # Search filter
    search_res = client.get("/api/processes?search=Procurement", headers=headers)
    assert search_res.status_code == 200
    assert len(search_res.json()) >= 1

    # Analyze Process
    analyze_res = client.post(f"/api/processes/{proc_id}/analyze", headers=headers)
    assert analyze_res.status_code == 200
    analyzed = analyze_res.json()
    assert analyzed["status"] == "Completed"
    assert analyzed["overall_confidence"] is not None
    assert analyzed["overall_confidence"] > 0
    assert analyzed["confidence_decision"] in ["HIGH", "REVIEW", "LOW"]
    assert analyzed["analysis"] is not None
    assert analyzed["model"] is not None
    assert analyzed["validation"] is not None
    assert analyzed["confidence"] is not None
    assert analyzed["intelligence"] is not None

    # Retrieve Process by ID
    get_res = client.get(f"/api/processes/{proc_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == proc_id

    # Delete Process
    del_res = client.delete(f"/api/processes/{proc_id}", headers=headers)
    assert del_res.status_code == 204

    # Confirm Deleted
    confirm_res = client.get(f"/api/processes/{proc_id}", headers=headers)
    assert confirm_res.status_code == 404
