import src.graphics as gfx

class MinerCamera:
    def __init__(self):
        from src.game import Miner
        self.miners: list[Miner] = []
        self.miner_total: int = 0
        self.current_index: int = None
        self.current_miner: Miner = None
        self.camera_pos: tuple[float, float] = (0.0, 0.0)
        self.pixel_pos: tuple[float, float] = (0.0, 0.0)
        self.active = False
        self.switch_cd = 0.1
        self.time_between_switch = 0
        self.camera_changed = False

    def set_pixel_pos(self):
        camera_x, camera_y = self.camera_pos
        pixel_x, pixel_y = camera_x * gfx.TILE_SIZE, camera_y * gfx.TILE_SIZE
        self.pixel_pos = (pixel_x, pixel_y)
        return self.pixel_pos
    
    def reset_camera(self):
        self.current_index = None
        self.current_miner = None
        self.camera_pos = None
        self.pixel_pos = None
        self.active = False
        self.camera_changed = False

    def update_pos(self):
        self.camera_pos = self.current_miner.pos
        return self.set_pixel_pos()

    def update_total_miners(self, miners):
        self.miners = miners
        self.miner_total = len(self.miners)

    def handle_miner_updates(self):
        if self.current_miner:
            if self.current_miner.pos != self.camera_pos:
                self.camera_changed = True
                return self.update_pos()
            self.camera_changed = False
            return self.pixel_pos

    def switch_miner(self, direction, dt):
        self.time_between_switch -= dt
        if self.time_between_switch <= 0:
            if self.current_index == None:
                if direction == "Right":
                    self.current_index = 0
                elif direction == "Left":
                    self.current_index  = self.miner_total - 1
                elif direction == "Exit":
                    return

            else:
                if direction == "Right":
                    self.current_index += 1
                    if self.current_index >= self.miner_total:
                        self.current_index = 0
                elif direction == "Left":
                    self.current_index -= 1
                    if self.current_index < 0:
                        self.current_index = self.miner_total - 1
                elif direction == "Exit":
                    self.reset_camera()
                    return
                
            self.active = True
            self.current_miner = self.miners[self.current_index]
            self.time_between_switch = self.switch_cd

            
            


        
