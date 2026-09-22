def test_user_registration_and_login(client):
    # 1. Register
    reg_payload = {
        "full_name": "Alice Engineer",
        "email": "alice@processiq.ai",
        "password": "SecurePassword123!",
        "organization": "Acme Corp"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["email"] == "alice@processiq.ai"
    assert user_data["full_name"] == "Alice Engineer"
    assert "password_hash" not in user_data

    # 2. Duplicate registration rejected
    dup_res = client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"].lower()

    # 3. Invalid login
    bad_login = client.post("/api/auth/login", json={
        "email": "alice@processiq.ai",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 4. Valid login returns JWT
    login_res = client.post("/api/auth/login", json={
        "email": "alice@processiq.ai",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # 5. Protected /me without token fails
    unauth_me = client.get("/api/auth/me")
    assert unauth_me.status_code == 401

    # 6. Protected /me with token succeeds
    auth_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert auth_me.status_code == 200
    assert auth_me.json()["email"] == "alice@processiq.ai"

    # 7. Logout
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200
