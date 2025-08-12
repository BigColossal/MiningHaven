import pygame as pg

class TextHandler():
    def __init__(self):
        self.font_cache = {}

    def create_text(self, text, font_name, size, color=(255, 255, 255)):
        font_name = font_name.lower()
        if font_name not in self.font_cache:
            self.font_cache[font_name] = pg.font.SysFont(font_name, size)

        font = self.font_cache[font_name]
        text_surface = font.render(text, True, color)
        return text_surface
    

