from enum import Enum

class terrainTypes(Enum):
    Floor = 0
    Stone = 1
    Coal = 2
    Copper = 3
    Iron = 4
    Graphite = 5
    Manganese = 6
    Nickel = 7
    Silver = 8
    Uranium = 9
    Emberrite = 10

class Ore:
    def __init__(self, type, health, gold, pos, event_handler):
        from src.game import EventHandler
        self.type: terrainTypes = type
        self.max_health: int = health
        self.health: int = health
        self.gold: int = gold
        self.pos = pos
        self.event_handler: EventHandler = event_handler
        self.destroyed = False

    def take_damage(self, damage) -> str:
        self.health -= damage
        destroyed: str = self.check_status()
        return destroyed

    def check_status(self) -> str:
        if self.destroyed:
            return "Already Destroyed"
        if self.health <= 0:
            self.event_handler.call_tile_broken(self.pos, gold_amount=self.gold)
            self.destroyed = True
            return "Destroyed"
        return "Alive"