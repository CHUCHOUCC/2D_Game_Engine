"""Shared rules of the game world. The frontend and the AI service use the same values."""

WORLD_WIDTH = 1600
WORLD_HEIGHT = 960
TILE_SIZE = 32

# Kinds the editor can place. 'player' is the spawn point (at most one per scene).
OBJECT_KINDS = ("player", "box", "wall", "house", "tree", "spike", "coin", "enemy")
MAX_OBJECTS = 600
