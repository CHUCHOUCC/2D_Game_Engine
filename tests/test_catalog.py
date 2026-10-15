from fastapi.testclient import TestClient

from app.catalog.router import get_catalog
from app.main import app


class FakeCatalog:
    def character_lines(self):
        return [{"kind": "knight", "line": "Hola"}, {"kind": "knight", "line": "Adiós"}, {"kind": "wizard", "line": "Magia"}]


def test_character_lines_are_grouped_by_kind():
    app.dependency_overrides[get_catalog] = FakeCatalog
    try:
        body = TestClient(app).get("/catalog/characters").json()
    finally:
        app.dependency_overrides.clear()
    assert body == {"knight": ["Hola", "Adiós"], "wizard": ["Magia"]}
