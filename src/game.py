from typing import Optional

import os
import pygame
import pygame_gui

from config import TITLE, WIDTH, HEIGHT, FPS, GUI_PATH
from game_states import GameState, GameStates, MainMenu, Playing, Pause, GameOver
from highscore_manager import HighscoreManager


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption(TITLE)

        self.running = False

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.ui_manager.get_theme().load_theme(os.path.join(GUI_PATH, 'button.json'))
        self.ui_manager.get_theme().load_theme(os.path.join(GUI_PATH, 'label.json'))
        self.ui_manager.get_theme().load_theme(os.path.join(GUI_PATH, 'panel.json'))
        self.ui_manager.get_theme().load_theme(os.path.join(GUI_PATH, 'text_box.json'))
        self.clock = pygame.time.Clock()

        self.states = {
            GameStates.MAIN_MENU: MainMenu(self.ui_manager, self.change_state, self.stop),
            GameStates.PLAYING: Playing(self.ui_manager, self.change_state, self.stop),
            GameStates.PAUSE: Pause(self.ui_manager, self.change_state, self.stop),
            GameStates.GAME_OVER: GameOver(self.ui_manager, self.change_state, self.stop)
        }

        self.state: GameState = self.states[GameStates.MAIN_MENU]
        self.state.enter()

        HighscoreManager.get_instance().load()

    def run(self) -> None:
        self.running = True
        while self.running:
            delta = self.clock.tick(FPS)
            self.state.update(delta)
            self.state.draw(self.screen)

        pygame.quit()

    def stop(self) -> None:
        self.running = False

    def change_state(self, new_state: GameStates, options: Optional[dict[str, str]] = None) -> None:
        self.state.exit()
        self.state = self.states[new_state]
        self.state.enter(options)
