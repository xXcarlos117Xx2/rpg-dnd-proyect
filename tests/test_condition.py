def test_create_condition(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Gladiador",
        "race": "Humano",
        "goal": "Sobrevivir la arena",
        "background": "Combatiente",
        "stats": {"FUE": 3, "AGI": 1, "MEN": 0, "CAR": 0}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.post('/api/condition', json={
        "character_id": cid,
        "name": "Herido",
        "description": "Tiene una herida abierta",
        "temporary": True
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert "condition_id" in res.get_json()

def test_get_conditions(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Clérigo",
        "race": "Enano",
        "goal": "Curar a los heridos",
        "background": "Sanador",
        "stats": {"FUE": 1, "AGI": 0, "MEN": 2, "CAR": 2}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.get(f'/api/condition/{cid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "conditions" in res.get_json()

def test_delete_condition(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Hechicero",
        "race": "Orco",
        "goal": "Superar maldiciones",
        "background": "Cazador de sombras",
        "stats": {"FUE": 2, "AGI": 1, "MEN": 1, "CAR": 0}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    condition = client.post('/api/condition', json={
        "character_id": cid,
        "name": "Paralizado",
        "description": "No puede moverse"
    }, headers={"Authorization": f"Bearer {token}"})
    condition_id = condition.get_json()["condition_id"]

    res = client.delete(f'/api/condition/{condition_id}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["condition_id"] == condition_id
