from .nodo import Nodo


class PilaVaciaError(Exception):
    """Se intentó leer o retirar un elemento de una pila vacía."""


class Pila:
    """Pila LIFO con nodos enlazados: el último en entrar es el primero en salir.

    Invariante: _tope es None si y solo si la pila está vacía.
    Costos: apilar, desapilar, tope y esta_vacia son O(1), porque solo se
    toca el nodo del tope y nunca se recorre la cadena.
    Regla para pila vacía: desapilar() y tope() lanzan PilaVaciaError;
    quien llama puede comprobarlo antes con esta_vacia().
    """

    def __init__(self):
        self._tope = None

    def esta_vacia(self):
        return self._tope is None

    def apilar(self, dato):
        # El nuevo nodo apunta al tope anterior y pasa a ser el tope.
        self._tope = Nodo(dato, self._tope)

    def desapilar(self):
        if self._tope is None:
            raise PilaVaciaError("No se puede desapilar: la pila está vacía")
        dato = self._tope.dato
        self._tope = self._tope.siguiente
        return dato

    def tope(self):
        if self._tope is None:
            raise PilaVaciaError("No hay tope: la pila está vacía")
        return self._tope.dato
