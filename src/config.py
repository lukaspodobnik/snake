import os
import sys
from enum import Enum, auto
from typing import Tuple

import pygame

# Game
TITLE = 'Snake'
FPS = 60
GRID_DIMENSION = (30, 20)
TILE_SIZE = 20

PLAYING_FIELD_WIDTH, PLAYING_FIELD_HEIGHT = GRID_DIMENSION[0] * TILE_SIZE, GRID_DIMENSION[1] * TILE_SIZE
PLAYING_UI_WIDTH, PLAYING_UI_HEIGHT = GRID_DIMENSION[0] * TILE_SIZE, 3 * TILE_SIZE
WIDTH, HEIGHT = GRID_DIMENSION[0] * TILE_SIZE, GRID_DIMENSION[1] * TILE_SIZE + PLAYING_UI_HEIGHT

# User events
MOVE = pygame.USEREVENT + 1

# Snake
EASY_SPEED = 180
MEDIUM_SPEED = 130
HARD_SPEED = 90
EXTREME_SPEED = 50

# Score
SCORE_BASE = 70
SCORE_EFFICIENCY_FACTOR = 4000
PICKUP_GROWTH_FACTOR = 0.1


class ColorTheme(Enum):
    NEON_GARDEN = auto()
    CYBER_RETRO = auto()
    PIXEL_DESERT = auto()
    FUTURE_MONOCHROME = auto()


class ColorConfig:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.background: Tuple[int, int, int] = (30, 30, 30)
        self.snake_head: Tuple[int, int, int] = (173, 255, 47)
        self.snake_tail: Tuple[int, int, int] = (34, 139, 34)
        self.food: Tuple[int, int, int] = (255, 69, 0)

    def set_color_theme(self, theme: ColorTheme):
        match theme:
            case ColorTheme.NEON_GARDEN:
                self.background = (30, 30, 30)
                self.snake_head = (173, 255, 47)
                self.snake_tail = (34, 139, 34)
                self.food = (255, 69, 0)
            case ColorTheme.CYBER_RETRO:
                self.background = (20, 20, 20)
                self.snake_head = (0, 255, 180)
                self.snake_tail = (0, 180, 130)
                self.food = (255, 105, 180)
            case ColorTheme.PIXEL_DESERT:
                self.background = (48, 35, 24)
                self.snake_head = (237, 201, 175)
                self.snake_tail = (205, 133, 63)
                self.food = (220, 20, 60)
            case ColorTheme.FUTURE_MONOCHROME:
                self.background = (25, 25, 25)
                self.snake_head = (200, 200, 200)
                self.snake_tail = (120, 120, 120)
                self.food = (255, 255, 255)


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
