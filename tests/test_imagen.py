# Archivo falso con extensión de imagen
TRAMPA = ("foto.png", b"esto es texto con nombre de imagen", "image/png")

def test_archivo_trampa_da_415(client, admin, producto):
    r = client.post(
        f"/productos/{producto['id']}/imagen",
        headers=admin,
        files={"archivo": TRAMPA},
    )
    assert r.status_code == 415

def test_cliente_no_puede_subir_imagen(client, cliente, producto):
    r = client.post(
        f"/productos/{producto['id']}/imagen",
        headers=cliente, # <-- Es un cliente normal, no un admin
        files={"archivo": TRAMPA},
    )
    assert r.status_code == 403 # Forbidden

def test_sin_sesion_no_puede_subir_imagen(client, producto):
    r = client.post(
        f"/productos/{producto['id']}/imagen",
        files={"archivo": TRAMPA}, # <-- Sin headers
    )
    assert r.status_code == 401