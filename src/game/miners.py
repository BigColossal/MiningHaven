import pygame as pg

class Miner():
    miner_amount = 0
    def __init__(self, terrain):
        from src.game import Terrain
        Miner.miner_amount += 1
        self.id = Miner.miner_amount
        self.pos = None
        self._terrain: Terrain = terrain

    def spawn_miner(self):
        cave_mid = (self._terrain.middle - 1, self._terrain.middle - 1)
        self.pos = cave_mid

