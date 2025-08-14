import pygame as pg
import src.graphics as gfx

class GameSprites:
    def __init__(self, terrain, shadows, outlines, objects, surrounding_shadows):
        self.terrain_tileset = terrain
        self.shadow_tileset = shadows
        self.outlines_tileset = outlines
        self.object_tileset = objects
        self.surrounding_shadows_tileset = surrounding_shadows

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
    
    def get_surrounding_shadow_tile(self, direction):
        return self.surrounding_shadows_tileset.get(direction)


def extract_sprites(use_smooth_for_surrounding=False) -> GameSprites:
    # load sheets once (keep per-pixel alpha)
    ore_sheet = pg.image.load("assets/sprites/ore_sprite_sheet.png").convert_alpha()
    shadow_sheet = pg.image.load("assets/sprites/shadow_sprite_sheet.png").convert_alpha()
    outline_sheet = pg.image.load("assets/sprites/outline_sprite_sheet.png").convert_alpha()
    object_sheet = pg.image.load("assets/sprites/object_sprite_sheet.png").convert_alpha()

    # locals for speed
    _Rect = pg.Rect
    _subsurface = lambda s, r: s.subsurface(r).copy()  # copy so returned surface is independent
    _scale = pg.transform.scale
    _smoothscale = pg.transform.smoothscale
    _convert = lambda surf: surf.convert()
    _convert_alpha = lambda surf: surf.convert_alpha()

    SRC_TILE = 128
    TARGET = gfx.TILE_SIZE
    TARGET_2X = TARGET * 2

    # cache to avoid re-extracting / re-scaling same tiles
    tile_cache = {}

    def get_tile(sheet, src_tile_size, x, y, target_px, smooth=False):
        """Return a converted, scaled tile surface. Cached by (sheet id, x, y, target_px, smooth)."""
        key = (id(sheet), x, y, target_px, smooth)
        if key in tile_cache:
            return tile_cache[key]

        rect = _Rect(x * src_tile_size, y * src_tile_size, src_tile_size, src_tile_size)
        # use subsurface + copy (fast) instead of creating a fresh SRCALPHA surface then blitting into it
        tile = _subsurface(sheet, rect)

        if tile.get_width() != target_px or tile.get_height() != target_px:
            # choose faster scale by default, optionally smoothscale for higher quality
            if smooth:
                tile = _smoothscale(tile, (target_px, target_px))
            else:
                tile = _scale(tile, (target_px, target_px))

        # convert once to display-friendly per-pixel-alpha surface
        tile = _convert_alpha(tile)
        tile_cache[key] = tile
        return tile

    # Build tilesets — cache ensures duplicates reused automatically
    terrain_tileset = {
        "Floor": get_tile(ore_sheet, SRC_TILE, 0, 0, TARGET),
        "Stone": get_tile(ore_sheet, SRC_TILE, 1, 0, TARGET),
        "Copper": get_tile(ore_sheet, SRC_TILE, 0, 1, TARGET),
        "Iron": get_tile(ore_sheet, SRC_TILE, 1, 1, TARGET),
        "Coal": get_tile(ore_sheet, SRC_TILE, 0, 2, TARGET),
    }

    shadow_tileset = {
        "Up Left": get_tile(shadow_sheet, SRC_TILE, 1, 1, TARGET),
        "Up Right": get_tile(shadow_sheet, SRC_TILE, 0, 1, TARGET),
        "Down Left": get_tile(shadow_sheet, SRC_TILE, 1, 0, TARGET),
        "Down Right": get_tile(shadow_sheet, SRC_TILE, 0, 0, TARGET),
        "Right": get_tile(shadow_sheet, SRC_TILE, 2, 0, TARGET),
        "Left": get_tile(shadow_sheet, SRC_TILE, 2, 1, TARGET),
        "Up": get_tile(shadow_sheet, SRC_TILE, 0, 2, TARGET),
        "Down": get_tile(shadow_sheet, SRC_TILE, 1, 2, TARGET),
    }

    # surrounding shadows are just scaled versions of the same source tiles — reuse get_tile with target_px*2
    surrounding_shadows_tileset = {
        "Up Left": get_tile(shadow_sheet, SRC_TILE, 1, 1, TARGET_2X, smooth=use_smooth_for_surrounding),
        "Up Right": get_tile(shadow_sheet, SRC_TILE, 0, 1, TARGET_2X, smooth=use_smooth_for_surrounding),
        "Down Left": get_tile(shadow_sheet, SRC_TILE, 1, 0, TARGET_2X, smooth=use_smooth_for_surrounding),
        "Down Right": get_tile(shadow_sheet, SRC_TILE, 0, 0, TARGET_2X, smooth=use_smooth_for_surrounding),
        "Right": get_tile(shadow_sheet, SRC_TILE, 2, 0, TARGET_2X, smooth=use_smooth_for_surrounding),
        "Left": get_tile(shadow_sheet, SRC_TILE, 2, 1, TARGET_2X, smooth=use_smooth_for_surrounding),
        "Up": get_tile(shadow_sheet, SRC_TILE, 0, 2, TARGET_2X, smooth=use_smooth_for_surrounding),
        "Down": get_tile(shadow_sheet, SRC_TILE, 1, 2, TARGET_2X, smooth=use_smooth_for_surrounding),
    }

    outline_tileset = {
        "Down": get_tile(outline_sheet, SRC_TILE, 1, 1, TARGET),
        "Up": get_tile(outline_sheet, SRC_TILE, 0, 1, TARGET),
        "Left": get_tile(outline_sheet, SRC_TILE, 0, 0, TARGET),
        "Right": get_tile(outline_sheet, SRC_TILE, 1, 0, TARGET),
    }

    object_tileset = {
        "Ladder": get_tile(object_sheet, SRC_TILE, 0, 0, TARGET),
    }

    return GameSprites(terrain_tileset, shadow_tileset, outline_tileset,
                       object_tileset, surrounding_shadows_tileset)
