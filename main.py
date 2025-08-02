from src.game import Terrain, terrainTypes
import src.graphics as gfx
import pygame as pg

terrain = Terrain()
terrain_surface = gfx.TerrainSurface()
outline_surface = gfx.OutlineSurface()
shadow_surface = gfx.ShadowSurface()

terrain.set_surface(terrain_surface)
terrain.set_outlines(outline_surface)
terrain.set_shadows(shadow_surface)
terrain_surface.set_terrain(terrain)
outline_surface.set_terrain(terrain)
shadow_surface.set_terrain(terrain)

FPS = 60

graphics_engine = gfx.RenderManager(terrain)

while True:
    pg.init()
    clock = pg.time.Clock()
    running = True

    while running:
        keys = pg.key.get_pressed()
        graphics_engine.move_camera(keys)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pg.mouse.get_pos()

                # Convert screen coords to grid coords
                tile_x = int((mouse_x + graphics_engine.offset_x) // gfx.TILE_SIZE)
                tile_y = int((mouse_y + graphics_engine.offset_y) // gfx.TILE_SIZE)
                coord_broken = (tile_x, tile_y)

                # Bounds check
                if 0 <= tile_x < terrain.grid_size and 0 <= tile_y < terrain.grid_size:
                    if terrain.data[tile_y][tile_x] != terrainTypes.Floor:
                        terrain.break_terrain(coord_broken)
                        graphics_engine.break_terrain(coord_broken)

        graphics_engine.update()
        graphics_engine.render()
        clock.tick(FPS)


    pg.quit()
        

if __name__ == "__main__":
    main()
