def test_create_ability(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Héroe",
        "race": "Místico",
        "goal": "Dominar la magia",
        "background": "Sabio",
        "stats": {"FUE": 0, "AGI": 0, "MEN": 3, "CAR": 1}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.post('/api/ability', json={
        "character_id": cid,
        "name": "Meditación",
        "description": "Recupera energía",
        "uses_per_session": 3
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert "ability_id" in res.get_json()

def test_get_abilities(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Sabio",
        "race": "Mago",
        "goal": "Saber absoluto",
        "background": "Archivero",
        "stats": {"FUE": 0, "AGI": 0, "MEN": 2, "CAR": 2}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.get(f'/api/ability/{cid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "abilities" in res.get_json()

def test_update_ability(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Luz",
        "race": "Hada",
        "goal": "Iluminar",
        "background": "Guía",
        "stats": {"FUE": 0, "AGI": 1, "MEN": 2, "CAR": 2}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    ab = client.post('/api/ability', json={
        "character_id": cid,
        "name": "Brillar",
        "description": "Luz mágica",
        "uses_per_session": 2
    }, headers={"Authorization": f"Bearer {token}"})
    aid = ab.get_json()["ability_id"]

    res = client.put(f'/api/ability/{aid}', json={
        "description": "Luz mágica intensa",
        "used": True
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["ability_id"] == aid

def test_delete_ability(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Oscuro",
        "race": "Sombrío",
        "goal": "Confundir",
        "background": "Espía",
        "stats": {"FUE": 1, "AGI": 1, "MEN": 1, "CAR": 1}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    ab = client.post('/api/ability', json={
        "character_id": cid,
        "name": "Esconderse",
        "description": "Desaparece de la vista",
        "uses_per_session": 1
    }, headers={"Authorization": f"Bearer {token}"})
    aid = ab.get_json()["ability_id"]

    res = client.delete(f'/api/ability/{aid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["ability_id"] == aid
