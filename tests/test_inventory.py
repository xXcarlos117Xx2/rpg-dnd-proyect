def test_add_inventory_item(client, user_and_token):
    user, token = user_and_token
    # Crear personaje primero
    character = client.post('/api/character', json={
        "name": "Carlos",
        "race": "Humano",
        "goal": "Sobrevivir",
        "background": "Mercader",
        "stats": {"FUE": 1, "AGI": 1, "MEN": 1, "CAR": 1}
    }, headers={"Authorization": f"Bearer {token}"})
    character_id = character.get_json()["character_id"]

    res = client.post('/api/inventory', json={
        "character_id": character_id,
        "item": "Espada corta",
        "description": "Una espada básica.",
        "magical": False,
        "notes": "Recibida del abuelo"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert "item_id" in res.get_json()

def test_get_inventory(client, user_and_token):
    user, token = user_and_token
    character = client.post('/api/character', json={
        "name": "Test",
        "race": "Humano",
        "goal": "Explorar",
        "background": "Guerrero",
        "stats": {"FUE": 2, "AGI": 0, "MEN": 0, "CAR": 0}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = character.get_json()["character_id"]

    res = client.get(f'/api/inventory/{cid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "items" in res.get_json()

def test_update_inventory_item(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "A",
        "race": "Elfo",
        "goal": "Destruir anillo",
        "background": "Misterioso",
        "stats": {"FUE": 1, "AGI": 2, "MEN": 1, "CAR": 0}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    item = client.post('/api/inventory', json={
        "character_id": cid,
        "item": "Anillo",
        "description": "Brilla",
    }, headers={"Authorization": f"Bearer {token}"})
    item_id = item.get_json()["item_id"]

    res = client.put(f'/api/inventory/{item_id}', json={"notes": "Debe ser destruido"},
                     headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["item_id"] == item_id

def test_delete_inventory_item(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "B",
        "race": "Orco",
        "goal": "Luchar",
        "background": "Bestia",
        "stats": {"FUE": 3, "AGI": 0, "MEN": 0, "CAR": 0}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    item = client.post('/api/inventory', json={
        "character_id": cid,
        "item": "Maza",
        "description": "Pesada"
    }, headers={"Authorization": f"Bearer {token}"})
    iid = item.get_json()["item_id"]

    res = client.delete(f'/api/inventory/{iid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["item_id"] == iid
