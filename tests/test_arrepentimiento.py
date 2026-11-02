def test_arrepentimiento_sin_sesion(client, producto):
    # Sin headers, el backend debe rebotarlo con 401
    r = client.post(f"/pedidos/1/revocacion", json={"producto_id": producto["id"]})
    assert r.status_code == 401

def test_arrepentimiento_no_revela(client, cliente):
    # Intentamos arrepentirnos de un pedido que no existe (ID 99999)
    r = client.post("/pedidos/99999/revocacion", headers=cliente, json={"producto_id": 1})
    
    # El profe pide que devuelva 201 y un código (para no revelar que no existe)
    assert r.status_code == 201
    assert "codigo" in r.json()