import pygame as pg

class Miner():
    miner_amount = 0
    global_miner_speed_boost = 1
    def __init__(self, terrain):
        from src.game import Terrain
        Miner.miner_amount += 1
        self.id = Miner.miner_amount
        self.grid_pos = None
        self.pos = None
        self.moving_pos = None
        self._terrain: Terrain = terrain
        self._state = "Searching"
        self._path = None
        self._target = (None, None)

        self.base_movement_speed = 15
        self.base_mine_cd = 0.075
        self.movement_speed = self.base_movement_speed
        self.mine_cd = self.base_mine_cd

        self.cd_timer = self.mine_cd
        self.damage = 65
        self.miner_type = "Normal"
        self.passive_active_chance = 0.3

    def set_boost(self):
        self.movement_speed = round(self.base_movement_speed * Miner.global_miner_speed_boost, 3)
        self.mine_cd = round(self.base_mine_cd / Miner.global_miner_speed_boost, 3)

    def spawn_miner(self):
        cave_mid = (self._terrain.middle, self._terrain.middle)
        self.grid_pos = cave_mid
        self.pos = cave_mid
        self._path = []
        self._target = (None, None)


    def decision_make(self, dt):
        if self._state == "Moving":
            self.move()
        elif self._state == "Searching":
            self.choose_mining_direction()
        elif self._state == "Mining":
            self.mine(dt)
        

    def check_surroundings(self):
        from collections import deque

        visited = set()
        queue = deque()
        queue.append((self.grid_pos, []))  # (current_position, path_to_here)

        while queue:
            current_pos, path = queue.popleft()
            x, y = current_pos

            if current_pos in visited:
                continue
            visited.add(current_pos)

            # Check if this tile is NOT a floor
            if self._terrain.data[y][x].type != self._terrain.terrain_types.Floor:
                self._target = path.pop()
                self._path = path  # Save the full path to the target
                self._state = "Moving"
                self._sub_state = "Grid Moving"
                return

            # Explore neighbors (up, down, left, right)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < self._terrain.grid_size and
                    0 <= ny < self._terrain.grid_size and
                    (nx, ny) not in visited
                ):
                    queue.append(((nx, ny), path + [(nx, ny)]))

    def move(self):
        import src.graphics as gfx
        if not self._path:
            if self._sub_state == "Mining Block":
                self._state = "Mining"
            elif self._sub_state == "Grid Moving":
                self._state = "Searching"
            return

        target_tile = self._path[0]
        tx, ty = target_tile
        px, py = self.pos

        # Convert movement speed from pixels to tiles
        tile_speed = self.movement_speed / gfx.TILE_SIZE

        dx = tx - px
        dy = ty - py
        distance = (dx**2 + dy**2) ** 0.5
        if distance < tile_speed:
            # Snap to tile and pop from path
            self.pos = (tx, ty)
            self.grid_pos = target_tile
            self._path.pop(0)

            if not self._path:
                if self._sub_state == "Mining Block":
                    self._state = "Mining"
                elif self._sub_state == "Grid Moving":
                    self._state = "Searching"
        else:
            # Normalize direction and move in tile space
            nx = dx / distance
            ny = dy / distance
            x, y = round(px + nx * tile_speed, 2), round(py + ny * tile_speed, 2)
            self.pos = (x, y)

    def mine(self, dt):
        if self.cd_timer <= 0:
            x, y = self._target
            ore = self._terrain.data[y][x]
            destroyed = True
            if ore.health > 0:
                destroyed = ore.take_damage(self.damage)
            try:
                self._terrain.ores_damaged[self._target] = ((ore.health / ore.max_health) * 100, 2.5)
            except ZeroDivisionError:
                self._terrain.ores_damaged[self._target] = ((0, 0.0))
            if destroyed:
                self._path = [self._target]  # Move into the mined tile
                self._state = "Moving"
                self._sub_state = "Grid Moving"
            self.cd_timer = self.mine_cd
        else:
            self.cd_timer = max(0, self.cd_timer - dt)

        

    def choose_mining_direction(self):
        import random
        x, y = self.grid_pos
        candidates = []

        # Gather all adjacent non-floor tiles
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < self._terrain.grid_size and
                0 <= ny < self._terrain.grid_size and
                self._terrain.data[ny][nx].type != self._terrain.terrain_types.Floor
            ):
                candidates.append(((nx, ny), (dx, dy)))

        if candidates:
            # Pick one at random
            target, direction = random.choice(candidates)
            self._path = self.move_to_wall(self.pos, direction)
            self._target = target
            self._state = "Moving"
            self._sub_state = "Mining Block"

        else:
            # No adjacent targets, fallback to BFS
            self.check_surroundings()
        
    def move_to_wall(self, pos: tuple[int, int], direction: tuple[int, int]):
        x, y = pos
        xdir, ydir = direction
        xdir *= 0.25
        ydir *= 0.25
        return [(x + xdir, y + ydir)]
    
    def passive_chance_roll(self):
        import random
        chance = random.random()
        if chance <= self.passive_active_chance:
            return True
        return False
    
class FireMiner(Miner):
    def __init__(self, terrain):
        super().__init__(terrain)
        self.miner_type = "Fire"
        self.passive_active_chance = 0.3

    def activate_passive_ability(self):
        x, y = self._target
        possible_targets = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]
        targets = [self._target]
        for target_x, target_y in possible_targets:
            if target_x < self._terrain.grid_size and target_y < self._terrain.grid_size:
                if self._terrain.data[target_y][target_x].type != self._terrain.terrain_types.Floor and \
                    (target_x, target_y) in self._terrain.visible_tiles:
                        targets.insert(0, (target_x, target_y))

        return targets

    def mine(self, dt):
        if self.cd_timer <= 0:
            if self.passive_chance_roll():
                targets = self.activate_passive_ability()
            else:
                targets = [self._target]

            targets_to_animate = []

            for target in targets:
                x, y = target
                ore = self._terrain.data[y][x]
                if ore.health > 0:
                    if target != self._target:
                        dmg_factor = 0.1
                    else:
                        dmg_factor = 1
                    destroyed = ore.take_damage(self.damage * dmg_factor)
                    targets_to_animate.append(target)
                try:
                    self._terrain.ores_damaged[target] = ((ore.health / ore.max_health) * 100, 2.5)
                except ZeroDivisionError:
                    self._terrain.ores_damaged[target] = ((0, 0.0))
                    
            self._terrain._special_gfx_surface.animate_fire(dt, coords=targets_to_animate)

            target_x, target_y = self._target
            if self._terrain.data[target_y][target_x].health <= 0:
                self._path = [self._target]  # Move into the mined tile
                self._state = "Moving"
                self._sub_state = "Grid Moving"
            self.cd_timer = self.mine_cd
        else:
            self.cd_timer = max(0, self.cd_timer - dt)

class LightningMiner(Miner):
    def __init__(self, terrain):
        super().__init__(terrain)
        self.miner_type = "Lightning"
        self.passive_active_chance = 0.3

    def mine(self, dt):
        if self.cd_timer <= 0:
            if self.passive_chance_roll():
                path = self.get_chain_path()
            else:
                path = [self._target]
            path_to_animate = []

            for target in path:
                x, y = target
                ore = self._terrain.data[y][x]
                if ore.health > 0:
                    if target != self._target:
                        dmg_factor = 0.1
                    else:
                        dmg_factor = 1
                    destroyed = ore.take_damage(self.damage * dmg_factor)
                    path_to_animate.append(target)
                try:
                    self._terrain.ores_damaged[target] = ((ore.health / ore.max_health) * 100, 2.5)
                except ZeroDivisionError:
                    self._terrain.ores_damaged[target] = ((0, 0.0))

            self._terrain._special_gfx_surface.animate_electricity(dt, coords=path_to_animate)

            target_x, target_y = self._target
            if self._terrain.data[target_y][target_x].health <= 0:
                self._path = [self._target]  # Move into the mined tile
                self._state = "Moving"
                self._sub_state = "Grid Moving"
            self.cd_timer = self.mine_cd
        else:
            self.cd_timer = max(0, self.cd_timer - dt)

    
    def get_chain_path(self):
        visited = set()
        best_path = []

        def dfs(pos, current_path):
            nonlocal best_path
            x, y = pos

            if pos in visited:
                return
            visited.add(pos)

            # Skip if it's a floor tile or not visible
            if self._terrain.data[y][x].type == self._terrain.terrain_types.Floor or pos not in self._terrain.visible_tiles:
                visited.remove(pos)
                return

            # Enforce adjacency
            if not current_path or abs(x - current_path[-1][0]) + abs(y - current_path[-1][1]) == 1:
                current_path.append(pos)

                # Update best path if longer
                if len(current_path) > len(best_path):
                    best_path = current_path.copy()

                # Stop if max length reached
                if len(current_path) == 4:
                    visited.remove(pos)
                    current_path.pop()
                    return

                # Explore neighbors
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                import random
                random.shuffle(directions)

                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self._terrain.grid_size and 0 <= ny < self._terrain.grid_size:
                        dfs((nx, ny), current_path)

                current_path.pop()  # Backtrack
            visited.remove(pos)

        dfs(self._target, [])
        return best_path