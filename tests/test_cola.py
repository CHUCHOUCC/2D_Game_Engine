import pytest

from app.dominio import ContadorPuntos, Evento
from app.estructuras import Cola, ColaVaciaError


def test_cola_nueva_esta_vacia():
    assert Cola().esta_vacia()


def test_fifo_el_primero_en_entrar_es_el_primero_en_salir():
    cola = Cola()
    for dato in (1, 2, 3):
        cola.encolar(dato)
    assert cola.frente() == 1
    assert cola.final() == 3
    assert [cola.desencolar() for _ in range(3)] == [1, 2, 3]


def test_eventos_salen_en_orden_y_el_puntaje_termina_en_15():
    cola = Cola()
    entrada = [Evento("moneda", "A"), Evento("moneda", "B"), Evento("daño")]
    for evento in entrada:
        cola.encolar(evento)

    contador = ContadorPuntos()
    salida = []
    while not cola.esta_vacia():
        evento = cola.desencolar()
        salida.append(evento)
        contador.aplicar(evento)

    assert salida == entrada
    assert contador.puntaje == 15


def test_al_retirar_el_ultimo_frente_y_final_quedan_vacios():
    cola = Cola()
    cola.encolar("unico")
    assert cola.desencolar() == "unico"
    assert cola.esta_vacia()
    with pytest.raises(ColaVaciaError):
        cola.frente()
    with pytest.raises(ColaVaciaError):
        cola.final()


def test_encolar_de_nuevo_despues_de_vaciar_funciona():
    cola = Cola()
    cola.encolar("a")
    cola.desencolar()
    cola.encolar("b")
    assert cola.frente() == "b"
    assert cola.final() == "b"
    assert cola.desencolar() == "b"


def test_desencolar_cola_vacia_sigue_una_regla_explicita():
    with pytest.raises(ColaVaciaError):
        Cola().desencolar()
