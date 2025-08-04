"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Game State Machine Tests                                                    ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Test suite for game state management and screen transitions║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.9                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pytest
from unittest.mock import Mock, patch
from enum import Enum

from src.game.game_state_machine import GameStateMachine, GameState, StateTransition
from src.ui.main_ui import MainUI, MenuScreen


class TestGameState:
    """Test GameState enum and state management."""

    def test_game_state_enum_values(self):
        """Test that all expected game states exist."""
        assert GameState.MAIN_MENU
        assert GameState.EXPLORATION
        assert GameState.COMBAT
        assert GameState.INVESTIGATION
        assert GameState.CHARACTER
        assert GameState.INVENTORY
        assert GameState.SETTINGS
        assert GameState.SAVE_LOAD
        assert GameState.EXIT


class TestStateTransition:
    """Test StateTransition data structure."""

    def test_state_transition_creation(self):
        """Test creating state transitions."""
        transition = StateTransition(
            from_state=GameState.MAIN_MENU,
            to_state=GameState.EXPLORATION,
            action="start_game",
            description="Start new game",
        )

        assert transition.from_state == GameState.MAIN_MENU
        assert transition.to_state == GameState.EXPLORATION
        assert transition.action == "start_game"
        assert transition.description == "Start new game"


class TestGameStateMachine:
    """Test GameStateMachine state management."""

    def test_state_machine_initialization(self):
        """Test state machine starts in main menu."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()
            assert state_machine.current_state == GameState.MAIN_MENU
            assert state_machine.previous_state is None
            assert state_machine.ui is not None

    def test_valid_state_transition(self):
        """Test valid state transitions."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            # Transition from main menu to exploration
            result = state_machine.transition_to(GameState.EXPLORATION)

            assert result is True
            assert state_machine.current_state == GameState.EXPLORATION
            assert state_machine.previous_state == GameState.MAIN_MENU

    def test_invalid_state_transition(self):
        """Test invalid state transitions are rejected."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            # Can't go directly from main menu to combat
            result = state_machine.transition_to(GameState.COMBAT)

            assert result is False
            assert state_machine.current_state == GameState.MAIN_MENU

    def test_get_current_screen(self):
        """Test getting current screen for state."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            # Should return main menu screen
            screen = state_machine.get_current_screen()
            assert screen is not None

    def test_handle_menu_action_start_game(self):
        """Test handling start game action."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            # Handle start game action
            result = state_machine.handle_menu_action("1")  # Start game option

            assert result is True
            assert state_machine.current_state == GameState.EXPLORATION

    def test_handle_menu_action_invalid(self):
        """Test handling invalid menu actions."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            # Handle invalid action
            result = state_machine.handle_menu_action("invalid")

            assert result is False
            assert state_machine.current_state == GameState.MAIN_MENU

    def test_create_main_menu_screen(self):
        """Test creating main menu screen."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            screen = state_machine._create_main_menu_screen()

            assert screen.title == "Broken Divinity - Main Menu"
            assert len(screen.options) > 0

    def test_create_exploration_screen_stub(self):
        """Test creating exploration screen stub."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()
            state_machine.transition_to(GameState.EXPLORATION)

            screen = state_machine._create_exploration_screen()

            assert screen.title == "Exploration - Central District"
            assert "Under Development" in screen.description

    def test_create_combat_screen_stub(self):
        """Test creating combat screen stub."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()
            state_machine.current_state = GameState.COMBAT  # Force state for testing

            screen = state_machine._create_combat_screen()

            assert screen.title == "Combat Encounter"
            assert "Combat System" in screen.description

    def test_create_investigation_screen_stub(self):
        """Test creating investigation screen stub."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()
            state_machine.current_state = GameState.INVESTIGATION

            screen = state_machine._create_investigation_screen()

            assert screen.title == "Investigation - Crime Scene"
            assert "Investigation System" in screen.description

    def test_create_character_screen_stub(self):
        """Test creating character screen stub."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()
            state_machine.current_state = GameState.CHARACTER

            screen = state_machine._create_character_screen()

            assert screen.title == "Character Sheet - Detective"
            assert "Character Management" in screen.description

    def test_create_inventory_screen_stub(self):
        """Test creating inventory screen stub."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()
            state_machine.current_state = GameState.INVENTORY

            screen = state_machine._create_inventory_screen()

            assert screen.title == "Inventory & Equipment"
            assert "Inventory System" in screen.description

    def test_create_settings_screen_stub(self):
        """Test creating settings screen stub."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()
            state_machine.current_state = GameState.SETTINGS

            screen = state_machine._create_settings_screen()

            assert screen.title == "Game Settings"
            assert "Settings System" in screen.description

    def test_get_valid_transitions(self):
        """Test getting valid transitions from current state."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            transitions = state_machine.get_valid_transitions()

            # From main menu, should be able to go to exploration, settings, etc.
            assert len(transitions) > 0
            target_states = [t.to_state for t in transitions]
            assert GameState.EXPLORATION in target_states

    def test_can_transition_to(self):
        """Test checking if transition is valid."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            # Can transition from main menu to exploration
            assert state_machine.can_transition_to(GameState.EXPLORATION)

            # Cannot transition from main menu to combat
            assert not state_machine.can_transition_to(GameState.COMBAT)

    def test_go_back_to_previous_state(self):
        """Test returning to previous state."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            # Transition to exploration
            state_machine.transition_to(GameState.EXPLORATION)
            assert state_machine.current_state == GameState.EXPLORATION

            # Go back to main menu
            result = state_machine.go_back()
            assert result is True
            assert state_machine.current_state == GameState.MAIN_MENU

    def test_cannot_go_back_from_main_menu(self):
        """Test cannot go back from main menu."""
        with patch("src.game.game_state_machine.MainUI") as mock_ui:
            state_machine = GameStateMachine()

            # Cannot go back from main menu
            result = state_machine.go_back()
            assert result is False
            assert state_machine.current_state == GameState.MAIN_MENU


# EOF
