from dataclasses import dataclass


@dataclass(frozen=True)
class Evento:
    """Algo que ocurrió en el juego. 'origen' identifica de dónde vino (por ejemplo, moneda A)."""

    tipo: str
    origen: str = ""
