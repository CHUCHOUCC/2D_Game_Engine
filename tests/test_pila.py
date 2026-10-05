import pytest

from app.estructuras import Pila, PilaVaciaError


def test_pila_nueva_esta_vacia():
    assert Pila().esta_vacia()


def test_lifo_el_ultimo_en_entrar_es_el_primero_en_salir():
    pila = Pila()
    for dato in (1, 2, 3):
        pila.apilar(dato)
    assert [pila.desapilar() for _ in range(3)] == [3, 2, 1]
    assert pila.esta_vacia()


def test_tope_no_retira_el_elemento():
    pila = Pila()
    pila.apilar("a")
    assert pila.tope() == "a"
    assert not pila.esta_vacia()


def test_deshacer_dos_movimientos_con_posiciones():
    # Se guarda una tupla (copia inmutable) de la posición anterior antes de mover.
    posicion = (0, 0)
    historial = Pila()

    historial.apilar(posicion)
    posicion = (5, 0)
    historial.apilar(posicion)
    posicion = (5, 4)

    posicion = historial.desapilar()
    assert posicion == (5, 0)
    posicion = historial.desapilar()
    assert posicion == (0, 0)


def test_desapilar_pila_vacia_sigue_una_regla_explicita_y_la_pila_sigue_usable():
    pila = Pila()
    with pytest.raises(PilaVaciaError):
        pila.desapilar()
    with pytest.raises(PilaVaciaError):
        pila.tope()
    pila.apilar(1)
    assert pila.desapilar() == 1
