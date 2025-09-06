import pygame as pg
import src.graphics as gfx

class GameSurface:
    from src.game import Terrain
    def __init__(self):
        self.dynamic_surface = None
        self.static_surface = None
        self.off_x, self.off_y = None, None
        self._terrain = None

    def set_terrain(self, terrain: Terrain):
        self._terrain = terrain

    def set_dynamic_screen(self, screen):
        self.dynamic_surface = screen

    def create_static_surface(self):
        # Create new surface (static surfaces used for non moving tiles, such as terrain, shadows, outlines, UI, etc)
        grid_pixels = self._terrain.grid_size * gfx.TILE_SIZE
        self.static_surface = pg.Surface((grid_pixels, grid_pixels), pg.SRCALPHA).convert_alpha()

class CaveSurface(GameSurface):
    def __init__(self):
        super().__init__()
        self._tmp_tile = self._tmp_tile = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)
        self.padding = gfx.SHADOW_PADDING
        self.dark_tile = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)
        self.dark_tile.fill((1, 1, 1, 255))

        from src.game import GameObject
        self.objects: dict[tuple[int, int]: GameObject] = {}
        self.ores_damaged: set[tuple[int, int]] = set()
        self.game_sprites: gfx.GameSprites = None

    def set_game_sprites(self, game_sprites: gfx.GameSprites):
        self.game_sprites = game_sprites

    def set_objects(self):
        self.objects = self._terrain._objects

    def update_tile_edges(self, coord: tuple[int, int]):
        x, y = coord
        directions = []
        if coord in self._terrain.edge_map:
            directions = self._terrain.edge_map[coord]

        surrounding_floor, shadow_surf = self.create_shadow_surf(directions, coord)
        self.static_surface.blit(shadow_surf, ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE))

        outl_surf = self.create_outline_surf(directions)
        self.static_surface.blit(outl_surf, ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE))

        direction_coords = {
            "Up": (x, y - 1), "Down": (x, y + 1),
            "Right": (x + 1, y), "Left": (x - 1, y),
            "Up Right": (x + 1, y - 1), "Up Left": (x - 1, y - 1),
            "Down Right": (x + 1, y + 1), "Down Left": (x - 1, y + 1)
        }
        for direction in surrounding_floor: # for all adjacent tiles that are floor
            neighbor_floor_pos = direction_coords[direction]
            neigh_x, neigh_y = neighbor_floor_pos

            neighbor_directions = None
            if neighbor_floor_pos in self._terrain.edge_map:
                neighbor_directions = self._terrain.edge_map[neighbor_floor_pos]

            self.static_surface.fill((0, 0, 0, 0), ((neigh_x + self.padding) * gfx.TILE_SIZE, (neigh_y + self.padding) * gfx.TILE_SIZE, 
                                              gfx.TILE_SIZE, gfx.TILE_SIZE)) # clear out neighbor tile as to update the outlines there
            
            self.update_terrain_tile(neighbor_floor_pos)
            self.update_object(neighbor_floor_pos)
            
            _, neighbor_surf = self.create_shadow_surf(neighbor_directions, neighbor_floor_pos)
            self.static_surface.blit(neighbor_surf, ((neigh_x + self.padding) * gfx.TILE_SIZE, (neigh_y + self.padding) * gfx.TILE_SIZE))
            if neighbor_directions:
                neighbor_surf = self.create_outline_surf(neighbor_directions)
                self.static_surface.blit(neighbor_surf, ((neigh_x + self.padding) * gfx.TILE_SIZE, (neigh_y + self.padding) * gfx.TILE_SIZE))

    def update_terrain_tile(self, coord: tuple[int, int]):
        x, y = coord
        tile = self.game_sprites.get_terrain_tile(self._terrain.data[y][x].type)
        self.static_surface.blit(tile, ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE))

    def create_outline_surf(self, edge_directions):
            direction_log = {"Up", "Right", "Down", "Left"}

            self._tmp_tile.fill((0,0,0,0))  # reset


            for direction in edge_directions:
                direction_log.discard(direction) # removes from list as it will be used to check which direction has no edge

                outline_tile = self.game_sprites.get_outline_tile(direction)
                self._tmp_tile.blit(outline_tile, (0, 0))

            return self._tmp_tile.copy()
    
    def create_shadow_surf(self, edge_directions, coord):
            """
            Composes the shadow surface for a tile based on directional edges and floor-type corners.

            Args:
                edge_directions (list[str]): Edge directions ("Up", "Right", etc.)
                coord (tuple[int, int]): Tile coordinate.

            Returns:
                surrounding_floor (list[str]): Directions with adjacent floor tiles.
                shadow_surface (pg.Surface): Composite shadow surface for this tile.
            """
            from src.game import terrainTypes
            x, y = coord

            # neighbor positions
            direction_coords = {"adjacent": {
                "Up": (x, y - 1), "Down": (x, y + 1),
                "Right": (x + 1, y), "Left": (x - 1, y)}, "diagonal": {
                "Up Right": (x + 1, y - 1), "Up Left": (x - 1, y - 1),
                "Down Right": (x + 1, y + 1), "Down Left": (x - 1, y + 1)}
            }
    
            diagonal_data = {}
            # Check bounds and collect terrain types from diagonal neighbors
            for name, corner_coord in direction_coords["diagonal"].items():
                corner_x, corner_y = corner_coord
                if 0 <= corner_y < len(self._terrain.data) and 0 <= corner_x < len(self._terrain.data[0]):
                    diagonal_data[name] = self._terrain.data[corner_y][corner_x]

            direction_log = ["Up", "Right", "Down", "Left"]
            shadow_surface = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA).convert_alpha()

            # Add shadow edges for missing directions
            if edge_directions:
                for direction in edge_directions:
                    direction_log.remove(direction)
                    shadow_tile = self.game_sprites.get_shadow_tile(direction)
                    shadow_surface.blit(shadow_tile, (0, 0))

            valid_directions = []
            for direction in direction_log:
                checked_coord = direction_coords["adjacent"][direction]
                checked_x, checked_y = checked_coord
                if 0 <= checked_x < len(self._terrain.data[0]) and 0 <= checked_y < len(self._terrain.data):
                    valid_directions.append(direction)

            surrounding_floor = valid_directions  # Remaining directions are floor-adjacent

            # Determine valid corner combos for lighting
            corner_combos = [("Up", "Right"), ("Up", "Left"), ("Down", "Right"), ("Down", "Left")]
            corner_floors = [name for name, ore in diagonal_data.items() if ore.type == terrainTypes.Floor]

            surrounding_floor += corner_floors  # Merge floor-adjacent cardinal and diagonal

            # Check for corners eligible to light up
            for dir1, dir2 in corner_combos:
                if dir1 in surrounding_floor and dir2 in surrounding_floor:
                    corner = f"{dir1} {dir2}"
                    if corner not in corner_floors:
                        corner_shadow_tile = self.game_sprites.get_shadow_tile(corner)
                        shadow_surface.blit(corner_shadow_tile, (0, 0))

            return surrounding_floor, shadow_surface

    def add_surrounding_shadow(self, tile_coord: tuple[int, int], direction: str):
        shadow_tile = self.game_sprites.get_surrounding_shadow_tile(direction)
        x, y = tile_coord
        tile_size = gfx.TILE_SIZE

        # Convert tile coords to pixel coords
        pixel_x = x * tile_size
        pixel_y = y * tile_size

        self.static_surface.blit(shadow_tile, (pixel_x, pixel_y))

    def update_darkness(self, coord, darken=True):
        x, y = coord
        if darken:
            self.static_surface.blit(self.dark_tile, ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE))
        else:
            self.static_surface.fill((0, 0, 0, 0), ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE,
                                                gfx.TILE_SIZE, gfx.TILE_SIZE))
            
    def update_object(self, coord):
        if coord in self.objects:
            x, y = coord
            obj = self.objects[coord]
            if obj.on_floor:
                obj_sprite = self.game_sprites.get_object_tile(obj.name)
                self.static_surface.blit(obj_sprite, ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE))
            else:
                pass

    def update_ore_health(self, coord, health_percent, timer):
        x, y = coord
        transparency = 255
        if timer <= 0.5 and timer > 0:
            transparency = timer * 255

        if health_percent > 0 and timer > 0:
            self.ores_damaged.add(coord)
            pg.draw.rect(self.static_surface, (40, 40, 40, transparency), ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE, gfx.TILE_SIZE, 10))

            # Fill (e.g., green) — scaled to health percentage
            fill_width = int(gfx.TILE_SIZE * (health_percent / 100))
            if health_percent > 50:
                color = (0, 255, 0)
            elif health_percent > 15:
                color = (150, 150, 15)
            else:
                color = (225, 0, 0)
            pg.draw.rect(self.static_surface, (*color, transparency), ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE, fill_width, 10))
        elif health_percent <= 0 or timer <= 0:
            self.ores_damaged.discard(coord)
            if health_percent > 0:
                self.update_terrain_tile((coord))

    def load_new(self):
        grid_size = self._terrain.grid_size
        tile_size = gfx.TILE_SIZE
        padding = self.padding

        padded_size = (grid_size + padding * 2) * tile_size
        self.create_static_surface(padded_size)

        # Shift the surface origin so (0,0) is at top-left of padded area
        self.origin_offset = (-padding * tile_size, -padding * tile_size)

        for y in range(-padding, grid_size + padding, 2):
            for x in range(-padding, grid_size + padding, 2):
                direction = None
                if x < 0 and y < 0:
                    direction = "Down Right"
                elif x >= grid_size and y < 0:
                    direction = "Down Left"
                elif x < 0 and y >= grid_size:
                    direction = "Up Right"
                elif x >= grid_size and y >= grid_size:
                    direction = "Up Left"
                elif x < 0:
                    direction = "Right"
                elif x >= grid_size:
                    direction = "Left"
                elif y < 0:
                    direction = "Down"
                elif y >= grid_size:
                    direction = "Up"

                if direction:
                    # Shift tile coords to match padded surface origin
                    draw_x = x + padding
                    draw_y = y + padding
                    self.add_surrounding_shadow((draw_x, draw_y), direction)

        for y in range(self._terrain.grid_size):
            for x in range(self._terrain.grid_size):
                if (x, y) not in self._terrain.visible_tiles:
                    self.update_darkness((x, y))
                else:
                    self.update_terrain_tile((x, y))

        pg.draw.rect(self.static_surface, (175, 220, 240), (
            -2 + (self.padding * gfx.TILE_SIZE),
            -2 + (self.padding * gfx.TILE_SIZE),
            (self._terrain.grid_size * gfx.TILE_SIZE) + 4,
            (self._terrain.grid_size * gfx.TILE_SIZE) + 4
        ), 2)

    def create_static_surface(self, size):
        self.static_surface = pg.Surface((size, size), pg.SRCALPHA).convert_alpha()

class MinerSurface(GameSurface):
    def __init__(self):
        from src.game import Miner
        super().__init__()
        self.sprites = {}
        self.miners: list[Miner] = None
        self.miner_positions: dict[int: tuple[float, float]] = {}

    def update_miner_amount(self):
        self.miners = self._terrain._miners

    
    def get_sprite(self, miner_type: str):
        if miner_type not in self.sprites:
            surface = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)
            if miner_type == "Fire":
                color = (128, 0 ,0)
            elif miner_type == "Lightning":
                color = (200, 200, 5)
            circle_size = int(gfx.TILE_SIZE / 2)
            pg.draw.circle(surface, color, (circle_size, circle_size), circle_size - (gfx.TILE_SIZE / 4))
            self.sprites[miner_type] = surface
        return self.sprites[miner_type]
    
    def update_pos(self):
        for miner in self.miners:
            id, pos = miner.id, miner.pos
            self.miner_positions[id] = pos

    
    def update_static(self):
        """Only redraws changed miner positions."""
        dirty_rects = []

        for miner in self.miners:
            old_x, old_y = self.miner_positions[miner.id]
            dirty_rects.append(pg.Rect(old_x * gfx.TILE_SIZE, old_y * gfx.TILE_SIZE, gfx.TILE_SIZE, gfx.TILE_SIZE))

        for rect in dirty_rects:
            self.static_surface.fill((0, 0, 0, 0), rect)

        for miner in self.miners:
            sprite = self.get_sprite(miner.miner_type)

            x, y = miner.pos
            self.static_surface.blit(sprite, (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE))


    def load_new(self):
        self.create_static_surface()
        for miner in self.miners:
            self.miner_positions[miner.id] = miner.pos

        self.update_static()

class UISurface(GameSurface):
    def __init__(self):
        super().__init__()
        self.buttons = {}
        self.text = {}
        self.text_fonts = gfx.TextHandler()
        self.update_cd = 0.05
        self.cd_time = 0
        self.upgrades_manager = None
        self.update_list = set()
        self.past_fps = gfx.FPS
        self.FPS = self.past_fps
        self.filled_screen_color = (25, 25, 25)
        self.ore_panel = None
        self.ore_hover_active = True

    def set_upgrades_manager(self, upgrade_manager):
        self.upgrades_manager = upgrade_manager

    def add_to_update_list(self, info: tuple[str, bool]):
        self.update_list.add(info)

    def clear_update_list(self):
        self.update_list = set()

    def create_ore_panel(self, terrain):
        self.ore_panel = OrePanel(terrain, self)

    def fill_screen(self, type: str):
        if type == "invis":
            self.static_surface.fill((0, 0, 0, 0))
        elif type == "opaque":
            self.static_surface.fill(self.filled_screen_color)

    def create_button_bg(self, name: str, width: int, height: int, pos: tuple[int, int], color: tuple[int, int, int], round: bool, design=None):
        if name not in self.buttons:
            return Button(name, width, height, pos, color, round=round, surface_design=design)


    def create_text(self, name, text, pos, font, size, color, UI_height=None, center_x=None, button=False):
        font_obj = self.text_fonts.get_font(font, size)
        rendered_text = font_obj.render(text, True, color)

        if not button:
            self.add_to_update_list((name, False))

        # Center the text on the button if it exists
        if name in self.buttons:
            button = self.buttons[name]
            text_rect = rendered_text.get_rect()
            text_x = button.pos[0] + (button.width - text_rect.width) // 2
            text_y = button.pos[1] + (button.height - text_rect.height) // 2
            pos = (text_x, text_y)
        elif UI_height:
            pos = (pos[0], pos[1] + (UI_height / (UI_height / size)))
        elif center_x:
            text_rect = rendered_text.get_rect()
            text_x = text_rect.width
            if text_x > center_x:
                raise Exception(f"text \"{text}\" is too large for the given size to center the text in")
            else:
                text_x = pos[0] + (center_x - text_x) / 2
                pos = (text_x, pos[1])

        return (rendered_text, pos)

    def create_button(self, name, text, font, text_size, text_color, height, width, x, y, background_color, rounded, design=None):
        self.buttons[name] = self.create_button_bg(name, width, height,
                            (x, y),
                            background_color, rounded, design)
        if text:
            self.text[name] = self.create_text(name, text, 
                            (x, y),
                            font, text_size, 
                            text_color, center_x=True, button=True)
        
        self.add_to_update_list((name, True))


    def load_cave_UI(self):
        from src.game import Miner
        self.ore_hover_active = True
        self.buttons = {}
        self.text = {}
        self.clear_update_list()
        self.fill_screen("invis")
        self.create_button(name="Ore Luck Upgrade", text="Upgrade Luck", font="ubuntu", text_size=24, 
                           text_color=(200, 255, 200), height=50, width=150,x=15, 
                           y=gfx.SCREEN_HEIGHT - 65, background_color=(10, 10, 10), rounded=True)
        self.create_button(name="Ore Value Upgrade", text="Upgrade Value", font="ubuntu", text_size=24, 
                           text_color=(200, 255, 200), height=50, width=165,x=190, 
                           y=gfx.SCREEN_HEIGHT - 65, background_color=(10, 10, 10), rounded=True)
        
        self.create_button(name="Miner Boost", text=f"Current Boost: {round(Miner.global_miner_speed_boost, 3)}x", font="ubuntu", text_size=24,
                           text_color=(255, 255, 255), height=50, width=250, x=gfx.SCREEN_WIDTH / 2, 
                           y=gfx.SCREEN_HEIGHT - 100, background_color=(10, 10, 10), rounded=True)
        
        gold_amount = self.upgrades_manager.gold
        self.text["Gold Amount"] = self.create_text(name="Gold Amount", text=f"Gold: {gold_amount}", 
                                                    pos=(gfx.SCREEN_WIDTH - 200, 15), font="ubuntu", size=24,
                                                    color=(200, 255, 200))
        
        self._terrain._event_handler.set_buttons(self.buttons)
        
    def load_miner_UI(self):
        self.ore_hover_active = False
        self.buttons = {}
        self.text = {}
        self.clear_update_list()
        self.erase_ore_panel()
        self.fill_screen("opaque")
        max_miners = 20
        miner_box_length = 200
        x_distance, y_distance = 300, 250
        cols = 5
        rows = 4
        x_padding = (gfx.SCREEN_WIDTH - (cols * miner_box_length) - ((x_distance - miner_box_length) * (cols - 1))) / 2
        y_padding = (gfx.SCREEN_HEIGHT - (rows * miner_box_length) - ((y_distance - miner_box_length) * (rows - 1))) / 2
        x, y = x_padding, y_padding

        miner_sprite = pg.Surface((miner_box_length, miner_box_length), pg.SRCALPHA)
        pg.draw.circle(miner_sprite, (100, 100, 10), 
                           (int(miner_box_length / 2), int(miner_box_length / 2)), int(miner_box_length / 2) - 25)

        for i in range(max_miners):
            col = i % cols
            row = i // cols

            x = x_padding + col * x_distance
            y = y_padding + row * y_distance

            self.create_button(
                name=f"Miner {i + 1} Upgrades",
                text=None, font=None, text_size=None, text_color=None,
                height=miner_box_length, width=miner_box_length,
                x=x, y=y,
                background_color=(10, 10, 10), rounded=True, design=miner_sprite
            )
            self.text[f"Miner {i + 1} title"] = self.create_text(name=f"Miner {i + 1} title", text=f"Miner {i + 1}",  
                                            pos=(x, y + miner_box_length), font="ubuntu", size=24, 
                                            color=(200, 255, 200), center_x=miner_box_length)


        self._terrain._event_handler.set_buttons(self.buttons)

    def get_fps(self, FPS):
        self.past_fps = FPS
        self.FPS = int(FPS)
        if self.FPS <= self.past_fps + 2 or self.FPS >= self.past_fps + 2:
            self.update_text("FPS", f"fps {self.FPS}", pos=(0, 0), size=40)

    def update_text(self, name, new_text, pos=None, size=24, color=(200, 255, 200), button=False):
        if not pos:
            try:
                _, pos = self.text[name]
            except KeyError:
                pass

        self.text[name] = self.create_text(name=name, text=new_text, pos=pos, font="ubuntu", size=size,
                                           color=color, button=button)
    
        if button:
            self.add_to_update_list((name, button))

    def update_UI(self, dt=0, bypass_dt=False):
        self.cd_time -= dt
        if self.cd_time <= 0 or bypass_dt:
            to_be_updated = []
            for name, button in self.update_list:
                if button:
                    # render button background
                    try:
                        self.buttons[name].render(self.static_surface)
                    except: # name not found in buttons
                        to_be_updated.append(name)
                # render text
                if name not in to_be_updated:
                    text = None
                    if name in self.text:
                        try:
                            text, pos = self.text[name]
                            width, height = text.get_width(), text.get_height()
                            text_area = pg.Rect(pos[0], pos[1], width, height)
                        except TypeError:
                            del self.text[name]
                            continue
                    if not button:
                        try:
                            self.static_surface.fill((0, 0, 0, 0), text_area) # erase area
                        except:
                            continue
                    if text:
                        self.static_surface.blit(text, pos)

            self.clear_update_list()
            for button in to_be_updated: # Add it on pending list for when name is found in buttons, to update
                self.add_to_update_list((button, True))
            self.cd_time = self.update_cd

    def update_ore_panel(self, coord, ore):
        if self.ore_hover_active:
            if ore != self.ore_panel.ore:
                self.ore_panel.set_ore(ore)
                self.ore_panel.update_panel()

            if coord != self.ore_panel.pos:
                self.erase_ore_panel()
                self.ore_panel.pos = coord
                self.static_surface.blit(self.ore_panel.panel_surface, coord)

    def erase_ore_panel(self):
        if self.ore_panel.pos != None:
            if self.ore_hover_active:
                ore_panel_rect = pg.Rect(*self.ore_panel.pos, self.ore_panel.rect.width, self.ore_panel.rect.height)
                self.static_surface.fill((0, 0, 0, 0), (ore_panel_rect))

                colliding_buttons = []
                for key, button in self.buttons.items():
                    pos, button_rect = button.pos, button.rect
                    if ore_panel_rect.colliderect(button_rect):
                        self.add_to_update_list((key, True))
                        colliding_buttons.append(key)

                for key in self.text.keys():
                    if key not in colliding_buttons:
                        rendered_text, pos = self.text[key]
                        text_rect = rendered_text.get_rect()
                        text_rect = pg.Rect(pos[0], pos[1], text_rect.width, text_rect.height)
                        if ore_panel_rect.colliderect(text_rect):
                            self.add_to_update_list((key, False))

            self.update_UI(bypass_dt=True)

            

    def load_new(self):
        self.create_static_surface()
        self.load_cave_UI()
        self.update_UI(0)

    def create_static_surface(self):
        self.static_surface = pg.Surface((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT), pg.SRCALPHA).convert_alpha()


class Button():
    def __init__(self, name, width, height, pos, color, round, surface_design=None):
        self.name = name
        self.width = width
        self.height = height
        self.pos = pos
        self.color = color
        self.round_radius = 10 if round else 0
        self.rect = pg.Rect(pos[0], pos[1], width, height)
        self.surface_design = surface_design
        self.hovered = False

    def render(self, surface):
        rect = pg.draw.rect(surface, self.color, self.rect, border_radius=self.round_radius)
        if self.surface_design:
            surface.blit(self.surface_design, self.pos)
        return rect

    def collidepoint(self, *args):
        return self.rect.collidepoint(*args)
    
    def hovered_effect(self):
        self.hovered = True
        r, g, b = self.color
        r += 15
        g += 15
        b += 15
        self.color = (r, g, b)

    def non_hovered_effect(self):
        self.hovered = False
        r, g, b = self.color
        r -= 15
        g -= 15
        b -= 15
        self.color = (r, g, b)
    

class OrePanel():
    def __init__(self, terrain, UI_surface):
        from src.game import Terrain
        self._terrain: Terrain = terrain
        self._UI_surface: UISurface = UI_surface
        self.rect = pg.Rect(0, 0, 150, 165)
        self.ore = None
        self.ore_name = None
        self.ore_value = None
        self.ore_luck = None
        self.ore_health = None
        self.panel_surface = pg.Surface((150, 165))
        self.panel_color = (0, 0, 0)
        self.panel_text = {}
        self.text_color = (255, 255, 255)
        self.pos = None

    def set_ore(self, ore):
        self.ore = ore
        self.ore_name = f"{ore.type.name} Ore"
        try:
            self.ore_luck = f"Chance: {round(self._terrain._ore_chances[ore.type.value], 2)}/100"
        except KeyError:
            self.ore_luck = f"Chance: 0/100"
        self.ore_health = f"Health: {ore.health:.0f}/{ore.max_health:.0f}"
        self.ore_value = f"Value: {ore.gold}"
        self.update_panel()

    def update_text(self, y_pos, text, font="ubuntu", size=20, color=(255, 255, 255)):
        while True:
            font_obj = self._UI_surface.text_fonts.get_font(font, size)
            rendered_text = font_obj.render(text, True, color)
            text_width = rendered_text.get_width()
            if self.rect.width > text_width:
                padding = (self.rect.width - text_width) / 2
                pos = (padding, y_pos)
                break
            else:
                size -= 1

        self.panel_surface.blit(rendered_text, pos)
    
    def update_panel(self):
        self.panel_surface.fill(self.panel_color)
        self.update_text(10, self.ore_name)
        self.update_text(30, self.ore_luck, size=16)
        self.update_text(50, self.ore_health, size=16)
        self.update_text(70, self.ore_value, size=16)

class SpecialEffectSurface(GameSurface):

    def __init__(self):
        super().__init__()
        self.fire_effect_cd: float = 0.25
        self.fire_tiles: dict[tuple[int, int]: float] = {}

        self.electricity_effect_cd: float = 0.25
        self.electricity_tiles: dict[tuple[int, int]: float] = {}

    def get_fill_rect(self, x, y):
        return (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE, gfx.TILE_SIZE, gfx.TILE_SIZE)

    def animate_fire(self, dt, coords=[], updating=False):
        for coord in coords:
            self.fire_tiles[coord] = self.fire_effect_cd
        
        if updating:
            tiles_to_remove = []
            for key in self.fire_tiles.keys():
                self.fire_tiles[key] -= dt
                if self.fire_tiles[key] <= 0:
                    tiles_to_remove.append(key)

            for key in tiles_to_remove:
                x, y = key
                self.static_surface.fill((0, 0, 0, 0), self.get_fill_rect(x, y))
                del self.fire_tiles[key]

        for coord, timer in self.fire_tiles.items():
            x, y = coord
            transparency = 255
            if timer <= 0:
                break
            elif timer < self.fire_effect_cd / 2:
                transparency = min(timer * 10, 1) * 255
            color = (255, 0, 0, transparency)

            self.static_surface.fill(color, self.get_fill_rect(x, y))

    def animate_electricity(self, dt, coords=[], updating=False):
        for coord in coords:
            self.electricity_tiles[coord] = self.electricity_effect_cd
        
        if updating:
            tiles_to_remove = []
            for key in self.electricity_tiles.keys():
                self.electricity_tiles[key] -= dt
                if self.electricity_tiles[key] <= 0:
                    tiles_to_remove.append(key)

            for key in tiles_to_remove:
                x, y = key
                self.static_surface.fill((0, 0, 0, 0), self.get_fill_rect(x, y))
                del self.electricity_tiles[key]

        for coord, timer in self.electricity_tiles.items():
            x, y = coord
            transparency = 255
            if timer <= 0:
                break
            elif timer < self.electricity_effect_cd / 2:
                transparency = min(timer * 10, 1) * 255
            color = (255, 255, 0, transparency)

            self.static_surface.fill(color, self.get_fill_rect(x, y))

    def load_new(self):
        self.create_static_surface()

    

        
