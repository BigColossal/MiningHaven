from src.game import Terrain, terrainTypes, EventHandler, Miner
import src.graphics as gfx
import pygame as pg

# order in all creation is important
terrain = Terrain()
terrain_surface = gfx.TerrainSurface()


outline_surface = gfx.OutlineSurface()
shadow_surface = gfx.ShadowSurface()
darkness_surface = gfx.DarknessSurface()
miner_surface = gfx.MinerSurface()
miners = []
miner_amount = 1
for i in range(miner_amount):
    miners.append(Miner(terrain))

terrain.set_surface(terrain_surface)
terrain.set_outlines(outline_surface)
terrain.set_shadows(shadow_surface)
terrain.set_darkness(darkness_surface)
terrain.set_miner_surface(miner_surface)
terrain.set_miners(miners)
terrain_surface.set_terrain(terrain)
outline_surface.set_terrain(terrain)
shadow_surface.set_terrain(terrain)
darkness_surface.set_terrain(terrain)
miner_surface.set_terrain(terrain)

FPS = 60

graphics_engine = gfx.RenderManager(terrain)
events_handler = EventHandler(graphics_engine, terrain)

terrain.set_event_handler(events_handler)
graphics_engine.set_renderer_to_surfaces()
terrain.initialize_terrain()
graphics_engine.load_new_cave()

def main():
    pg.init()
    clock = pg.time.Clock()
    running = True
    dt = 0

    while running:
        keys = pg.key.get_pressed()
        if keys[pg.K_w] or keys[pg.K_a] or keys[pg.K_s] or keys[pg.K_d]:
            graphics_engine.move_camera(keys)


        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                events_handler.handle_mouse_click(mouse_pos)

                

            if event.type == events_handler.events.TILE_BROKEN.value:
                for coord in event.positions:
                    terrain.break_terrain(coord, event.initialization, event.new_grid)
                    graphics_engine.break_terrain(coord)
                    terrain.check_if_cleared()

            if event.type == events_handler.events.SCREEN_DARKENING.value:
                graphics_engine.darkening = True
            if event.type == events_handler.events.SCREEN_LIGHTENING.value:
                graphics_engine.lightening = True

            if event.type == events_handler.events.CAVE_CLEARED.value:
                terrain.initialize_terrain()
                graphics_engine.set_initial_offset()
                graphics_engine.load_new_cave()

        graphics_engine.render(dt)
        dt = clock.tick(FPS)


    pg.quit()
        

if __name__ == "__main__":
    main()
