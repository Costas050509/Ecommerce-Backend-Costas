def test_salud_responde_con_la_base(client):
    r = client.get("/salud")
    assert r.status_code == 200
    assert r.json() == {"estado": "ok", "base": "ok"}