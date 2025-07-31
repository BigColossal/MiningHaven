import pygame as pg
import src.graphics as gfx

class GameSurface:
    def __init__(self):
        self.surface = pg.Surface((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT), pg.SRCALPHA)
        self.dirty = True
        self.off_x, self.off_y = None, None

    def draw(self, data):
        pass

    def update(self, data):
        pass

class TerrainSurface(GameSurface):
    from src.game import Terrain
    def __init__(self):
        super().__init__()
        self._terrain = None

    def set_terrain(self, terrain: Terrain):
        self._terrain = terrain

    def update(self, game_sprites: gfx.GameSprites, coord: tuple[int, int] = None, full_screen: bool = False, 
               offsets: tuple[float, float] = None):
        
        if full_screen:
            # if the whole screen, as in the camera was moved or if the cave got restarted, itll run 
            # and set new offset coords while updating everything
            self.off_x, self.off_y = offsets
            for y in range(self._terrain.grid_size):
                for x in range(self._terrain.grid_size):
                    self.get_and_update_tile(x, y, game_sprites)
        else:
            # if full_screen wasn't True, itll only update whatever individual coord was selected in the 
            # function call
            x, y = coord
            self.get_and_update_tile(x, y, game_sprites)

    def get_and_update_tile(self, x: int, y: int, game_sprites: gfx.GameSprites):
        tile = game_sprites.get_terrain_tile(self._terrain.data[y][x])
        self.surface.blit(tile, (self.off_x + x * gfx.TILE_SIZE, self.off_y + y * gfx.TILE_SIZE))





