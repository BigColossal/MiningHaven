class UpgradesManager:
    def __init__(self, terrain, gold: int = 0, ore_luck: int = 1, ore_value: int = 1):
        from src.game import Miner, Terrain
        self.gold = gold
        self.ore_luck = ore_luck
        self.ore_value = ore_value
        self.miners: dict[int: Miner] = None
        self.terrain: Terrain = terrain
        self.miner_speed_click_increase = 0.1
        self.miner_speed_boost_limit = 5
        self.miner_speed_boost_decay = 0.15
        self.time_since_last_click = 0
        self.decay_rate = 0.025
        self.decay_rate_timer = self.decay_rate

    def increment_gold(self, amount):
        self.gold += amount

    def set_miners(self, miners):
        self.miners = miners

    def increment_ore_luck(self, amount):
        self.ore_luck *= amount
        self.terrain.ore_luck = self.ore_luck
        self.terrain.modify_chances_with_luck()

    def increment_ore_value(self, amount):
        self.ore_value *= amount
        self.terrain.ore_value_mult = self.ore_value
        self.terrain.create_ore_golds()

    def upgrade_miner_speed(self, id, amount):
        from src.game import Miner
        miner: Miner = self.miners[id]
        miner.movement_speed += amount

    def upgrade_pickaxe_strength(self, id, amount):
        from src.game import Miner
        miner: Miner = self.miners[id]
        miner.damage *= amount

    def upgrade_miner_pickaxe_speed(self, id, amount):
        from src.game import Miner
        miner: Miner = self.miners[id]
        miner.mine_cd -= amount

    def incre_global_miner_speed_mult(self):
        from src.game import Miner

        Miner.global_miner_speed_boost = min(Miner.global_miner_speed_boost + self.miner_speed_click_increase, self.miner_speed_boost_limit)
        self.time_since_last_click = 0
        for miner in self.miners:
            miner.set_boost()

    def incre_time_since_last(self, dt):
        self.time_since_last_click += dt

    def global_miner_speed_decay(self, dt):
        from src.game import Miner

        self.decay_rate_timer -= dt
        if self.decay_rate_timer <= 0 and Miner.global_miner_speed_boost != 1:
            Miner.global_miner_speed_boost = max(1, Miner.global_miner_speed_boost - self.miner_speed_boost_decay)
            self.decay_rate_timer = 0.1
            for miner in self.miners:
                miner.set_boost()

    