import pygame as pg
import src.graphics as gfx

class GameSprites:
    def __init__(self, terrain, shadows, outlines):
        self.terrain_tileset = terrain
        self.shadow_tileset = shadows
        self.outlines_tileset = outlines

    def get_terrain_tile(self, terrain):
        terrain_name = terrain.name if hasattr(terrain, "name") else str(terrain)
        return self.terrain_tileset.get(terrain_name)
    
    def get_outline_tile(self, direction):
        """
        Direction: Must be one of four (Up, Down, Left, Right)
        """
        return self.outlines_tileset.get(direction)


def extract_sprites() -> GameSprites:
    ore_sheet = pg.image.load("assets/sprites/ore_sprite_sheet.png")
    shadow_sheet = pg.image.load("assets/sprites/ore_sprite_sheet.png")
    outline_sheet = pg.image.load("assets/sprites/ore_sprite_sheet.png")

    def get_tile(sheet, tile_size, x, y):
        rect = pg.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
        tile = pg.Surface((tile_size, tile_size), pg.SRCALPHA)
        tile.blit(sheet, (0, 0), rect)
        scaled_tile = pg.transform.scale(tile, (gfx.TILE_SIZE, gfx.TILE_SIZE))
        return scaled_tile

    TILE_SIZE = 128

    terrain_tileset = {
        "Floor": get_tile(ore_sheet, TILE_SIZE, 0, 0),
        "Stone": get_tile(ore_sheet, TILE_SIZE, 1, 0),
        "Copper": get_tile(ore_sheet, TILE_SIZE, 0, 1),
        "Iron": get_tile(ore_sheet, TILE_SIZE, 1, 1),
        "Coal": get_tile(ore_sheet, TILE_SIZE, 0, 2),
    }

    shadow_tileset = {
        "top left": get_tile(shadow_sheet, TILE_SIZE, 0, 0),
        "top right": get_tile(shadow_sheet, TILE_SIZE, 1, 0),
        "bottom left": get_tile(shadow_sheet, TILE_SIZE, 0, 1),
        "bottom right": get_tile(shadow_sheet, TILE_SIZE, 1, 1),
        "right": get_tile(shadow_sheet, TILE_SIZE, 2, 0),
        "left": get_tile(shadow_sheet, TILE_SIZE, 2, 1),
        "up": get_tile(shadow_sheet, TILE_SIZE, 0, 2),
        "down": get_tile(shadow_sheet, TILE_SIZE, 1, 2)
    }

    outline_tileset = {
        "Down": get_tile(outline_sheet, TILE_SIZE, 0, 0),
        "Up": get_tile(outline_sheet, TILE_SIZE, 1, 1),
        "Left": get_tile(outline_sheet, TILE_SIZE, 1, 0),
        "Right": get_tile(outline_sheet, TILE_SIZE, 0, 1)
    }
    return GameSprites(terrain_tileset, shadow_tileset, outline_tileset)