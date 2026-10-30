import pytest

from app.domain.scene import Scene, SceneFullError
from app.projects.world import MAX_OBJECTS


def obj(object_id, kind="wall", x=0, y=0):
    return {"id": object_id, "kind": kind, "x": x, "y": y}


def test_a_new_scene_is_empty():
    scene = Scene()
    assert len(scene) == 0 and scene.to_list() == []


def test_objects_keep_the_order_they_were_added():
    scene = Scene([obj("a"), obj("b"), obj("c")])
    assert [o["id"] for o in scene] == ["a", "b", "c"]


def test_find_returns_the_object_or_none():
    scene = Scene([obj("a"), obj("b", "coin")])
    assert scene.find("b")["kind"] == "coin" and scene.find("zzz") is None


def test_count_kind():
    scene = Scene([obj("a", "coin"), obj("b", "coin"), obj("c", "wall")])
    assert scene.count_kind("coin") == 2 and scene.count_kind("player") == 0


def test_unique_ids_are_detected():
    assert Scene([obj("a"), obj("b")]).has_unique_ids()
    assert not Scene([obj("a"), obj("a")]).has_unique_ids()


def test_free_id_adds_a_counter_when_the_id_is_taken():
    scene = Scene([obj("rock"), obj("rock-2")])
    assert scene.free_id("tree") == "tree" and scene.free_id("rock") == "rock-3"


def test_a_scene_cannot_pass_the_limit():
    scene = Scene(obj(str(i)) for i in range(MAX_OBJECTS))
    with pytest.raises(SceneFullError):
        scene.add(obj("one-too-many"))


def test_to_list_is_a_copy():
    scene = Scene([obj("a")])
    plain = scene.to_list()
    plain.clear()
    assert len(scene) == 1
