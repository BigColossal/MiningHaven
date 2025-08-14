from .render_manager import RenderManager
from .sprite_extraction import extract_sprites, GameSprites
from .surfaces import TerrainSurface, OutlineShadowSurface, MinerSurface, ObjectSurface, HealthBarSurface
from .text import TextHandler, FPSCounter

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
PADDING = 6
SHADOW_PADDING = 2
BG_COLOR = (15, 15, 15)
TILE_SIZE = 100
BASE_FPS = 60
FPS = 150
CAMERA_MOVEMENT_SPEED = int(20 / (FPS / BASE_FPS))
SHADOW_OFFSET = (-SHADOW_PADDING * TILE_SIZE, -SHADOW_PADDING * TILE_SIZE)
MIN_OFFSET = -TILE_SIZE * PADDING


