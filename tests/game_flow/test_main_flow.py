"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Game Flow Integration Tests                                                 ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Your Name                                                  ║
║  Purpose       : Verify the main game flow and screen transitions.          ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.12                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pytest
from unittest.mock import MagicMock

from src.ui.main_menu_screen import MainMenuScreen
from src.ui.apartment_screen import ApartmentScreen


def test_continue_game_flow():
    """
    Tests the flow from the main menu to the apartment screen when continuing a game.
    This acts as a smoke test to ensure the core loop is functional.
    """
    # Arrange
    mock_main_ui = MagicMock()
    main_menu = MainMenuScreen(mock_main_ui)

    # Act
    main_menu.handle_action("continue_game")

    # Assert
    # Verify that the change_screen method was called
    mock_main_ui.change_screen.assert_called_once()

    # Verify that the screen being changed to is an instance of ApartmentScreen
    call_args = mock_main_ui.change_screen.call_args
    new_screen_instance = call_args[0][0]
    assert isinstance(
        new_screen_instance, ApartmentScreen
    ), f"Expected to transition to ApartmentScreen, but got {type(new_screen_instance).__name__}"


# EOF
