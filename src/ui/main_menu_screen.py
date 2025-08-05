"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Main Menu Screen                                                            ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019               ║
║  Purpose       : Professional main menu as game entry point                 ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.12                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
from typing import List

from src.ui.main_ui import MenuOption, MenuScreen
from src.game.character_creation import CharacterCreator

log = logging.getLogger("[MainMenu]")


class MainMenuScreen(MenuScreen):
    """Main menu screen as game entry point."""

    def __init__(self, main_ui):
        """Initialize main menu with standard options."""
        super().__init__("Broken Divinity - Main Menu")
        self.main_ui = main_ui
        self.character_creator = CharacterCreator()
        self.options = self._build_menu_options()
        log.info("Main menu screen initialized")

    def _build_menu_options(self) -> List[MenuOption]:
        """Build the main menu options."""
        return [
            MenuOption("1", "New Game", "new_game"),
            MenuOption("2", "Continue Game", "continue_game"),
            MenuOption("3", "Settings", "settings"),
            MenuOption("4", "Exit", "exit_game"),
        ]

    def handle_action(self, action: str) -> None:
        """Handle menu action selections."""
        log.debug(f"Handling action: {action}")

        if action == "new_game":
            self._start_new_game()
        elif action == "continue_game":
            self._continue_game()
        elif action == "settings":
            self._show_settings()
        elif action == "exit_game":
            self._exit_game()
        else:
            log.warning(f"Unknown action: {action}")

    def _start_new_game(self) -> None:
        """Start new game - go to character creation."""
        log.info("Starting new game - transitioning to character creation")
        from src.ui.character_creation_screen import CharacterCreationScreen

        character_screen = CharacterCreationScreen(self.main_ui, self.character_creator)
        self.main_ui.change_screen(character_screen)

    def _continue_game(self) -> None:
        """Continue existing game - go to apartment."""
        log.info("Continuing game - transitioning to apartment")
        from src.ui.apartment_screen import ApartmentScreen
        from src.game.locations import ApartmentLocation
        from src.game.character_state import CharacterState

        # Load existing character/save data (for now, use default detective)
        character_state = CharacterState()

        apartment_screen = ApartmentScreen()  # Now data-driven, no args needed
        self.main_ui.change_screen(apartment_screen)

    def _show_settings(self) -> None:
        """Show settings menu (placeholder for now)."""
        log.info("Settings menu requested (not implemented yet)")
        # TODO: Implement settings screen
        pass

    def _exit_game(self) -> None:
        """Exit the game."""
        log.info("Exit game requested")
        self.main_ui.should_exit = True


# EOF
