import random
from abc import ABC, abstractmethod
from enum import Enum, auto
from itertools import product
from typing import Tuple

import pygame

from config import (PLAYING_FIELD_WIDTH, PLAYING_FIELD_HEIGHT, TILE_SIZE, GRID_DIMENSION, ColorConfig,
                    EASY_SPEED)


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Food:
    def __init__(self):
        self.rect: pygame.Rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        self.color_config: ColorConfig = ColorConfig.get_instance()
        self.grid_positions = set((x, y) for x, y in product(range(GRID_DIMENSION[0]), range(GRID_DIMENSION[1])))

    def spawn(self, invalid_positions: set[Tuple[int, int]]) -> None:
        x, y = random.choice(list(self.grid_positions - invalid_positions))
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color_config.food, self.rect)


class SnakeBody(ABC):
    color_config: ColorConfig = ColorConfig.get_instance()

    def __init__(self, spawn_pos: Tuple[int, int]):
        x, y = spawn_pos
        self.rect: pygame.Rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.position: Tuple[int, int] = spawn_pos

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass


class Head(SnakeBody):
    def __init__(self):
        super().__init__(spawn_pos=(random.randint(2, GRID_DIMENSION[0] - 3), random.randint(2, GRID_DIMENSION[1] - 3)))
        self.next_dir: Direction = random.choice([direction for direction in Direction])
        self.last_dir: Direction = self.next_dir

    def move(self) -> None:
        x, y = self.position
        match self.next_dir:
            case Direction.UP:
                self.rect.y -= TILE_SIZE
                self.position = (x, y - 1)
            case Direction.DOWN:
                self.rect.y += TILE_SIZE
                self.position = (x, y + 1)
            case Direction.LEFT:
                self.rect.x -= TILE_SIZE
                self.position = (x - 1, y)
            case Direction.RIGHT:
                self.rect.x += TILE_SIZE
                self.position = (x + 1, y)

    def collides_with_screen(self) -> bool:
        return (self.rect.left < 0 and self.next_dir == Direction.LEFT
                or self.rect.right > PLAYING_FIELD_WIDTH and self.next_dir == Direction.RIGHT
                or self.rect.top < 0 and self.next_dir == Direction.UP
                or self.rect.bottom > PLAYING_FIELD_HEIGHT and self.next_dir == Direction.DOWN)

    def collides_with_tail(self, tail: SnakeBody) -> bool:
        return self.rect.colliderect(tail.rect)

    def collides_with_food(self, food: Food) -> bool:
        return self.rect.colliderect(food.rect)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(surface=screen, color=self.color_config.snake_head, rect=self.rect)


class Tail(SnakeBody):
    def __init__(self, spawn_pos: Tuple[int, int]):
        super().__init__(spawn_pos=spawn_pos)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(surface=screen, color=self.color_config.snake_tail, rect=self.rect.inflate((-2, -2)))


class Snake:
    def __init__(self):
        self.head: Head = Head()
        x, y = self.head.rect.x / TILE_SIZE, self.head.rect.y / TILE_SIZE
        match self.head.next_dir:
            case Direction.UP:
                x_fac, y_fac = 0, 1
            case Direction.DOWN:
                x_fac, y_fac = 0, -1
            case Direction.LEFT:
                x_fac, y_fac = 1, 0
            case Direction.RIGHT:
                x_fac, y_fac = -1, 0
            case _:
                x_fac, y_fac = 0, 0

        self.body: list[SnakeBody] = [self.head,
                                      Tail(spawn_pos=(x + x_fac, y + y_fac)),
                                      Tail(spawn_pos=(x + 2 * x_fac, y + 2 * y_fac))]
        self.grow_position: Tuple[int, int] = (0, 0)
        self.move_rate = EASY_SPEED

    def set_next_direction(self, next_dir: Direction) -> None:
        if {self.head.last_dir, next_dir} in [{Direction.UP, Direction.DOWN}, {Direction.LEFT, Direction.RIGHT}]:
            return
        self.head.next_dir = next_dir

    def _remember_grow_position(self) -> None:
        self.grow_position = self.body[-1].position

    def _remember_last_direction(self) -> None:
        self.head.last_dir = self.head.next_dir

    def move(self) -> None:
        self._remember_grow_position()
        self._remember_last_direction()

        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].rect = self.body[i - 1].rect.copy()
            self.body[i].position = self.body[i - 1].position
        self.head.move()

    def collides_with_screen(self) -> bool:
        return self.head.collides_with_screen()

    def collides_with_self(self) -> bool:
        return any(self.head.collides_with_tail(tail) for tail in self.body[1:])

    def collides_with_food(self, food: Food) -> bool:
        return self.head.collides_with_food(food)

    def get_positions(self) -> set[Tuple[int, int]]:
        return set(body_part.position for body_part in self.body)

    def grow(self) -> None:
        self.body.append(Tail(spawn_pos=self.grow_position))

    def draw(self, screen: pygame.Surface) -> None:
        for snake_body in self.body:
            snake_body.draw(screen)
