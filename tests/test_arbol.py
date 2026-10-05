import pytest

from app.estructuras import ErrorExpresion, NodoNumero, NodoOperacion


def test_2_mas_3_por_4_es_20():
    suma = NodoOperacion("+", NodoNumero(2), NodoNumero(3))
    arbol = NodoOperacion("*", suma, NodoNumero(4))
    assert arbol.evaluar() == 20


def test_hoja_con_7_se_evalua_como_7():
    assert NodoNumero(7).evaluar() == 7


def test_operador_desconocido_se_rechaza_con_mensaje_identificable():
    arbol = NodoOperacion("^", NodoNumero(2), NodoNumero(3))
    with pytest.raises(ErrorExpresion, match="Operador desconocido"):
        arbol.evaluar()


def test_operacion_sin_los_hijos_necesarios_se_rechaza():
    arbol = NodoOperacion("+", NodoNumero(2), None)
    with pytest.raises(ErrorExpresion, match="necesita dos hijos"):
        arbol.evaluar()


def test_error_en_un_subarbol_se_propaga_hacia_arriba():
    interno = NodoOperacion("?", NodoNumero(1), NodoNumero(1))
    arbol = NodoOperacion("+", interno, NodoNumero(5))
    with pytest.raises(ErrorExpresion, match="Operador desconocido"):
        arbol.evaluar()


def test_division_por_cero_se_rechaza():
    arbol = NodoOperacion("/", NodoNumero(4), NodoNumero(0))
    with pytest.raises(ErrorExpresion, match="División por cero"):
        arbol.evaluar()


def test_hoja_con_texto_se_rechaza():
    with pytest.raises(ErrorExpresion):
        NodoNumero("7")
