def test_create_journal_entry(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Escritor",
        "race": "Elfo",
        "goal": "Documentar aventuras",
        "background": "Cronista",
        "stats": {"FUE": 0, "AGI": 1, "MEN": 2, "CAR": 2}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.post('/api/journal', json={
        "character_id": cid,
        "content": "Hoy comenzó la aventura..."
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert "entry_id" in res.get_json()

def test_get_journal_entries(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Narrador",
        "race": "Gnomo",
        "goal": "Recordar todo",
        "background": "Historiador",
        "stats": {"FUE": 0, "AGI": 1, "MEN": 3, "CAR": 1}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.get(f'/api/journal/{cid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "entries" in res.get_json()

def test_delete_journal_entry(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Memorioso",
        "race": "Humano",
        "goal": "No olvidar nada",
        "background": "Archivo viviente",
        "stats": {"FUE": 1, "AGI": 0, "MEN": 3, "CAR": 1}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    entry = client.post('/api/journal', json={
        "character_id": cid,
        "content": "Esta es una nota efímera."
    }, headers={"Authorization": f"Bearer {token}"})
    entry_id = entry.get_json()["entry_id"]

    res = client.delete(f'/api/journal/{entry_id}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["entry_id"] == entry_id

def test_create_decision(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Decisor",
        "race": "Enano",
        "goal": "Tomar buenas decisiones",
        "background": "Líder",
        "stats": {"FUE": 2, "AGI": 0, "MEN": 2, "CAR": 1}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.post('/api/decision', json={
        "character_id": cid,
        "description": "Salvar al aldeano",
        "impact": "Ganó aliados"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert "decision_id" in res.get_json()

def test_get_decisions(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Pensador",
        "race": "Humano",
        "goal": "Evaluar todas las opciones",
        "background": "Estratega",
        "stats": {"FUE": 0, "AGI": 1, "MEN": 3, "CAR": 2}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.get(f'/api/decision/{cid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "decisions" in res.get_json()

def test_delete_decision(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Accionista",
        "race": "Orco",
        "goal": "Actuar sin pensar",
        "background": "Impulsivo",
        "stats": {"FUE": 3, "AGI": 0, "MEN": 0, "CAR": 0}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    dec = client.post('/api/decision', json={
        "character_id": cid,
        "description": "Atacar sin preguntar"
    }, headers={"Authorization": f"Bearer {token}"})
    decision_id = dec.get_json()["decision_id"]

    res = client.delete(f'/api/decision/{decision_id}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["decision_id"] == decision_id
