from app.dominio import ContadorPuntos, Evento

MONEDA = Evento("moneda")
DANO = Evento("daño")


def procesar(eventos):
    """Procesa los eventos uno por uno y devuelve el puntaje tras cada uno."""
    contador = ContadorPuntos()
    return [(contador.aplicar(e), contador.puntaje)[1] for e in eventos]


def test_moneda_moneda_dano_da_10_20_15():
    assert procesar([MONEDA, MONEDA, DANO]) == [10, 20, 15]


def test_dano_desde_cero_deja_cero():
    assert procesar([DANO]) == [0]


def test_lista_vacia_conserva_cero():
    assert procesar([]) == []
    assert ContadorPuntos().puntaje == 0


def test_evento_desconocido_conserva_el_puntaje_anterior():
    contador = ContadorPuntos()
    contador.aplicar(MONEDA)
    mensaje = contador.aplicar(Evento("teletransporte"))
    assert contador.puntaje == 10
    assert "desconocido" in mensaje
