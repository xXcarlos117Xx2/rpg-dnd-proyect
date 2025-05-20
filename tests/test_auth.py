def test_signup_and_login(client):
    res = client.post('/api/signup', json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "pass123"
    })
    assert res.status_code == 201

    res = client.post('/api/login', json={
        "login_name": "newuser",
        "password": "pass123"
    })
    assert res.status_code == 200
    assert "access_token" in res.get_json()

def test_userinfo(client, user_and_token):
    _, token = user_and_token
    res = client.get('/api/userinfo', headers={
        "Authorization": f"Bearer {token}"
    })
    assert res.status_code == 200
    assert "username" in res.get_json()
