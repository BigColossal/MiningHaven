import pygame as pg

ore_sheet = pg.image.load("./assets/ore_sprite_sheet.png").convert_alpha()
shadow_sheet = pg.image.load("./assets/ore_sprite_sheet.png").convert_alpha()
outline_sheet = pg.image.load("./assets/ore_sprite_sheet.png").convert_alpha()

def get_tile(sheet, tile_size, x, y):
    rect = pg.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
    tile = pg.Surface((tile_size, tile_size), pg.SRCALPHA)
    tile.blit(sheet, (0, 0), rect)
    return tile

TILE_SIZE = 128

terrain_tileset = {
    "floor": get_tile(ore_sheet, TILE_SIZE, 0, 0),
    "stone": get_tile(ore_sheet, TILE_SIZE, 1, 0),
    "coal": get_tile(ore_sheet, TILE_SIZE, 0, 1),
    "copper": get_tile(ore_sheet, TILE_SIZE, 1, 1),
    "iron": get_tile(ore_sheet, TILE_SIZE, 0, 2),
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
    "down": get_tile(outline_sheet, TILE_SIZE, 0, 0),
    "up": get_tile(outline_sheet, TILE_SIZE, 1, 1),
    "left": get_tile(outline_sheet, TILE_SIZE, 1, 0),
    "right": get_tile(outline_sheet, TILE_SIZE, 0, 1)
}