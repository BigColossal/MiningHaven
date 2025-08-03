import pygame as pg
from enum import Enum

class GameEvents(Enum):
    TILE_BROKEN = pg.USEREVENT + 1

class EventHandler:
    def __init__(self, graphics_engine, terrain):
        self.events = GameEvents
        self.graphics_engine = graphics_engine
        self.terrain = terrain

    def handle_mouse_click(self, mouse_pos: tuple[int, int]):
        import src.graphics as gfx
        # Convert screen coords to grid coords
        mouse_x, mouse_y = mouse_pos
        tile_x = int((mouse_x + self.graphics_engine.offset_x) // gfx.TILE_SIZE)
        tile_y = int((mouse_y + self.graphics_engine.offset_y) // gfx.TILE_SIZE)
        coord_broken = (tile_x, tile_y)

        # Bounds check
        if 0 <= tile_x < self.terrain.grid_size and 0 <= tile_y < self.terrain.grid_size:
            from src.game import terrainTypes
            if self.terrain.data[tile_y][tile_x] != terrainTypes.Floor:
                self.call_tile_broken([coord_broken])

    def call_tile_broken(self, coords, new_grid=None, initialization=False):
        pg.event.post(pg.event.Event(GameEvents.TILE_BROKEN.value, {'positions': coords, 'new_grid': new_grid,
                                                                    "initialization": initialization}))

    


