def test_create_spell(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Mago",
        "race": "Elfo",
        "goal": "Dominar el arcano",
        "background": "Estudioso",
        "stats": {"FUE": 0, "AGI": 1, "MEN": 3, "CAR": 1}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.post('/api/spell', json={
        "character_id": cid,
        "name": "Bola de fuego",
        "type": "Ofensivo",
        "description": "Inflige daño en área",
        "uses": 3,
        "uses_max": 3
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert "spell_id" in res.get_json()

def test_get_spells(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Hechicero",
        "race": "Humano",
        "goal": "Explorar magia antigua",
        "background": "Investigador",
        "stats": {"FUE": 0, "AGI": 1, "MEN": 2, "CAR": 2}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.get(f'/api/spell/{cid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "spells" in res.get_json()

def test_update_spell(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Ilusionista",
        "race": "Gnomo",
        "goal": "Confundir enemigos",
        "background": "Tramposo",
        "stats": {"FUE": 0, "AGI": 2, "MEN": 2, "CAR": 2}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    sp = client.post('/api/spell', json={
        "character_id": cid,
        "name": "Invisibilidad",
        "type": "Defensivo",
        "description": "Te hace invisible",
        "uses": 2,
        "uses_max": 3
    }, headers={"Authorization": f"Bearer {token}"})
    sid = sp.get_json()["spell_id"]

    res = client.put(f'/api/spell/{sid}', json={
        "description": "Desaparecer completamente",
        "uses": 1
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["spell_id"] == sid

def test_delete_spell(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Conjurador",
        "race": "Enano",
        "goal": "Llamar aliados mágicos",
        "background": "Chamán",
        "stats": {"FUE": 1, "AGI": 0, "MEN": 3, "CAR": 1}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    sp = client.post('/api/spell', json={
        "character_id": cid,
        "name": "Evocar elemental",
        "type": "Invocación",
        "description": "Crea un elemental",
        "uses": 1,
        "uses_max": 3
    }, headers={"Authorization": f"Bearer {token}"})
    sid = sp.get_json()["spell_id"]

    res = client.delete(f'/api/spell/{sid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["spell_id"] == sid
