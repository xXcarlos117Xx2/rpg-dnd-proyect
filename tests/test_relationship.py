def test_create_relationship(client, user_and_token):
    user, token = user_and_token
    # Crear dos personajes del mismo usuario
    char1 = client.post('/api/character', json={
        "name": "A",
        "race": "Elfo",
        "goal": "Conectar",
        "background": "Sociable",
        "stats": {"FUE": 0, "AGI": 1, "MEN": 1, "CAR": 3}
    }, headers={"Authorization": f"Bearer {token}"})
    cid1 = char1.get_json()["character_id"]

    char2 = client.post('/api/character', json={
        "name": "B",
        "race": "Enano",
        "goal": "Aislarse",
        "background": "Huraño",
        "stats": {"FUE": 1, "AGI": 1, "MEN": 1, "CAR": 0}
    }, headers={"Authorization": f"Bearer {token}"})
    cid2 = char2.get_json()["character_id"]

    res = client.post('/api/relationship', json={
        "source_id": cid1,
        "target_id": cid2,
        "relation_type": "Amistad"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert "relationship_id" in res.get_json()

def test_get_relationships(client, user_and_token):
    user, token = user_and_token
    char = client.post('/api/character', json={
        "name": "Nodo",
        "race": "Humano",
        "goal": "Conocer aliados",
        "background": "Diplomático",
        "stats": {"FUE": 0, "AGI": 0, "MEN": 2, "CAR": 3}
    }, headers={"Authorization": f"Bearer {token}"})
    cid = char.get_json()["character_id"]

    res = client.get(f'/api/relationship/{cid}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "relationships" in res.get_json()

def test_delete_relationship(client, user_and_token):
    user, token = user_and_token
    c1 = client.post('/api/character', json={
        "name": "X",
        "race": "Orco",
        "goal": "Alianza",
        "background": "Guerrero",
        "stats": {"FUE": 2, "AGI": 1, "MEN": 0, "CAR": 0}
    }, headers={"Authorization": f"Bearer {token}"})
    id1 = c1.get_json()["character_id"]

    c2 = client.post('/api/character', json={
        "name": "Y",
        "race": "Humano",
        "goal": "Defender",
        "background": "Paladín",
        "stats": {"FUE": 1, "AGI": 1, "MEN": 1, "CAR": 1}
    }, headers={"Authorization": f"Bearer {token}"})
    id2 = c2.get_json()["character_id"]

    rel = client.post('/api/relationship', json={
        "source_id": id1,
        "target_id": id2,
        "relation_type": "Rivalidad"
    }, headers={"Authorization": f"Bearer {token}"})
    rel_id = rel.get_json()["relationship_id"]

    res = client.delete(f'/api/relationship/{rel_id}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["relationship_id"] == rel_id
