class Nodo:
    """Nodo enlazado: guarda un dato y la referencia al nodo siguiente."""

    def __init__(self, dato, siguiente=None):
        self.dato = dato
        self.siguiente = siguiente
