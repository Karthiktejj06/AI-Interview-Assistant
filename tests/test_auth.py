def test_register_user(client):
    """Test candidate registration API."""
    response = client.post("/api/v1/auth/register", json={
        "full_name": "Test Candidate",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["full_name"] == "Test Candidate"

def test_register_duplicate_email(client):
    """Test duplicate email rejection."""
    payload = {
        "full_name": "Test Candidate",
        "email": "duplicate@example.com",
        "password": "password123"
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"]

def test_login_user(client):
    """Test candidate login API."""
    # Register first
    client.post("/api/v1/auth/register", json={
        "full_name": "Login User",
        "email": "login@example.com",
        "password": "secretpassword"
    })

    # Test valid login
    response = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "secretpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Test invalid password
    bad_resp = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "wrongpassword"
    })
    assert bad_resp.status_code == 401
