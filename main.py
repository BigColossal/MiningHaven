from src.game import Terrain
import src.graphics as gfx
import pygame as pg

terrain = Terrain()
terrain_surface = gfx.TerrainSurface()

terrain.set_surface(terrain_surface)
terrain_surface.set_terrain(terrain)

graphics_engine = gfx.RenderManager(terrain)

while True:
    pg.init()
    clock = pg.time.Clock()
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pg.mouse.get_pos()

                # Convert screen coords to grid coords
                tile_x = (mouse_x - graphics_engine.offset_x) // gfx.TILE_SIZE
                tile_y = (mouse_y - graphics_engine.offset_y) // gfx.TILE_SIZE
                coord_broken = (tile_x, tile_y)

                # Bounds check
                if 0 <= tile_x < terrain.grid_size and 0 <= tile_y < terrain.grid_size:
                    terrain.break_terrain(coord_broken)
                    graphics_engine.break_terrain(coord_broken)


        graphics_engine.render()
        clock.tick(60)

    pg.quit()
        

if __name__ == "__main__":
    main()
