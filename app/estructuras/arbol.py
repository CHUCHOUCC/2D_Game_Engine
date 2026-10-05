from abc import ABC, abstractmethod


class ErrorExpresion(Exception):
    """La expresión es inválida: operador desconocido, hijo faltante o error de cálculo."""


class NodoExpresion(ABC):
    """Nodo de un árbol de expresión. Cada tipo de nodo sabe evaluarse (polimorfismo)."""

    @abstractmethod
    def evaluar(self):
        """Devuelve el valor numérico del subárbol que cuelga de este nodo."""


class NodoNumero(NodoExpresion):
    """Hoja: caso base de la recursión, se evalúa como su propio valor."""

    def __init__(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ErrorExpresion(f"El valor de una hoja debe ser numérico, no {valor!r}")
        self.valor = valor

    def evaluar(self):
        return self.valor


class NodoOperacion(NodoExpresion):
    """Nodo interno: combina los resultados de sus dos hijos con un operador.

    Se evalúa en posorden: primero el hijo izquierdo, luego el derecho y por
    último la operación del padre. Recorrer todo el árbol visita cada nodo
    una vez, por eso cuesta O(n).
    Regla ante errores: un operador desconocido o un hijo faltante lanza
    ErrorExpresion con un mensaje identificable, antes de calcular nada.
    """

    OPERADORES_VALIDOS = ("+", "-", "*", "/")

    def __init__(self, operador, izquierdo=None, derecho=None):
        self.operador = operador
        self.izquierdo = izquierdo
        self.derecho = derecho

    def evaluar(self):
        if self.operador not in self.OPERADORES_VALIDOS:
            raise ErrorExpresion(f"Operador desconocido: '{self.operador}'")
        if self.izquierdo is None or self.derecho is None:
            raise ErrorExpresion(f"La operación '{self.operador}' necesita dos hijos")

        a = self.izquierdo.evaluar()
        b = self.derecho.evaluar()

        if self.operador == "+":
            return a + b
        if self.operador == "-":
            return a - b
        if self.operador == "*":
            return a * b
        if b == 0:
            raise ErrorExpresion("División por cero")
        return a / b
