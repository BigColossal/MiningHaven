import pygame as pg
import src.graphics as gfx
from src.game import Terrain

class RenderManager:
    def __init__(self, terrain: Terrain):
        self._screen = pg.display.set_mode((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT))
        #self._dynamic_screen = pg.Surface((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT))
        pg.display.set_caption("Mining Mayhem")

        self._GAME_SPRITES = gfx.extract_sprites()
        self._terrain = terrain
        self.grid_size = self._terrain.grid_size
        self._cave_surface: gfx.CaveSurface = self._terrain._cave_surface
        self._miner_surface: gfx.MinerSurface = self._terrain._miner_surface
        self._ui_surface: gfx.UISurface = self._terrain._ui_surface
        self._special_gfx_surface: gfx.SpecialEffectSurface = self._terrain._special_gfx_surface
        self.surfaces = [self._cave_surface, self._miner_surface, self._ui_surface, self._terrain._special_gfx_surface]
        self._cave_surface.set_game_sprites(self._GAME_SPRITES)

        self.map_height, self.map_width = None, None
        self.offset_x, self.offset_y = None, None
        self.dirty = True

        self.set_map_dimensions()
        self.set_initial_offset()
        self.darkening = False
        self.lightening = False
        self.dark_alpha = 0
        self.lighten_buffer_duration = 1500

        self._text_handler: gfx.TextHandler = gfx.TextHandler()

        self.MIN_OFFSET = -gfx.TILE_SIZE * gfx.PADDING
        self.MAX_OFFSET_Y = self.map_height - gfx.SCREEN_HEIGHT + (gfx.PADDING * gfx.TILE_SIZE)
        self.MAX_OFFSET_X = self.map_width - gfx.SCREEN_WIDTH + (gfx.PADDING * gfx.TILE_SIZE)

        self._visible_rect = pg.Rect(0, 0, gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT)
        self._shadow_visible_rect = pg.Rect(0, 0, gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT)
        self._visible_terrain = set()

        self.cave_hidden = False
        self.miner_ui_visible = False
        self.ui_switch_cooloff_cd = 0.35
        self.miner_switch_timer = 0

    def set_renderer_to_surfaces(self):
        for surface in self.surfaces:
            surface.set_dynamic_screen(self._screen)

    def set_map_dimensions(self):
        total_pixels = self.grid_size * gfx.TILE_SIZE
        self.map_height, self.map_width = total_pixels, total_pixels

    def set_initial_offset(self): # to start the game at the center of the cave
        self.offset_x = -(gfx.SCREEN_WIDTH - self.map_width) // 2
        self.offset_y = -(gfx.SCREEN_HEIGHT - self.map_height) // 2

    def load_new_cave(self): # for drawing brand new caves
        self._cave_surface.set_objects()
        self._miner_surface.update_miner_amount()
        for surface in self.surfaces:
            surface.load_new()

    def check_miner_pos(self):
        miners_changed = False
        for miner in self._terrain._miners:
            id = miner.id
            if miner.pos != self._miner_surface.miner_positions[id]:
                miners_changed = True
                break
        if miners_changed:
            self._miner_surface.update_static()
            self._miner_surface.update_pos()
            self.dirty = True


    def fill(self, color): # fill background
        self._screen.fill(color)

    def render(self, dt, fps):
        self.miner_switch_timer -= dt
        if self._special_gfx_surface.fire_tiles:
            self._special_gfx_surface.animate_fire(dt, updating=True)
        if self._special_gfx_surface.electricity_tiles:
            self._special_gfx_surface.animate_electricity(dt, updating=True)

        if self.dirty or self.darkening or self.lightening:
            self._ui_surface.get_fps(fps)
            self._ui_surface.update_UI(dt)
            self.fill(gfx.BG_COLOR)

            self.update_visible_rects()
            surfaces = self.select_surfaces()
            
            self._screen.blits(surfaces)
            if self.darkening:
                self.darken_screen(dt)
            elif self.lightening:
                self.lighten_screen(dt)
            pg.display.flip()
        self.dirty = False

    def select_surfaces(self):
        surfaces = []
        if not self.cave_hidden:
            surfaces.append((self._cave_surface.static_surface, (0, 0), self._shadow_visible_rect))
            surfaces.append((self._special_gfx_surface.static_surface, (0, 0), self._visible_rect))
            surfaces.append((self._miner_surface.static_surface, (0, 0), self._visible_rect))
        surfaces.append((self._ui_surface.static_surface, (0, 0)))
        return surfaces


    def break_terrain(self, coord: tuple[int, int]):
        # updates the broken terrain and its surroundings
        self.dirty = True
        x, y = coord
        coords_to_check = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), 
                            (x - 1, y - 1), (x - 1, y + 1), (x + 1, y + 1), (x + 1, y -1)]
        
        self._cave_surface.update_darkness((x, y), darken=False)
        self._cave_surface.update_terrain_tile(coord)
        self._cave_surface.update_object(coord)
        self._cave_surface.update_tile_edges(coord)
        for coord in coords_to_check:
            x, y = coord
            if (x >= 0 and x < self.grid_size) and (y >= 0 and y < self.grid_size):
                type = self._terrain.data[y][x].type
                if type != self._terrain.terrain_types.Floor and coord not in self._cave_surface.ores_damaged:
                    self._cave_surface.update_darkness((x, y), darken=False)
                    self._cave_surface.update_terrain_tile(coord)

    def update_visible_rects(self):
        self._visible_rect.topleft = (self.offset_x, self.offset_y)

        self._shadow_visible_rect.topleft = (self.offset_x - gfx.SHADOW_OFFSET[0], self.offset_y - gfx.SHADOW_OFFSET[1])

    def update_healthbars(self, dt):
        if self._terrain.ores_damaged:
            self.dirty = True
            for coord, info in self._terrain.ores_damaged.items():
                health_percent, timer = info
                timer -= dt
                self._terrain.ores_damaged[coord] = (health_percent, timer)
                self._cave_surface.update_ore_health(coord, health_percent, timer)

                

    def move_camera(self, keys):
        move_x = 0
        move_y = 0

        if keys[pg.K_a]:
            move_x -= 1
        if keys[pg.K_d]:
            move_x += 1
        if keys[pg.K_w]:
            move_y -= 1
        if keys[pg.K_s]:
            move_y += 1

        # Normalize vector if moving diagonally
        if move_x != 0 and move_y != 0:
            norm = gfx.CAMERA_MOVEMENT_SPEED / (2 ** 0.5)  # ≈ 0.707
        else:
            norm = gfx.CAMERA_MOVEMENT_SPEED

        self.offset_x += int(move_x * norm)
        self.offset_y += int(move_y * norm)

        self.offset_x = max(self.MIN_OFFSET, min(self.offset_x, self.MAX_OFFSET_X))
        self.offset_y = max(self.MIN_OFFSET, min(self.offset_y, self.MAX_OFFSET_Y))
        
        self.dirty = True

    def darken_screen(self, dt):
        self.dirty = True
        # Fade speed: pixels per second
        fade_rate = 300  # Increase for faster fade
        self.dark_alpha = min(self.dark_alpha + fade_rate * (dt), 255)

        fade_surface = pg.Surface(self._screen.get_size())
        fade_surface.set_alpha(int(self.dark_alpha))
        fade_surface.fill((0, 0, 0))
        self._screen.blit(fade_surface, (0, 0))

        if self.dark_alpha >= 255:
            self.darkening = False
            self._terrain._event_handler.call_cave_cleared()

    def lighten_screen(self, dt):
        # Only start buffer when darkening stops
        self.dirty = True
        if not hasattr(self, 'lighten_buffer_time'):
            self.lighten_buffer_time = 0

        if self.lighten_buffer_time < self.lighten_buffer_duration:
            self.lighten_buffer_time += dt * 1000
            fade_surface = pg.Surface(self._screen.get_size())
            self.dark_alpha = 255
            fade_surface.fill((0, 0, 0))  # Full black during buffer
            self._screen.blit(fade_surface, (0, 0))
            return
        # Fade out begins after buffer
        fade_rate = 300
        self.dark_alpha = max(self.dark_alpha - fade_rate * (dt), 0)

        fade_surface = pg.Surface(self._screen.get_size())
        fade_surface.set_alpha(int(self.dark_alpha))
        fade_surface.fill((0, 0, 0))
        self._screen.blit(fade_surface, (0, 0))

        if self.dark_alpha <= 0:
            self.lightening = False
            self.lighten_buffer_time = 0  # Reset for future use

    def switch_to_miner_UI(self):
        if self.miner_switch_timer <= 0:
            if not self.miner_ui_visible:
                self.cave_hidden = True
                self.miner_ui_visible = True
                self._ui_surface.load_miner_UI()
            else: 
                self.miner_ui_visible = False
                self.cave_hidden = False
                self._ui_surface.load_cave_UI()
            self.miner_switch_timer = self.ui_switch_cooloff_cd

    def handle_mouse_hover(self, pos):
        mouse_x, mouse_y = pos
        tile_x = int((mouse_x + self.offset_x) // gfx.TILE_SIZE)
        tile_y = int((mouse_y + self.offset_y) // gfx.TILE_SIZE)

        if 0 <= tile_x < self._terrain.grid_size and 0 <= tile_y < self._terrain.grid_size:
                ore = self._terrain.data[tile_y][tile_x]
                if ore.type != self._terrain.terrain_types.Floor and (tile_x, tile_y) in self._terrain.visible_tiles and \
                    self._ui_surface.ore_hover_active:
                        self._ui_surface.update_ore_panel(pos, ore)
                else:
                    self._ui_surface.erase_ore_panel()







        