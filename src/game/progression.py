class UpgradesManager:
    def __init__(self, terrain, gold: int = 0, ore_luck: int = 1, ore_value: int = 1):
        from src.game import Miner, Terrain
        self.gold = gold
        self.ore_luck = ore_luck
        self.ore_value = ore_value
        self.miners: dict[int: Miner] = None
        self.terrain: Terrain = terrain

    def increment_gold(self, amount):
        self.gold += amount

    def increment_ore_luck(self, amount):
        self.ore_luck *= amount
        self.terrain.ore_luck = self.ore_luck
        self.terrain.modify_chances_with_luck()

    def increment_ore_value(self, amount):
        self.ore_value *= amount
        self.terrain.ore_value_mult = self.ore_value
        self.terrain.create_ore_golds()

    def upgrade_miner_speed(self, id, amount):
        miner = self.miners[id]
        miner.movement_speed += amount

    def upgrade_pickaxe_strength(self, id, amount):
        miner = self.miners[id]
        miner.damage *= amount

    def upgrade_miner_pickaxe_speed(self, id, amount):
        miner = self.miners[id]
        miner.mine_cd -= amount

    