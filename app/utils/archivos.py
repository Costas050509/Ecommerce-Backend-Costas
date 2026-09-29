FIRMAS = (
    b"\xff\xd8\xff",       # jpg
    b"\x89PNG\r\n\x1a\n", # png
    b"RIFF",               # webp
)


def parece_imagen(contenido: bytes) -> bool:
    return contenido.startswith(FIRMAS)
