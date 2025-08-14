from src.game import Terrain, EventHandler, Miner
import src.graphics as gfx
import pygame as pg
import math

pg.init()

# order in all creation is important
terrain = Terrain()
terrain_surface = gfx.TerrainSurface()


outline_surface = gfx.OutlineSurface()
shadow_surface = gfx.ShadowSurface()
darkness_surface = gfx.DarknessSurface()
miner_surface = gfx.MinerSurface()
object_surface = gfx.ObjectSurface()
healthbar_surface = gfx.HealthBarSurface()
surfaces = [terrain_surface, outline_surface, shadow_surface, darkness_surface, miner_surface, object_surface, healthbar_surface]
miners = []
miner_amount = 3
for i in range(miner_amount):
    miners.append(Miner(terrain))

terrain.set_surface(terrain_surface)
terrain.set_outlines(outline_surface)
terrain.set_shadows(shadow_surface)
terrain.set_darkness(darkness_surface)
terrain.set_miner_surface(miner_surface)
terrain.set_miners(miners)
terrain.set_object_surface(object_surface)
terrain.set_healthbar_surface(healthbar_surface)
for surface in surfaces:
    surface.set_terrain(terrain)

graphics_engine = gfx.RenderManager(terrain)
events_handler = EventHandler(graphics_engine, terrain)
text_handler = gfx.TextHandler()

terrain.set_event_handler(events_handler)
graphics_engine.set_renderer_to_surfaces()
graphics_engine.set_text_handler(text_handler)
terrain.initialize_terrain()
graphics_engine.load_new_cave()

def main():
    clock = pg.time.Clock()
    running = True
    dt = 0
    fps = 60
    events_handler.call_lightening_screen()

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

        terrain.clear_ores_damaged()
        terrain.miner_decision_make(dt)
        graphics_engine.update_healthbars()
        graphics_engine.check_miner_pos()

        graphics_engine.render(dt, fps)
        dt = clock.tick(gfx.FPS) / 1000
        fps = clock.get_fps()
        if math.isinf(fps) or math.isnan(fps):
            fps = 0




    pg.quit()
        

if __name__ == "__main__":
    main()
