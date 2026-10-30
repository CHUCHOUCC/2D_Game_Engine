from app.projects.world import MAX_OBJECTS
from app.structures import DynamicArray


class SceneFullError(Exception):
    """Raised when adding an object would pass the limit of objects per scene."""


class Scene:
    """The objects of a project, kept in our own DynamicArray (no native list).

    Rules: at most MAX_OBJECTS objects, ids are unique, and a scene has at most
    one player. Each object is a dict with id, kind, x and y.
    Costs: add is O(1) amortised; looking an object up by id is O(n).
    """

    def __init__(self, objects=()):
        self._objects = DynamicArray()
        for obj in objects:
            self.add(obj)

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self):
        return iter(self._objects)

    def add(self, obj: dict) -> None:
        if len(self._objects) >= MAX_OBJECTS:
            raise SceneFullError(f"A scene can have at most {MAX_OBJECTS} objects")
        self._objects.append(obj)

    def find(self, object_id: str):
        """The object with that id, or None."""
        for obj in self._objects:
            if obj["id"] == object_id:
                return obj
        return None

    def count_kind(self, kind: str) -> int:
        total = 0
        for obj in self._objects:
            if obj["kind"] == kind:
                total += 1
        return total

    def has_unique_ids(self) -> bool:
        seen = set()
        for obj in self._objects:
            if obj["id"] in seen:
                return False
            seen.add(obj["id"])
        return True

    def free_id(self, wanted: str) -> str:
        """`wanted` if no object uses it, otherwise wanted-2, wanted-3, ..."""
        candidate, n = wanted, 1
        while self.find(candidate) is not None:
            n += 1
            candidate = f"{wanted}-{n}"
        return candidate

    def to_list(self) -> list:
        """The objects as a plain list, which is what the database and the JSON need."""
        return [obj for obj in self._objects]
