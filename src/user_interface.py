from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional

import pygame
import pygame_gui.elements

from config import WIDTH, HEIGHT, PLAYING_UI_WIDTH, PLAYING_UI_HEIGHT
from highscore_manager import HighscoreManager


class UIEvents(Enum):
    # MainMenu UIEvents
    HS_BACK = auto()
    MM_START = auto()
    MM_HIGHSCORE = auto()
    MM_QUIT = auto()
    MM_USER_NAME_RETURNED = auto()

    # StartingMenu UIEvents
    SM_BACK = auto()

    # Playing UIEvents
    PL_PAUSE = auto()

    # Pause UIEvents
    PS_RESUME = auto()
    PS_MENU = auto()
    PS_QUIT = auto()

    # GameOver UIEvents
    GO_RESTART = auto()
    GO_MENU = auto()
    GO_QUIT = auto()


class SubUIs(Enum):
    # MainMenu SubUIs:
    MM_STARTING = auto()
    MM_HIGHSCORE = auto()

    # Playing SubUIs:
    P_PAUSE = auto()


class UserInterface(ABC):
    def __init__(self, manager: pygame_gui.UIManager,
                 relative_container_rect=pygame.Rect((0, 0), (WIDTH, HEIGHT)),
                 sub_uis=None,
                 container=None):
        e = pygame_gui.elements
        self._manager: pygame_gui.UIManager = manager
        self._sub_uis: dict[SubUIs, UserInterface] = sub_uis if sub_uis is not None else {}
        self._container: pygame_gui.elements.UIPanel = e.UIPanel(relative_rect=relative_container_rect,
                                                                 manager=manager) if container is None else container
        self._container.hide()

    @abstractmethod
    def _send_data(self) -> dict[str, str]:
        pass

    @abstractmethod
    def _receive_data(self, data: dict[str, str]):
        pass

    @abstractmethod
    def _check_event(self, event: pygame.Event) -> Optional[UIEvents]:
        pass

    def send_data(self) -> dict[str, str]:
        for sub_ui in self._sub_uis.values():
            if not sub_ui.is_hidden():
                return sub_ui._send_data()

        return self._send_data()

    def receive_data(self, data: dict[str, str]):
        for sub_ui in self._sub_uis.values():
            if not sub_ui.is_hidden():
                sub_ui._receive_data(data)
                return

        self._receive_data(data)

    def check_event(self, event: pygame.Event) -> Optional[UIEvents]:
        for sub_ui in self._sub_uis.values():
            if not sub_ui.is_hidden():
                return sub_ui._check_event(event)

        return self._check_event(event)

    def deactivate(self) -> None:
        for sub_ui in self._sub_uis.values():
            sub_ui.hide()
        self.hide()

    def show(self) -> None:
        self._container.show()

    def hide(self) -> None:
        self._container.hide()

    def show_sub_ui(self, ui: SubUIs) -> None:
        self._sub_uis[ui].show()

    def hide_sub_ui(self, ui: SubUIs) -> None:
        self._sub_uis[ui].hide()

    def enable(self) -> None:
        self._container.enable()

    def disable(self) -> None:
        self._container.disable()

    def enable_sub_ui(self, ui: SubUIs) -> None:
        self._sub_uis[ui].enable()

    def disable_sub_ui(self, ui: SubUIs) -> None:
        self._sub_uis[ui].disable()

    def is_enabled(self) -> bool:
        return self._container.is_enabled

    def is_hidden(self) -> bool:
        return not self._container.visible

    def update(self, delta: float) -> None:
        self._manager.update(delta)

    def process_event(self, event: pygame.Event) -> None:
        self._manager.process_events(event)

    def draw(self, screen: pygame.Surface) -> None:
        self._manager.draw_ui(screen)


class MainMenuUI(UserInterface):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(manager, sub_uis={SubUIs.MM_STARTING: self.StartingMenuUI(manager),
                                           SubUIs.MM_HIGHSCORE: self.HighscoreMenuUI(manager)})

        offset_label, offset_button, offset_first_button = (0, 20), (0, 10), (0, 20)
        size_label, size_button = (420, 150), (170, 70)

        self.logo_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(offset_label, size_label),
                                                      text='SNAKE',
                                                      manager=manager,
                                                      container=self._container,
                                                      anchors={'centerx': 'centerx'},
                                                      object_id=pygame_gui.core.ObjectID('#logo', None))

        self.start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(offset_first_button, size_button),
                                                         text='START',
                                                         manager=manager,
                                                         container=self._container,
                                                         anchors={'centerx': 'centerx',
                                                                  'top_target': self.logo_label})

        self.highscore_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(offset_button, size_button),
                                                             text='HIGHSCORE',
                                                             manager=manager,
                                                             container=self._container,
                                                             anchors={'centerx': 'centerx',
                                                                      'top_target': self.start_button})

        self.quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(offset_button, size_button),
                                                        text='QUIT',
                                                        manager=manager,
                                                        container=self._container,
                                                        anchors={'centerx': 'centerx',
                                                                 'top_target': self.highscore_button})

    def _check_event(self, event: pygame.Event) -> Optional[UIEvents]:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_button:
                return UIEvents.MM_START
            elif event.ui_element == self.highscore_button:
                return UIEvents.MM_HIGHSCORE
            elif event.ui_element == self.quit_button:
                return UIEvents.MM_QUIT

        return None

    def _send_data(self) -> dict[str, str]:
        pass

    def _receive_data(self, data: dict[str, str]):
        pass

    class StartingMenuUI(UserInterface):
        def __init__(self, manager: pygame_gui.UIManager):
            super().__init__(manager)
            self.msg = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 50, 500, 80),
                                                   text='Enter you name and press RETURN to start',
                                                   manager=manager,
                                                   container=self._container,
                                                   anchors={'centerx': 'centerx'})

            self.name_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(0, 40, 300, 50),
                                                                  manager=manager,
                                                                  container=self._container,
                                                                  anchors={'centerx': 'centerx',
                                                                           'top_target': self.msg})
            self.name_input.focus()

            button_rect = pygame.Rect(0, 0, 100, 50)
            button_rect.bottomleft = (10, -10)
            self.back_button = pygame_gui.elements.UIButton(relative_rect=button_rect,
                                                            text='BACK',
                                                            manager=manager,
                                                            container=self._container,
                                                            tool_tip_text='Press ESC to go back',
                                                            anchors={'bottom': 'bottom',
                                                                     'left': 'left'})

        def _check_event(self, event: pygame.Event) -> Optional[UIEvents]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return UIEvents.MM_USER_NAME_RETURNED
                elif event.key == pygame.K_ESCAPE:
                    return UIEvents.SM_BACK
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_button:
                    return UIEvents.SM_BACK

        def _send_data(self) -> dict[str, str]:
            return {'player_name': self.name_input.get_text()}

        def _receive_data(self, data: dict[str, str]):
            pass

    class HighscoreMenuUI(UserInterface):
        def __init__(self, manager: pygame_gui.UIManager):
            super().__init__(manager)
            e = pygame_gui.elements
            self.highscore_label = e.UILabel(relative_rect=pygame.Rect((0, 20), (WIDTH - 300, 60)),
                                             manager=manager,
                                             container=self._container,
                                             text='HIGHSCORES',
                                             anchors={'centerx': 'centerx'},
                                             object_id=pygame_gui.core.ObjectID('#game_over_label', None))

            self.score_panel = e.UIPanel(relative_rect=pygame.Rect((0, 20), (WIDTH - 100, 338)),
                                         manager=manager,
                                         container=self._container,
                                         anchors={'centerx': 'centerx',
                                                  'top_target': self.highscore_label},
                                         object_id=pygame_gui.core.ObjectID('#score_panel', None))

            self.back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(5, 5, 70, 25),
                                                            text='BACK',
                                                            manager=manager,
                                                            container=self._container,
                                                            tool_tip_text='Press ESC to go back',
                                                            object_id=pygame_gui.core.ObjectID('#hs_back', None))

        def _check_event(self, event: pygame.Event) -> Optional[UIEvents]:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_button:
                    return UIEvents.HS_BACK

            return None

        def _send_data(self) -> dict[str, str]:
            pass

        def _receive_data(self, data: dict[str, str]):
            scores = HighscoreManager.get_instance().get()
            scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

            def create_label(text, pos, size, object_id):
                x, y = pos
                pygame_gui.elements.UILabel(relative_rect=pygame.Rect((x - 2, y), size),
                                            text=text,
                                            manager=self._manager,
                                            container=self.score_panel,
                                            object_id=pygame_gui.core.ObjectID(object_id, '@hs_label'))

            create_label('Rank', (0, 0), size=(60, 30), object_id='#hs_heading_label')
            create_label('Name', (60, 0), size=(220, 30), object_id='#hs_heading_label')
            create_label("Score", (280, 0), size=(210, 30), object_id='#hs_heading_label')

            for i in range(10):
                o_id = '#hs_label_odd' if i % 2 == 1 else '#hs_label_even'
                name, score = scores[i] if len(scores) > i else ('', '')
                create_label(str(i + 1), (0, (i + 1) * 30), (60, 30), object_id=o_id)
                create_label(name, (60, (i + 1) * 30), (220, 30), object_id=o_id)
                create_label(str(score), (280, (i + 1) * 30), (210, 30), object_id=o_id)


class PlayingUI(UserInterface):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(manager, relative_container_rect=pygame.Rect(0, 0, PLAYING_UI_WIDTH, PLAYING_UI_HEIGHT))
        self.name_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(5, 0, 100, PLAYING_UI_HEIGHT - 20),
                                                      manager=manager,
                                                      container=self._container,
                                                      text='',
                                                      anchors={'centery': 'centery'},
                                                      object_id=pygame_gui.core.ObjectID(object_id='#name_label',
                                                                                         class_id='@playing_label'))

        self.score_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 0, 100, PLAYING_UI_HEIGHT - 20),
                                                       manager=manager,
                                                       container=self._container,
                                                       text='SCORE: 0',
                                                       anchors={'center': 'center'},
                                                       object_id=pygame_gui.core.ObjectID(object_id=None,
                                                                                          class_id='@playing_label'))

        button_rect = pygame.Rect(0, 0, 100, PLAYING_UI_HEIGHT - 20)
        button_rect.right = -5
        self.pause_button = pygame_gui.elements.UIButton(relative_rect=button_rect,
                                                         manager=manager,
                                                         container=self._container,
                                                         text='PAUSE',
                                                         anchors={'centery': 'centery',
                                                                  'right': 'right'})

    def _check_event(self, event: pygame.Event) -> Optional[UIEvents]:
        if event.type == pygame_gui.UI_BUTTON_PRESSED and hasattr(event, 'ui_element'):
            if event.ui_element == self.pause_button:
                return UIEvents.PL_PAUSE

        return None

    def _send_data(self) -> dict[str, str]:
        pass

    def _receive_data(self, data: dict[str, str]):
        player_name = data.get('player_name', None)
        score = data.get('score', None)
        font = self._manager.get_theme().get_font(['@playing_label'])

        if player_name is not None:
            self.name_label.set_dimensions((font.size('NAME: ' + player_name)[0] + 10, PLAYING_UI_HEIGHT - 20))
            self.name_label.set_text('NAME: ' + player_name)

        if score is not None:
            self.score_label.set_dimensions((font.size('SCORE: ' + score)[0] + 10, PLAYING_UI_HEIGHT - 20))
            self.score_label.set_text('SCORE: ' + score)


class PauseUI(UserInterface):
    def __init__(self, manager: pygame_gui.UIManager):
        container = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(0, 20, WIDTH - 100, HEIGHT - 100),
                                                manager=manager,
                                                anchors={'center': 'center'})
        super().__init__(manager=manager, container=container)

        self.pause_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 100),
                                                       text='PAUSE',
                                                       container=container,
                                                       anchors={'centerx': 'centerx'},
                                                       object_id=pygame_gui.core.ObjectID('#game_over_label', None))

        self.resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 30), (170, 50)),
                                                          manager=manager,
                                                          container=container,
                                                          text='RESUME',
                                                          anchors={'centerx': 'centerx',
                                                                   'top_target': self.pause_label})

        self.menu_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(0, 10, 170, 50),
                                                        manager=manager,
                                                        container=container,
                                                        text='BACK TO MENU',
                                                        anchors={'centerx': 'centerx',
                                                                 'top_target': self.resume_button})

        self.quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(0, 10, 170, 50),
                                                        manager=manager,
                                                        container=container,
                                                        text='QUIT GAME',
                                                        anchors={'centerx': 'centerx',
                                                                 'top_target': self.menu_button})

    def _send_data(self) -> dict[str, str]:
        pass

    def _receive_data(self, data: dict[str, str]):
        pass

    def _check_event(self, event: pygame.Event) -> Optional[UIEvents]:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.resume_button:
                return UIEvents.PS_RESUME
            elif event.ui_element == self.menu_button:
                return UIEvents.PS_MENU
            elif event.ui_element == self.quit_button:
                return UIEvents.PS_QUIT


class GameOverUI(UserInterface):
    def __init__(self, manager: pygame_gui.UIManager):
        container = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(0, 20, WIDTH - 100, HEIGHT - 100),
                                                manager=manager,
                                                anchors={'center': 'center'})
        super().__init__(manager=manager, container=container)

        button_size = (170, 50)

        self.go_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 100),
                                                    text='GAME OVER',
                                                    container=container,
                                                    anchors={'centerx': 'centerx'},
                                                    object_id=pygame_gui.core.ObjectID('#game_over_label', None))

        self.restart_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 30), button_size),
                                                           manager=manager,
                                                           container=container,
                                                           text='RESTART',
                                                           anchors={'centerx': 'centerx',
                                                                    'top_target': self.go_label})

        self.menu_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 10), button_size),
                                                        manager=manager,
                                                        container=container,
                                                        text='BACK TO MENU',
                                                        anchors={'centerx': 'centerx',
                                                                 'top_target': self.restart_button})

        self.quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 10), button_size),
                                                        manager=manager,
                                                        container=container,
                                                        text='QUIT GAME',
                                                        anchors={'centerx': 'centerx',
                                                                 'top_target': self.menu_button})

    def _send_data(self) -> dict[str, str]:
        pass

    def _receive_data(self, data: dict[str, str]):
        pass

    def _check_event(self, event: pygame.Event) -> Optional[UIEvents]:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.restart_button:
                return UIEvents.GO_RESTART
            elif event.ui_element == self.menu_button:
                return UIEvents.GO_MENU
            elif event.ui_element == self.quit_button:
                return UIEvents.GO_QUIT
