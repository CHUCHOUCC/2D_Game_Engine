from app.structures.general_tree import Tree


def sample():
    """world -> (solid -> (wall, house), hazard -> (spikes), coin)"""
    tree = Tree("world")
    solid = tree.root.add_child("solid")
    solid.add_child("wall")
    solid.add_child("house")
    tree.root.add_child("hazard").add_child("spikes")
    tree.root.add_child("coin")
    return tree


def test_preorder_goes_deep_first():
    assert list(sample().preorder()) == ["world", "solid", "wall", "house", "hazard", "spikes", "coin"]


def test_level_order_goes_level_by_level():
    assert list(sample().level_order()) == ["world", "solid", "hazard", "coin", "wall", "house", "spikes"]


def test_size_and_height():
    tree = sample()
    assert tree.size() == 7 and tree.height() == 2


def test_a_lone_root():
    tree = Tree("root")
    assert list(tree.preorder()) == ["root"] and tree.size() == 1 and tree.height() == 0


def test_find_returns_the_first_match_in_preorder():
    assert sample().find(lambda v: v.startswith("h")) == "house"
    assert sample().find(lambda v: v == "dragon") is None


def test_a_very_deep_tree_does_not_hit_the_recursion_limit():
    tree = Tree(0)
    node = tree.root
    for depth in range(1, 5000):
        node = node.add_child(depth)
    assert tree.size() == 5000 and tree.height() == 4999
    assert sum(1 for _ in tree.preorder()) == 5000
