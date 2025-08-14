import pygame as pg

class TextHandler():
    def __init__(self):
        self.font_cache = {}

    def get_font(self, font_name, size):
        key = f"{font_name.lower()}-{size}"
        if key not in self.font_cache:
            self.font_cache[key] = pg.font.SysFont(font_name, size)
        return self.font_cache[key]
    

