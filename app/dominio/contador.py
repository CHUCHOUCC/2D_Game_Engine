from .evento import Evento


class ContadorPuntos:
    """Lleva el puntaje y aplica la regla de cada evento.

    Reglas: una moneda suma 10, un daño resta 5, el puntaje nunca baja de
    cero y un evento desconocido no cambia el estado.
    """

    TIPO_MONEDA = "moneda"
    TIPO_DANO = "daño"
    PUNTOS_MONEDA = 10
    PUNTOS_DANO = 5

    def __init__(self):
        self._puntaje = 0

    @property
    def puntaje(self):
        return self._puntaje

    def aplicar(self, evento: Evento):
        """Aplica un evento y devuelve un mensaje con el resultado."""
        if evento.tipo == self.TIPO_MONEDA:
            self._puntaje += self.PUNTOS_MONEDA
            return f"Moneda: puntaje {self._puntaje}"
        if evento.tipo == self.TIPO_DANO:
            self._puntaje = max(0, self._puntaje - self.PUNTOS_DANO)
            return f"Daño: puntaje {self._puntaje}"
        return f"Evento desconocido '{evento.tipo}': puntaje sin cambios ({self._puntaje})"
