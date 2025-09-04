from src.game import Terrain, EventHandler, Miner, UpgradesManager, FireMiner, LightningMiner
import src.graphics as gfx
import pygame as pg
import math

pg.init()

# order in all creation is important
terrain = Terrain()

cave_surface = gfx.CaveSurface()
miner_surface = gfx.MinerSurface()
ui_surface = gfx.UISurface()
special_gfx_surface = gfx.SpecialEffectSurface()

upgrade_manager = UpgradesManager(terrain)
ui_surface.set_upgrades_manager(upgrade_manager)

surfaces = [cave_surface, miner_surface, ui_surface, special_gfx_surface]
miners = []
lightning_miner_amount = 10
fire_miner_amount = 10
for i in range(fire_miner_amount):
    miners.append(FireMiner(terrain))

for i in range(lightning_miner_amount):
    miners.append(LightningMiner(terrain))

upgrade_manager.set_miners(miners)

terrain.set_cave_surface(cave_surface)
terrain.set_miner_surface(miner_surface)
terrain.set_ui_surface(ui_surface)
terrain.set_special_gfx_surface(special_gfx_surface)
terrain.set_miners(miners)
for surface in surfaces:
    surface.set_terrain(terrain)

graphics_engine = gfx.RenderManager(terrain)
events_handler = EventHandler(graphics_engine, terrain)

terrain.set_event_handler(events_handler)
graphics_engine.set_renderer_to_surfaces()
terrain.initialize_terrain()
graphics_engine.load_new_cave()

def main():
    clock = pg.time.Clock()
    running = True
    dt = 0
    fps = 60
    events_handler.call_lightening_screen()
    ui_surface.create_ore_panel(terrain)

    while running:
        keys = pg.key.get_pressed()
        if keys[pg.K_w] or keys[pg.K_a] or keys[pg.K_s] or keys[pg.K_d]:
            graphics_engine.move_camera(keys)
        if keys[pg.K_q]:
            graphics_engine.switch_to_miner_UI()

        mouse_pos = pg.mouse.get_pos()
        graphics_engine.handle_mouse_hover(mouse_pos)

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

            if event.type == events_handler.events.LUCK_UPGRADED.value:
                upgrade_manager.increment_ore_luck(event.multiplier)

            if event.type == events_handler.events.ORE_VALUE_UPGRADED.value:
                upgrade_manager.increment_ore_value(event.multiplier)

            if event.type == events_handler.events.GOLD_GIVEN.value:
                upgrade_manager.increment_gold(event.amount)
                ui_surface.update_text("Gold Amount", f"Gold: {upgrade_manager.gold}")

            if event.type == events_handler.events.MINER_BOOST_CLICKED.value:
                upgrade_manager.incre_global_miner_speed_mult()
                ui_surface.update_text("Miner Boost", f"Current Boost: {round(Miner.global_miner_speed_boost, 3)}x", color=(255, 255, 255), button=True)

        upgrade_manager.incre_time_since_last(dt)
        if upgrade_manager.time_since_last_click >= 1.5:
            upgrade_manager.global_miner_speed_decay(dt)
            ui_surface.update_text("Miner Boost", f"Current Boost: {round(Miner.global_miner_speed_boost, 3)}x", color=(255, 255, 255), button=True)

        terrain.miner_decision_make(dt)
        graphics_engine.update_healthbars(dt)
        graphics_engine.check_miner_pos()

        graphics_engine.render(dt, fps)
        dt = clock.tick(gfx.FPS) / 1000
        fps = clock.get_fps()
        if math.isinf(fps) or math.isnan(fps):
            fps = 0




    pg.quit()
        

if __name__ == "__main__":
    main()
