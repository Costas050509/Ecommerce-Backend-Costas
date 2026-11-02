"""Lo que se repite en todos los tests."""

def registrar(client, email="cliente@prueba.com", password="clave-larga-123"):
    r = client.post(
        "/auth/register",
        json={
            "nombre": "Cliente de Prueba",
            "email": email,
            "password": password,
            "acepto_tratamiento": True,  # Arreglado el campo en rojo
        },
    )
    assert r.status_code == 201, r.text
    return email, password

def token_de(client, email, password):
    # Tu endpoint de login usa form-data (username y password)
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def cuerpo_pedido(producto_id, cantidad):
    """El body que espera TU checkout. Si pide más campos, van acá."""
    # Tu backend (PedidoCreate) espera esta estructura exacta con items
    return {"items": [{"producto_id": producto_id, "cantidad": cantidad}]}