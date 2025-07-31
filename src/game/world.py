from src.game import terrainTypes

class Terrain:
    def __init__(self):
        import src.graphics as gfx
        
        self._surface: gfx.TerrainSurface = None
        self.data = []
        self.grid_size = 10
        self.ore_chances = []

        self.initialize_terrain()

    def initialize_terrain(self):
        self.data = [[terrainTypes.Stone for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def set_surface(self, terrain_surface):
        self._surface = terrain_surface

    def wipe_terrain_data(self):
        self.data = []

    def break_terrain(self, coord):
        x, y = coord
        self.data[y][x] = terrainTypes.Floor

    def create_ore(self, coords):
        """
        As ore will be created when theyre revealed, or adjacent to a floor tile and in other terms everything starts
        as stone but gets converted to ore as theyre exposed as the player can upgrade their ore luck mid game, this will
        handle the creation of the ore dependant on the luck
        """
        for coord in coords:
            pass