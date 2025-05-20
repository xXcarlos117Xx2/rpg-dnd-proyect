import pytest

def test_create_character(client, user_and_token):
    user, token = user_and_token
    res = client.post('/api/character', json={
        "name": "Carlos",
        "race": "Humano",
        "goal": "Ser leyenda",
        "background": "Vendedor carismático",
        "stats": {"FUE": 2, "AGI": 1, "MEN": -1, "CAR": 3}
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    data = res.get_json()
    print(res.status_code, res.get_json())
    assert "character_id" in data

def test_get_characters(client, user_and_token):
    user, token = user_and_token
    res = client.get('/api/character', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "characters" in res.get_json()

def test_update_character(client, user_and_token):
    user, token = user_and_token
    create = client.post('/api/character', json={
        "name": "Carlos",
        "race": "Humano",
        "goal": "Ser leyenda",
        "background": "Vendedor carismático",
        "stats": {"FUE": 2, "AGI": 1, "MEN": -1, "CAR": 3}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = create.get_json()["character_id"]

    update = client.put(f'/api/character/{cid}', json={"level": 3}, headers={"Authorization": f"Bearer {token}"})
    assert update.status_code == 200
    assert update.get_json()["character_id"] == cid

def test_delete_character(client, user_and_token):
    user, token = user_and_token
    create = client.post('/api/character', json={
        "name": "Carlos",
        "race": "Humano",
        "goal": "Ser leyenda",
        "background": "Vendedor carismático",
        "stats": {"FUE": 2, "AGI": 1, "MEN": -1, "CAR": 3}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = create.get_json()["character_id"]

    delete = client.delete(f'/api/character/{cid}', headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == 200
    assert delete.get_json()["character_id"] == cid
