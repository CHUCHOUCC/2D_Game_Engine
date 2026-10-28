"""Shared rules of the game world. The frontend and the AI service use the same values."""

WORLD_WIDTH = 1600
WORLD_HEIGHT = 960
TILE_SIZE = 32

# Kinds the editor can place. 'player' is the spawn point (at most one per scene).
OBJECT_KINDS = (
    "player", "box", "wall", "house", "tree", "spike", "coin", "enemy", "villager", "knight", "wizard",
    # more enemies
    "bat", "spider", "ghost", "brute",
    # items: a chest drops one of the others when opened
    "chest", "potion", "sword", "axe", "wand", "bow",
    # more obstacles
    "barrel", "fence", "bush",
)
ENEMY_KINDS = ("enemy", "bat", "spider", "ghost", "brute")
ITEM_KINDS = ("chest", "potion", "sword", "axe", "wand", "bow")
# 2D characters: friendly people that walk around and talk to the player.
CHARACTER_KINDS = ("villager", "knight", "wizard")
MAX_OBJECTS = 600

# Points the game gives for each coin and for defeating each kind of enemy.
# Same values as the frontend (ScoreCounter.ts and combat.ts): the backend uses
# them to reject runs that claim more points than the level can give.
COIN_POINTS = 1
ENEMY_POINTS = {"enemy": 5, "bat": 3, "spider": 4, "ghost": 6, "brute": 15}
