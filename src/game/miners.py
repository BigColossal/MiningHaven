import pygame as pg

class Miner():
    miner_amount = 0
    def __init__(self, terrain):
        from src.game import Terrain
        Miner.miner_amount += 1
        self.id = Miner.miner_amount
        self.grid_pos = None
        self.pos = None
        self.moving_pos = None
        self._terrain: Terrain = terrain
        self._state = "Mining"
        self._path = []
        self._target = (None, None)

        self.movement_speed = 2
        self.mine_cd = 1

    def spawn_miner(self):
        cave_mid = (self._terrain.middle, self._terrain.middle)
        self.grid_pos = cave_mid
        self.pos = cave_mid

    def decision_make(self):
        if self._state == "Moving":
            self.move()
        elif self._state == "Mining":
            self.mine()
        

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
            if self._terrain.data[y][x] != self._terrain.terrain_types.Floor:
                self._target = path.pop()
                self._path = path  # Save the full path to the target
                self._state = "Moving"
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
            self._state = "Mining"
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
                self._state = "Mining"
        else:
            # Normalize direction and move in tile space
            nx = dx / distance
            ny = dy / distance
            x, y = round(px + nx * tile_speed, 2), round(py + ny * tile_speed, 2)
            self.pos = (x, y)

    def mine(self):
        import random
        x, y = self.grid_pos
        candidates = []

        # Gather all adjacent non-floor tiles
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < self._terrain.grid_size and
                0 <= ny < self._terrain.grid_size and
                self._terrain.data[ny][nx] != self._terrain.terrain_types.Floor
            ):
                candidates.append((nx, ny))

        if candidates:
            # Pick one at random
            self._target = random.choice(candidates)
            self._terrain._event_handler.call_tile_broken(self._target)
            self._path = [self._target]  # Move into the mined tile
            self._state = "Moving"
        else:
            # No adjacent targets, fallback to BFS
            self.check_surroundings()
