import pygame as pg

class TextHandler():
    def __init__(self):
        self.font_cache = {}

    def get_font(self, font_name, size):
        key = f"{font_name.lower()}-{size}"
        if key not in self.font_cache:
            self.font_cache[key] = pg.font.SysFont(font_name, size)
        return self.font_cache[key]
    

class FPSCounter():
    def __init__(self, text_handler: TextHandler, dynamic_screen):
        self.update_cd = 0.5
        self.cd_time = self.update_cd
        self._last_fps = 0
        self._text_handler = text_handler
        self.font = "ubuntu"
        self.size = 40
        self.fps_counter = None
        self._dynamic_surface = dynamic_screen

    def set_FPS_counter(self, fps, dt):
        fps_int = int(fps)
        self.cd_time -= dt
        if fps_int != self._last_fps and self.cd_time <= 0:
            self._last_fps = fps_int
            font = self._text_handler.get_font(self.font, self.size)
            self.fps_counter = font.render(f"{fps_int}fps", True, (120, 225, 120))
            self.cd_time = self.update_cd

    def render(self):
        self._dynamic_surface.blit(self.fps_counter, (0, 0))
    

