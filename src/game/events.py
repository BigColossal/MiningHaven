import pygame as pg
from enum import Enum

class GameEvents(Enum):
    """
    Defines custom game-specific event types used for triggering gameplay actions
    via the pygame event queue.

    Events:
        TILE_BROKEN: Signals that terrain tiles have transitioned to a walkable state.
        SCREEN_DARKENING: Indicates a visual transition to a darker screen (e.g. entering cave).
        SCREEN_LIGHTENING: Signals a return to brighter visuals (e.g. exiting cave).
        CAVE_CLEARED: Marks a cave as cleared or completed, potentially tied to gameplay progress.
    """
    TILE_BROKEN = pg.USEREVENT + 1
    SCREEN_DARKENING = pg.USEREVENT + 2
    SCREEN_LIGHTENING = pg.USEREVENT + 3
    CAVE_CLEARED = pg.USEREVENT + 4

class EventHandler:
    def __init__(self, graphics_engine, terrain):
        self.events = GameEvents
        self.graphics_engine = graphics_engine
        self.terrain = terrain

    def handle_mouse_click(self, mouse_pos: tuple[int, int]):
        """
        Handles a mouse click by determining the clicked tile and triggering terrain modification
        if the tile is not already walkable.

        Converts screen coordinates to grid coordinates using rendering offsets and tile size,
        then checks whether the clicked tile is within bounds and not yet marked as Floor.
        If valid, emits an event to break the tile.

        Parameters:
            mouse_pos (tuple[int, int]): The x and y screen position of the mouse click.
        """

        import src.graphics as gfx

        # Convert screen coordinates to grid coordinates
        mouse_x, mouse_y = mouse_pos
        tile_x = int((mouse_x + self.graphics_engine.offset_x) // gfx.TILE_SIZE)
        tile_y = int((mouse_y + self.graphics_engine.offset_y) // gfx.TILE_SIZE)
        coord_broken = (tile_x, tile_y)

        # Ensure the clicked tile is within terrain bounds
        if 0 <= tile_x < self.terrain.grid_size and 0 <= tile_y < self.terrain.grid_size:
            from src.game import terrainTypes

            # Trigger tile break if it's not already walkable
            if self.terrain.data[tile_y][tile_x].type != terrainTypes.Floor:
                self.terrain.data[tile_y][tile_x].take_damage(100)

    def call_tile_broken(self, coords, new_grid=None, initialization=False):
        if isinstance(coords, tuple):
            coords = [coords]
        pg.event.post(pg.event.Event(GameEvents.TILE_BROKEN.value, {'positions': coords, 'new_grid': new_grid,
                                                                    "initialization": initialization}))
        
    def call_cave_cleared(self):
        pg.event.post(pg.event.Event(GameEvents.CAVE_CLEARED.value))
        pg.event.post(pg.event.Event(GameEvents.SCREEN_LIGHTENING.value))

    def call_darkening_screen(self):
        pg.event.post(pg.event.Event(GameEvents.SCREEN_DARKENING.value))

    


