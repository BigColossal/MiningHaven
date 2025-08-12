import pygame as pg
import src.graphics as gfx

class GameSprites:
    def __init__(self, terrain, shadows, outlines, objects):
        self.terrain_tileset = terrain
        self.shadow_tileset = shadows
        self.outlines_tileset = outlines
        self.object_tileset = objects

    def get_terrain_tile(self, terrain):
        terrain_name = terrain.name if hasattr(terrain, "name") else str(terrain)
        return self.terrain_tileset.get(terrain_name)
    
    def get_outline_tile(self, direction):
        """
        Direction: Must be one of four (Up, Down, Left, Right)
        """
        return self.outlines_tileset.get(direction)
    
    def get_shadow_tile(self, direction):
        return self.shadow_tileset.get(direction)
    
    def get_object_tile(self, obj_name):
        return self.object_tileset.get(obj_name)


def extract_sprites() -> GameSprites:
    ore_sheet = pg.image.load("assets/sprites/ore_sprite_sheet.png").convert_alpha()
    shadow_sheet = pg.image.load("assets/sprites/shadow_sprite_sheet.png").convert_alpha()
    outline_sheet = pg.image.load("assets/sprites/outline_sprite_sheet.png").convert_alpha()
    object_sheet = pg.image.load("assets/sprites/object_sprite_sheet.png").convert_alpha()

    def get_tile(sheet, tile_size, x, y):
        width, height = tile_size, tile_size
        rect = pg.Rect(x * tile_size, y * tile_size, width, height)
        tile = pg.Surface((width, height), pg.SRCALPHA)
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
        "Up Left": get_tile(shadow_sheet, TILE_SIZE, 1, 1),
        "Up Right": get_tile(shadow_sheet, TILE_SIZE, 0, 1),
        "Down Left": get_tile(shadow_sheet, TILE_SIZE, 1, 0),
        "Down Right": get_tile(shadow_sheet, TILE_SIZE, 0, 0),
        "Right": get_tile(shadow_sheet, TILE_SIZE, 2, 0),
        "Left": get_tile(shadow_sheet, TILE_SIZE, 2, 1),
        "Up": get_tile(shadow_sheet, TILE_SIZE, 0, 2),
        "Down": get_tile(shadow_sheet, TILE_SIZE, 1, 2)
    }

    outline_tileset = {
        "Down": get_tile(outline_sheet, TILE_SIZE, 1, 1),
        "Up": get_tile(outline_sheet, TILE_SIZE, 0, 1),
        "Left": get_tile(outline_sheet, TILE_SIZE, 0, 0),
        "Right": get_tile(outline_sheet, TILE_SIZE, 1, 0)
    }

    object_tileset = {
        "Ladder": get_tile(object_sheet, TILE_SIZE, 0, 0)
    }

    return GameSprites(terrain_tileset, shadow_tileset, outline_tileset, object_tileset)