def test_roll_success(client, user_and_token):
    user, token = user_and_token
    res = client.post('/api/character', json={
        "name": "Carlos",
        "race": "Humano",
        "goal": "Ser leyenda",
        "background": "Heroico",
        "stats": {"FUE": 3, "AGI": 1, "MEN": 0, "CAR": 2}
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    cid = res.get_json()["character_id"]

    # Hacer tirada
    roll = client.get(f'/api/roll?character_id={cid}&stat=FUE&difficulty=10')
    assert roll.status_code == 200
    data = roll.get_json()["result"]
    assert data["stat"] == "FUE"
    assert 1 <= data["base_roll"] <= 20
    assert data["modifier"] == 3
    assert isinstance(data["success"], bool)


def test_roll_missing_params(client, user_and_token):
    _, token = user_and_token
    roll = client.get('/api/roll', headers={"Authorization": f"Bearer {token}"})
    assert roll.status_code == 400
    assert "Parámetros" in roll.get_json()["error"]


def test_roll_invalid_character(client, user_and_token):
    _, token = user_and_token
    roll = client.get('/api/roll?character_id=999&stat=FUE&difficulty=10',
                      headers={"Authorization": f"Bearer {token}"})
    assert roll.status_code == 404
    assert "no encontrado" in roll.get_json()["error"]


def test_roll_invalid_stat(client, user_and_token):
    user, token = user_and_token

    res = client.post('/api/character', json={
        "name": "Carlos",
        "race": "Humano",
        "goal": "Ser leyenda",
        "background": "Heroico",
        "stats": {"FUE": 3, "AGI": 1, "MEN": 0, "CAR": 2}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = res.get_json()["character_id"]

    roll = client.get(f'/api/roll?character_id={cid}&stat=INT&difficulty=10',
                      headers={"Authorization": f"Bearer {token}"})
    assert roll.status_code == 400
    assert "no encontrada" in roll.get_json()["error"]
