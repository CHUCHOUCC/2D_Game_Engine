# Motor 2D · Backend (Python)

API en FastAPI. Por ahora solo tiene `GET /health` y las estructuras de datos propias (sin `list.append/pop`, `deque` ni `queue.Queue`).

## Ejecutar en local (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest            # pruebas
uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000/health, que debe responder `{"ok": true}`. La documentación automática está en `/docs`.

## Estructuras y ejercicios del plan

| Código | Ejercicio | Qué demuestra |
|---|---|---|
| `app/estructuras/pila.py` | 3, pila de posiciones | LIFO, tope, deshacer; O(1) |
| `app/estructuras/cola.py` | 4, cola de eventos | FIFO con frente y final; O(1) |
| `app/estructuras/arbol.py` | 5, árbol de expresión | recorrido en posorden; O(n) |
| `app/dominio/contador.py` | 1, contador de puntos | regla de cada evento |

Cada archivo documenta su invariante, sus costos y qué pasa con la estructura vacía.

## Despliegue (Render u otro servicio similar)

- Comando de arranque: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Dependencias: `requirements.txt`
- Las claves (`API_KEY`, `DATABASE_URL`) van como variables de entorno del servicio, nunca en el código.
