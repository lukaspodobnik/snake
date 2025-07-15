from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Optional

import pygame.event
import pygame_gui

from config import (PLAYING_FIELD_WIDTH, PLAYING_FIELD_HEIGHT, PLAYING_UI_HEIGHT, MOVE, SCORE_BASE,
                    SCORE_EFFICIENCY_FACTOR, PICKUP_GROWTH_FACTOR, ColorTheme, ColorConfig, EASY_SPEED, MEDIUM_SPEED,
                    HARD_SPEED, EXTREME_SPEED, resource_path)
from highscore_manager import HighscoreManager
from snake import Direction, Food, Snake
from user_interface import UserInterface, MainMenuUI, PlayingUI, UIEvents, SubUIs, PauseUI, GameOverUI


class GameStates(Enum):
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSE = auto()
    GAME_OVER = auto()


class GameState(ABC):
    def __init__(self, change_game_state: Callable[[GameStates, Optional[dict[str, str]]], None],
                 stop_game: Callable[[], None],
                 user_interface: UserInterface):
        self.change_game_state: Callable[[GameStates, Optional[dict[str, str]]], None] = change_game_state
        self.stop_game: Callable[[], None] = stop_game
        self.user_interface = user_interface

    @abstractmethod
    def _enter(self, options: Optional[dict[str, str]]) -> None:
        pass

    @abstractmethod
    def _exit(self) -> None:
        pass

    @abstractmethod
    def _handle_event(self, event: pygame.Event) -> None:
        pass

    @abstractmethod
    def _draw_contents(self, screen: pygame.Surface) -> None:
        pass

    def enter(self, options: Optional[dict[str, str]] = None) -> None:
        self.user_interface.show()
        self._enter(options)

    def exit(self) -> None:
        self.user_interface.deactivate()
        self._exit()

    def update(self, delta: float) -> None:
        for event in pygame.event.get():
            self.user_interface.process_event(event)
            if event.type == pygame.QUIT:
                self.stop_game()
            else:
                self._handle_event(event)

            self.user_interface.update(delta)

    def draw(self, screen: pygame.Surface) -> None:
        self._draw_contents(screen)
        self.user_interface.draw(screen)
        pygame.display.flip()


class MainMenu(GameState):
    def __init__(self, manager: pygame_gui.UIManager,
                 change_game_state: Callable[[GameStates, Optional[dict[str, str]]], None],
                 stop_game: Callable[[], None]):
        super().__init__(change_game_state, stop_game, user_interface=MainMenuUI(manager))

    def _enter(self, options: Optional[dict[str, str]]) -> None:
        pass

    def _exit(self) -> None:
        pass

    def _handle_event(self, event: pygame.Event) -> None:
        match self.user_interface.check_event(event):
            case UIEvents.MM_START:
                self.user_interface.hide()
                self.user_interface.show_sub_ui(SubUIs.MM_STARTING)
            case UIEvents.MM_QUIT:
                self.stop_game()
            case UIEvents.MM_USER_NAME_RETURNED:
                options = self.user_interface.send_data()
                player_name = options.get('player_name', None)
                if player_name is not None and player_name != '' and len(player_name) <= 12:
                    options['restart'] = "1"
                    self.change_game_state(GameStates.PLAYING, options)
            case UIEvents.MM_HIGHSCORE:
                self.user_interface.hide()
                self.user_interface.show_sub_ui(SubUIs.MM_HIGHSCORE)
                self.user_interface.receive_data({})
            case UIEvents.SM_BACK:
                self.user_interface.hide_sub_ui(SubUIs.MM_STARTING)
                self.user_interface.show()
            case UIEvents.HS_BACK:
                self.user_interface.hide_sub_ui(SubUIs.MM_HIGHSCORE)
                self.user_interface.show()

    def _draw_contents(self, screen: pygame.Surface) -> None:
        pass


class Playing(GameState):
    def __init__(self, manager: pygame_gui.UIManager,
                 change_game_state: Callable[[GameStates, Optional[dict[str, str]]], None],
                 stop_game: Callable[[], None]):
        super().__init__(change_game_state, stop_game, user_interface=PlayingUI(manager))

        self.playing_flied: pygame.Surface = pygame.Surface((PLAYING_FIELD_WIDTH, PLAYING_FIELD_HEIGHT))

        self.color_config = ColorConfig.get_instance()
        self.color_config.set_color_theme(ColorTheme.NEON_GARDEN)

        self.player_name: str = ''
        self.time_last_pickup: int = 0
        self.pickup_count = 0
        self.score: int = 0

        self.eat_sound = pygame.mixer.Sound(resource_path('res/sounds/eat_apple.wav'))
        self.die_sound = pygame.mixer.Sound(resource_path('res/sounds/game_over.wav'))

        self.snake: Snake = Snake()
        self.food: Food = Food()
        self.food.spawn(self.snake.get_positions())

    def _enter(self, options: Optional[dict[str, str]]) -> None:
        restart = options.get('restart', '0')
        if restart == '1':
            self.time_last_pickup: int = 0
            self.pickup_count = 0
            self.score: int = 0
            self.snake: Snake = Snake()
            self.food: Food = Food()
            self.food.spawn(self.snake.get_positions())
            self.user_interface.receive_data({'score': '0'})
            self.snake.move_rate = EASY_SPEED

        player_name = options.get('player_name', None)
        self.player_name = player_name if player_name is not None else self.player_name
        self.user_interface.receive_data(options)

        passed_time = int(options.get('time_passed', 0))
        self.time_last_pickup = pygame.time.get_ticks() if passed_time == 0 else self.time_last_pickup + passed_time

        pygame.time.set_timer(event=MOVE, millis=self.snake.move_rate)

    def _exit(self) -> None:
        pygame.time.set_timer(event=MOVE, millis=0)
        highscores = HighscoreManager.get_instance().get()
        score = highscores.get(self.player_name, -1)
        if self.score > score:
            HighscoreManager.get_instance().update(self.player_name, self.score)

    def _handle_event(self, event: pygame.Event) -> None:
        match self.user_interface.check_event(event):
            case UIEvents.PL_PAUSE:
                self.change_game_state(GameStates.PAUSE, None)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.snake.set_next_direction(Direction.UP)
            elif event.key == pygame.K_s:
                self.snake.set_next_direction(Direction.DOWN)
            elif event.key == pygame.K_a:
                self.snake.set_next_direction(Direction.LEFT)
            elif event.key == pygame.K_d:
                self.snake.set_next_direction(Direction.RIGHT)
            elif event.key == pygame.K_ESCAPE:
                self.change_game_state(GameStates.PAUSE, None)
        elif event.type == MOVE:
            self.snake.move()
            if self.snake.collides_with_screen() or self.snake.collides_with_self():
                self.die_sound.play()
                self.change_game_state(GameStates.GAME_OVER, None)
            elif self.snake.collides_with_food(self.food):
                self.eat_sound.play()
                self.snake.grow()
                self.update_score()
                self.food.spawn(self.snake.get_positions())

    def _draw_contents(self, screen: pygame.Surface) -> None:
        self.playing_flied.fill(self.color_config.background)
        self.snake.draw(self.playing_flied)
        self.food.draw(self.playing_flied)
        screen.blit(self.playing_flied, dest=(0, PLAYING_UI_HEIGHT))

    def update_score(self) -> None:
        current_time = pygame.time.get_ticks()
        time_since_last_pickup = current_time - self.time_last_pickup
        self.time_last_pickup = current_time

        self.pickup_count += 1
        self.score += int((SCORE_BASE * (SCORE_EFFICIENCY_FACTOR / time_since_last_pickup)
                           * (1 + self.pickup_count * PICKUP_GROWTH_FACTOR)))
        self.user_interface.receive_data(data={'score': str(self.score)})

        if self.score >= 500:
            self.snake.move_rate = MEDIUM_SPEED
            pygame.time.set_timer(event=MOVE, millis=self.snake.move_rate)
        elif self.score >= 3000:
            self.snake.move_rate = HARD_SPEED
            pygame.time.set_timer(event=MOVE, millis=self.snake.move_rate)
        elif self.score >= 10000:
            self.snake.move_rate = EXTREME_SPEED
            pygame.time.set_timer(event=MOVE, millis=self.snake.move_rate)


class Pause(GameState):
    def __init__(self, manager: pygame_gui.UIManager,
                 change_game_state: Callable[[GameStates, Optional[dict[str, str]]], None],
                 stop_game: Callable[[], None]):
        super().__init__(change_game_state, stop_game, user_interface=PauseUI(manager))

        self.time_entered = 0

    def _enter(self, options: Optional[dict[str, str]]) -> None:
        self.time_entered = pygame.time.get_ticks()

    def _exit(self) -> None:
        pass

    def _handle_event(self, event: pygame.Event) -> None:
        match self.user_interface.check_event(event):
            case UIEvents.PS_RESUME:
                time_passed = pygame.time.get_ticks() - self.time_entered
                self.change_game_state(GameStates.PLAYING, {'time_passed': str(time_passed)})
            case UIEvents.PS_MENU:
                self.change_game_state(GameStates.MAIN_MENU, None)
            case UIEvents.PS_QUIT:
                self.stop_game()

    def _draw_contents(self, screen: pygame.Surface) -> None:
        pass


class GameOver(GameState):
    def __init__(self, manager: pygame_gui.UIManager,
                 change_game_state: Callable[[GameStates, Optional[dict[str, str]]], None],
                 stop_game: Callable[[], None]):
        super().__init__(change_game_state, stop_game, user_interface=GameOverUI(manager))

    def _enter(self, options: Optional[dict[str, str]]) -> None:
        pass

    def _exit(self) -> None:
        pass

    def _handle_event(self, event: pygame.Event) -> None:
        match self.user_interface.check_event(event):
            case UIEvents.GO_RESTART:
                self.change_game_state(GameStates.PLAYING, {'restart': '1'})
            case UIEvents.GO_MENU:
                self.change_game_state(GameStates.MAIN_MENU, None)
            case UIEvents.GO_QUIT:
                self.stop_game()

    def _draw_contents(self, screen: pygame.Surface) -> None:
        pass
