"""
Test suite for Warsim-Style UI Framework - Numbered Menu System.

Tests for the core UI framework that provides numbered menu options (1-9),
ASCII borders, status headers, and screen state management inspired by Warsim.
"""

import pytest
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch
from io import StringIO

from src.ui.main_ui import (
    MainUI,
    MenuOption,
    ScreenState,
    UIConfig,
    StatusData,
    MenuScreen,
    InputHandler,
)
from src.core.signals import get_signal_bus, CoreSignal


class TestMenuOption:
    """Test the MenuOption dataclass."""

    def test_menu_option_creation(self):
        """Test basic menu option creation."""
        option = MenuOption(key="1", text="Fight", action="combat_fight", enabled=True)

        assert option.key == "1"
        assert option.text == "Fight"
        assert option.action == "combat_fight"
        assert option.enabled == True

    def test_menu_option_with_description(self):
        """Test menu option with detailed description."""
        option = MenuOption(
            key="4",
            text="Use Ability",
            action="combat_ability",
            description="Cast spells or use special skills",
            hotkey="a",
            enabled=True,
        )

        assert option.description == "Cast spells or use special skills"
        assert option.hotkey == "a"

    def test_disabled_menu_option(self):
        """Test disabled menu option display."""
        option = MenuOption(
            key="7",
            text="Inventory",
            action="open_inventory",
            enabled=False,
            disabled_reason="Inventory is empty",
        )

        assert option.enabled == False
        assert option.disabled_reason == "Inventory is empty"


class TestStatusData:
    """Test the StatusData for header display."""

    def test_basic_status_data(self):
        """Test basic status data creation."""
        status = StatusData(location="Downtown Alley", gold=1247, time="15:42 Day 23")

        assert status.location == "Downtown Alley"
        assert status.gold == 1247
        assert status.time == "15:42 Day 23"

    def test_status_data_with_character_info(self):
        """Test status data with character information."""
        status = StatusData(
            location="Crime Scene",
            gold=850,
            time="09:15 Day 5",
            character_name="Detective Smith",
            health=(75, 100),
            mana=(12, 20),
        )

        assert status.character_name == "Detective Smith"
        assert status.health == (75, 100)
        assert status.mana == (12, 20)


class TestMenuScreen:
    """Test the MenuScreen rendering and management."""

    def test_menu_screen_creation(self):
        """Test basic menu screen creation."""
        options = [
            MenuOption("1", "Fight", "combat_fight"),
            MenuOption("2", "Defend", "combat_defend"),
            MenuOption("3", "Flee", "combat_flee"),
        ]

        screen = MenuScreen(
            title="Combat Options",
            description="Choose your action in combat",
            options=options,
        )

        assert screen.title == "Combat Options"
        assert len(screen.options) == 3
        assert screen.options[0].text == "Fight"

    def test_menu_screen_option_lookup(self):
        """Test finding options by key."""
        options = [
            MenuOption("1", "Fight", "combat_fight"),
            MenuOption("2", "Defend", "combat_defend"),
            MenuOption("9", "Settings", "open_settings"),
        ]

        screen = MenuScreen("Test", "Test menu", options)

        fight_option = screen.get_option("1")
        assert fight_option is not None
        assert fight_option.action == "combat_fight"

        settings_option = screen.get_option("9")
        assert settings_option is not None
        assert settings_option.action == "open_settings"

        invalid_option = screen.get_option("5")
        assert invalid_option is None

    def test_menu_screen_enabled_options_only(self):
        """Test filtering enabled options."""
        options = [
            MenuOption("1", "Fight", "combat_fight", enabled=True),
            MenuOption("2", "Defend", "combat_defend", enabled=True),
            MenuOption("3", "Flee", "combat_flee", enabled=False),
            MenuOption("4", "Ability", "combat_ability", enabled=True),
        ]

        screen = MenuScreen("Test", "Test menu", options)
        enabled = screen.get_enabled_options()

        assert len(enabled) == 3
        enabled_keys = [opt.key for opt in enabled]
        assert "1" in enabled_keys
        assert "2" in enabled_keys
        assert "4" in enabled_keys
        assert "3" not in enabled_keys


class TestInputHandler:
    """Test input handling for numbered menus."""

    def test_input_handler_creation(self):
        """Test input handler initialization."""
        handler = InputHandler()
        assert handler.current_screen is None

    def test_valid_key_input(self):
        """Test processing valid menu key inputs."""
        options = [
            MenuOption("1", "Fight", "combat_fight"),
            MenuOption("2", "Defend", "combat_defend"),
        ]
        screen = MenuScreen("Test", "Test menu", options)
        handler = InputHandler(screen)

        # Test valid inputs
        result = handler.process_input("1")
        assert result is not None
        assert result.action == "combat_fight"

        result = handler.process_input("2")
        assert result is not None
        assert result.action == "combat_defend"

    def test_invalid_key_input(self):
        """Test processing invalid menu key inputs."""
        options = [
            MenuOption("1", "Fight", "combat_fight"),
            MenuOption("2", "Defend", "combat_defend"),
        ]
        screen = MenuScreen("Test", "Test menu", options)
        handler = InputHandler(screen)

        # Test invalid inputs
        result = handler.process_input("3")
        assert result is None

        result = handler.process_input("a")
        assert result is None

        result = handler.process_input("")
        assert result is None

    def test_disabled_option_input(self):
        """Test processing input for disabled options."""
        options = [
            MenuOption("1", "Fight", "combat_fight", enabled=True),
            MenuOption("2", "Defend", "combat_defend", enabled=False),
        ]
        screen = MenuScreen("Test", "Test menu", options)
        handler = InputHandler(screen)

        # Enabled option should work
        result = handler.process_input("1")
        assert result is not None

        # Disabled option should return None
        result = handler.process_input("2")
        assert result is None


class TestMainUI:
    """Test the main MainUI class."""

    def test_ui_initialization(self):
        """Test UI framework initialization."""
        ui = MainUI()
        assert ui.current_screen is None
        assert ui.status_data is not None

    def test_ui_with_config(self):
        """Test UI with custom configuration."""
        config = UIConfig(
            width=80, height=25, border_style="double", show_timestamps=True
        )

        ui = MainUI(config)
        assert ui.config.width == 80
        assert ui.config.height == 25
        assert ui.config.border_style == "double"

    def test_screen_transition(self):
        """Test changing between screens."""
        ui = MainUI()

        # Create test screens
        main_options = [
            MenuOption("1", "Start Combat", "combat_start"),
            MenuOption("2", "Explore", "explore_area"),
        ]
        main_screen = MenuScreen(
            "Main Menu", "What would you like to do?", main_options
        )

        combat_options = [
            MenuOption("1", "Fight", "combat_fight"),
            MenuOption("2", "Defend", "combat_defend"),
        ]
        combat_screen = MenuScreen("Combat", "Choose your action", combat_options)

        # Test screen transitions
        ui.set_screen(main_screen)
        assert ui.current_screen == main_screen

        ui.set_screen(combat_screen)
        assert ui.current_screen == combat_screen

    def test_status_data_update(self):
        """Test updating status header data."""
        ui = MainUI()

        status = StatusData(location="Test Location", gold=500, time="12:00 Day 1")

        ui.update_status(status)
        assert ui.status_data.location == "Test Location"
        assert ui.status_data.gold == 500

    def test_ascii_border_rendering(self):
        """Test ASCII border generation."""
        ui = MainUI()

        # Test different border styles
        single_border = ui._generate_border_line(50, "single", "top")
        assert len(single_border) == 50
        assert single_border.startswith("┌")
        assert single_border.endswith("┐")

        double_border = ui._generate_border_line(50, "double", "top")
        assert len(double_border) == 50
        assert double_border.startswith("╔")
        assert double_border.endswith("╗")

    def test_menu_rendering(self):
        """Test menu option rendering."""
        ui = MainUI()

        options = [
            MenuOption("1", "Fight", "combat_fight"),
            MenuOption("2", "Defend", "combat_defend", enabled=False),
            MenuOption("3", "Flee", "combat_flee"),
        ]

        rendered_menu = ui._render_menu_options(options, 3)  # 3 columns
        assert isinstance(rendered_menu, list)
        assert len(rendered_menu) > 0

        # Check that enabled options appear in output
        menu_text = " ".join(rendered_menu)
        assert "1. Fight" in menu_text
        assert "3. Flee" in menu_text

    @patch("builtins.print")
    def test_full_screen_render(self, mock_print):
        """Test complete screen rendering."""
        ui = MainUI()

        status = StatusData(location="Test Area", gold=100, time="10:00 Day 1")
        ui.update_status(status)

        options = [
            MenuOption("1", "Option One", "action_one"),
            MenuOption("2", "Option Two", "action_two"),
            MenuOption("9", "Exit", "exit_game"),
        ]

        screen = MenuScreen("Test Menu", "This is a test menu", options)
        ui.set_screen(screen)

        # Render the screen
        ui.render()

        # Verify print was called (screen was rendered)
        assert mock_print.called

        # Check that output contains expected elements
        all_output = " ".join([str(call) for call in mock_print.call_args_list])
        assert "Test Area" in all_output
        assert "Test Menu" in all_output
        assert "Option One" in all_output


class TestMainUIIntegration:
    """Test MainUI integration with signal bus and game systems."""

    def test_ui_signal_integration(self):
        """Test UI responds to game signals."""
        ui = MainUI()
        signal_bus = get_signal_bus()

        signals_received = []

        def capture_signal(signal_data):
            signals_received.append(signal_data)

        # Set up signal listening
        signal_bus.listen(CoreSignal.UI_ACTION_SELECTED, capture_signal)

        # Simulate user action
        options = [MenuOption("1", "Test", "test_action")]
        screen = MenuScreen("Test", "Test screen", options)
        ui.set_screen(screen)

        # Process input (this should emit signal)
        result = ui.process_input("1")
        assert result is not None

        # Verify signal was emitted (may need to trigger manually in implementation)
        # This test structure is ready for when signals are implemented

    def test_ui_with_registry_data(self):
        """Test UI displaying data from game registries."""
        ui = MainUI()

        # This test would integrate with actual registries
        # For now, test the structure is ready

        # Example: Create menu from ability registry
        mock_abilities = [
            {"id": "snap_shot", "name": "Snap Shot"},
            {"id": "aimed_shot", "name": "Aimed Shot"},
            {"id": "patch_up", "name": "Patch Up"},
        ]

        # Convert to menu options
        options = []
        for i, ability in enumerate(mock_abilities, 1):
            options.append(
                MenuOption(
                    key=str(i),
                    text=ability["name"],
                    action=f"use_ability_{ability['id']}",
                )
            )

        screen = MenuScreen("Abilities", "Choose an ability to use", options)
        ui.set_screen(screen)

        assert len(screen.options) == 3
        assert screen.options[0].text == "Snap Shot"

    def test_screen_state_persistence(self):
        """Test that screen state persists correctly."""
        ui = MainUI()

        # Test screen history/back functionality
        main_screen = MenuScreen("Main", "Main menu", [])
        sub_screen = MenuScreen("Sub", "Sub menu", [])

        ui.set_screen(main_screen)
        ui.push_screen(sub_screen)  # Should stack screens

        assert ui.current_screen == sub_screen

        # Pop back to previous screen
        ui.pop_screen()
        assert ui.current_screen == main_screen


if __name__ == "__main__":
    pytest.main([__file__])
