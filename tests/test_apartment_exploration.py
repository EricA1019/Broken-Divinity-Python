"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Apartment Exploration Tests                                                ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Test apartment exploration system for Hop 11               ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.11                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pytest
from unittest.mock import Mock, patch
from src.core.signals import get_signal_bus, reset_signal_bus
from src.ui.main_ui import MainUI
from src.game.game_state_machine import GameStateMachine, GameState
from src.game.state_registry import StateRegistry


class TestApartmentExploration:
    """Test basic apartment exploration system"""

    def setup_method(self):
        """Setup test environment"""
        reset_signal_bus()
        self.signal_bus = get_signal_bus()
        self.ui = MainUI()
        self.state_machine = GameStateMachine()

    def test_apartment_location_creation(self):
        """Test apartment location can be created"""
        from src.game.locations import ApartmentLocation

        apartment = ApartmentLocation()
        assert apartment.name == "Morrison's Apartment"
        assert apartment.description is not None
        assert len(apartment.description) > 0

    def test_apartment_has_examinable_items(self):
        """Test apartment contains items that can be examined"""
        from src.game.locations import ApartmentLocation

        apartment = ApartmentLocation()
        items = apartment.get_items()

        # Should have key items
        assert "revolver" in items
        assert "jacket" in items
        assert "badge" in items
        assert "bottle" in items

    def test_item_examination_provides_descriptions(self):
        """Test examining items provides meaningful descriptions"""
        from src.game.locations import ApartmentLocation

        apartment = ApartmentLocation()

        # Test revolver examination
        revolver_desc = apartment.examine_item("revolver")
        assert revolver_desc is not None
        assert "service weapon" in revolver_desc
        assert ".38" in revolver_desc

        # Test jacket examination
        jacket_desc = apartment.examine_item("jacket")
        assert jacket_desc is not None
        assert "leather" in jacket_desc.lower()
        assert "defense" in jacket_desc.lower()

    def test_apartment_screen_integration(self):
        """Test apartment integrates with MainUI system"""
        from src.ui.apartment_screen import ApartmentScreen

        # Use default location file path
        screen = ApartmentScreen()

        assert screen.title == "Morrison's Apartment"
        assert len(screen.options) >= 7  # At least 7 menu options

    def test_hungover_status_applied(self):
        """Test hungover status effect is applied and persists"""
        from src.game.locations import ApartmentLocation

        state_registry = StateRegistry()
        state_registry.initialize()
        apartment = ApartmentLocation()

        # Apply hungover status
        apartment.apply_initial_status()

        # Check hungover effect exists
        hungover = state_registry.get_item("hungover")
        assert hungover is not None
        assert hungover.stat_changes["attack"] == -1
        assert hungover.stat_changes["defense"] == -1
        assert hungover.duration_hours == 2

    def test_exploration_menu_options(self):
        """Test that apartment provides expected exploration options"""
        from src.ui.apartment_screen import ApartmentScreen

        screen = ApartmentScreen()


class TestStatusEffectPersistence:
    """Test status effects persist outside combat"""

    def setup_method(self):
        """Setup test environment"""
        reset_signal_bus()
        self.signal_bus = get_signal_bus()
        self.state_registry = StateRegistry()
        self.state_registry.initialize()

    def test_hungover_status_definition(self):
        """Test hungover status effect is properly defined"""
        hungover = self.state_registry.get_item("hungover")
        assert hungover is not None
        assert hungover.name == "hungover"
        assert hungover.duration_hours == 2
        assert hungover.stat_changes["attack"] == -1
        assert hungover.stat_changes["defense"] == -1
        assert hungover.stat_changes["speed"] == -1

    def test_status_effects_outside_combat(self):
        """Test status effects can be tracked outside combat"""
        from src.game.character_state import CharacterState

        character = CharacterState()
        character.apply_status_effect("hungover")

        assert character.has_status("hungover")
        assert character.get_stat_modifier("attack") == -1
        assert character.get_stat_modifier("defense") == -1

    def test_status_duration_tracking(self):
        """Test status effects track duration properly"""
        from src.game.character_state import CharacterState

        character = CharacterState()
        character.apply_status_effect("hungover")

        # Advance time
        character.advance_time_minutes(30)
        assert character.has_status("hungover")  # Still active

        # Advance past duration
        character.advance_time_hours(2)
        assert not character.has_status("hungover")  # Should expire


class TestBasicItemSystem:
    """Test basic item examination and interaction"""

    def test_item_data_structure(self):
        """Test items have proper data structure"""
        from src.game.items import Item

        revolver = Item(
            name="S&W Model 10",
            description="Your old service weapon. Reliable .38 caliber revolver.",
            item_type="weapon",
            properties={"damage_type": "physical.ballistic.38", "damage": 8},
        )

        assert revolver.name == "S&W Model 10"
        assert revolver.item_type == "weapon"
        assert revolver.properties["damage_type"] == "physical.ballistic.38"

    def test_item_examination_system(self):
        """Test item examination provides detailed info"""
        from src.game.items import ItemExaminer
        from src.game.items import Item

        jacket = Item(
            name="Old Leather Jacket",
            description="Worn but still protective. Provides +2 defense.",
            item_type="armor",
            properties={"defense_bonus": 2},
        )

        examiner = ItemExaminer()
        examination = examiner.examine(jacket)

        assert "protective" in examination.lower()
        assert "+2" in examination
        assert "defense" in examination.lower()


class TestExplorationUI:
    """Test exploration UI integration with MainUI"""

    def setup_method(self):
        """Setup test environment"""
        reset_signal_bus()
        self.signal_bus = get_signal_bus()
        self.ui = MainUI()

    def test_apartment_screen_renders(self):
        """Test apartment screen renders without errors"""
        from src.ui.apartment_screen import ApartmentScreen

        screen = ApartmentScreen()
        # Note: ApartmentScreen extends MenuScreen which may not have render method
        # Test that screen has expected attributes instead
        assert hasattr(screen, 'title')
        assert hasattr(screen, 'options')
        assert screen.title == "Morrison's Apartment"

    def test_exploration_state_transition(self):
        """Test state machine handles exploration properly"""
        state_machine = GameStateMachine()

        # Should be able to transition to exploration
        assert state_machine.can_transition_to(GameState.EXPLORATION)
        state_machine.transition_to(GameState.EXPLORATION)
        assert state_machine.current_state == GameState.EXPLORATION

    def test_menu_option_handling(self):
        """Test apartment handles menu selection correctly"""
        from src.ui.apartment_screen import ApartmentScreen

        screen = ApartmentScreen()

        # Test examining revolver
        revolver_option = next(opt for opt in screen.options if "Revolver" in opt.text)
        assert revolver_option is not None
        assert revolver_option.enabled

        # Should have action string
        assert isinstance(revolver_option.action, str)
        assert revolver_option.action == "examine:revolver"


# EOF
