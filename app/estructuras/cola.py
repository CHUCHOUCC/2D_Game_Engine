from .nodo import Nodo


class ColaVaciaError(Exception):
    """Se intentó leer o retirar un elemento de una cola vacía."""


class Cola:
    """Cola FIFO enlazada: el primero en entrar es el primero en salir.

    Guarda referencias al frente (por donde se retira) y al final (por donde
    se inserta).
    Invariante: _frente y _final son ambos None (cola vacía) o ambos apuntan
    a nodos de la misma cadena, y _final.siguiente es None.
    Costos: encolar y desencolar son O(1); no se recorre la cadena porque se
    conserva la referencia al final.
    Regla para cola vacía: desencolar(), frente() y final() lanzan
    ColaVaciaError; se puede comprobar antes con esta_vacia().
    """

    def __init__(self):
        self._frente = None
        self._final = None

    def esta_vacia(self):
        return self._frente is None

    def encolar(self, dato):
        nuevo = Nodo(dato)
        if self._final is None:
            # Cola vacía: el nuevo nodo es a la vez frente y final.
            self._frente = nuevo
        else:
            self._final.siguiente = nuevo
        self._final = nuevo

    def desencolar(self):
        if self._frente is None:
            raise ColaVaciaError("No se puede desencolar: la cola está vacía")
        dato = self._frente.dato
        self._frente = self._frente.siguiente
        if self._frente is None:
            # Se retiró el último elemento: el final también debe quedar vacío.
            self._final = None
        return dato

    def frente(self):
        if self._frente is None:
            raise ColaVaciaError("No hay frente: la cola está vacía")
        return self._frente.dato

    def final(self):
        if self._final is None:
            raise ColaVaciaError("No hay final: la cola está vacía")
        return self._final.dato
