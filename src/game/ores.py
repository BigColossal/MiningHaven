from enum import Enum

class terrainTypes(Enum):
    Floor = 0
    Stone = 1
    Coal = 2
    Copper = 3
    Iron = 4

class Ore:
    def __init__(self, type, health, pos, event_handler):
        from src.game import EventHandler
        self.type: terrainTypes = type
        self.max_health: int = health
        self.health: int = health
        self.pos = pos
        self.event_handler: EventHandler = event_handler

    def take_damage(self, damage) -> bool:
        self.health -= damage
        destroyed: bool = self.check_status()
        return destroyed

    def check_status(self) -> bool:
        if self.health <= 0:
            self.event_handler.call_tile_broken(self.pos)
            return True
        return False

