"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Combat Screen Integration Tests                                             ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Test live combat screen functionality                      ║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.10                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from src.game.game_state_machine import GameStateMachine, GameState
from src.game.battle_manager import BattleManager, BattleResult
from src.game.turn_manager import TurnManager
from src.ui.main_ui import MenuScreen, StatusData
from src.core.signals import get_signal_bus, reset_signal_bus


class TestCombatScreenIntegration:
    """Test live combat screen integration."""

    def setup_method(self):
        """Setup for each test."""
        reset_signal_bus()
        self.state_machine = GameStateMachine()
        self.battle_manager = BattleManager()
        self.turn_manager = TurnManager()

    def test_combat_screen_creation_with_entities(self):
        """Test combat screen shows real entity data."""
        # Setup battle with detective vs imp using battle manager's from_registry method
        success = self.battle_manager.start_battle_from_registry("detective", ["imp"])
        assert success is True

        # Verify entities were created
        assert self.battle_manager.player is not None
        assert self.battle_manager.player.name == "Detective"
        assert len(self.battle_manager.enemies) == 1
        assert self.battle_manager.enemies[0].name == "Imp"

        # Setup turn order (filter out None values)
        all_entities = [
            e
            for e in [self.battle_manager.player] + self.battle_manager.enemies
            if e is not None
        ]
        self.turn_manager.setup_turn_order(all_entities)

        # Get combat screen
        screen = self.state_machine.get_current_screen()
        assert isinstance(screen, MenuScreen)

    def test_imp_has_infernal_abilities_data(self):
        """Test imp entity data loads correctly."""
        success = self.battle_manager.start_battle_from_registry("detective", ["imp"])
        assert success is True

        imp = self.battle_manager.enemies[0]
        assert imp is not None
        assert imp.name == "Imp"

        # Check that imp has expected stats
        assert imp.max_hp == 12
        assert imp.max_mana == 15
        assert imp.speed == 16

    def test_combat_flow_with_imp(self):
        """Test complete combat flow with imp enemy."""
        # Start battle using registry
        success = self.battle_manager.start_battle_from_registry("detective", ["imp"])
        assert success is True

        # Setup turn order
        all_entities = [
            e
            for e in [self.battle_manager.player] + self.battle_manager.enemies
            if e is not None
        ]
        self.turn_manager.setup_turn_order(all_entities)

        # Verify battle is active
        assert self.battle_manager.is_battle_active() is True
        assert len(self.turn_manager.turn_order) == 2

        # Check turn order includes both entities
        entities = [entry.entity for entry in self.turn_manager.turn_order]
        entity_names = [e.name for e in entities]
        assert "Detective" in entity_names
        assert "Imp" in entity_names

    def test_state_machine_combat_transition(self):
        """Test state machine can transition to combat with entities."""
        # Start in exploration
        assert self.state_machine.current_state == GameState.MAIN_MENU

        # Transition to exploration then combat
        self.state_machine.transition_to(GameState.EXPLORATION)
        assert self.state_machine.current_state == GameState.EXPLORATION

        self.state_machine.transition_to(GameState.COMBAT)
        assert self.state_machine.current_state == GameState.COMBAT

        # Get combat screen
        screen = self.state_machine.get_current_screen()
        assert screen.title == "Combat Encounter"


class TestCombatScreenDisplay:
    """Test combat screen visual layout and data display."""

    def setup_method(self):
        """Setup for each test."""
        reset_signal_bus()
        self.state_machine = GameStateMachine()

    def test_combat_screen_shows_entity_status(self):
        """Test combat screen displays entity HP/mana."""
        self.state_machine.transition_to(GameState.COMBAT)
        screen = self.state_machine.get_current_screen()

        # Screen should have status data
        assert isinstance(screen.status, StatusData)
        assert screen.status.location == "Combat Encounter"

    def test_combat_options_available(self):
        """Test combat screen has proper menu options."""
        self.state_machine.transition_to(GameState.COMBAT)
        screen = self.state_machine.get_current_screen()

        option_texts = [opt.text for opt in screen.options]
        assert "Attack" in option_texts
        assert "Use Ability" in option_texts
        assert "Defend" in option_texts

    def test_combat_screen_menu_actions(self):
        """Test combat screen responds to menu actions."""
        self.state_machine.transition_to(GameState.COMBAT)

        # Test action handling
        result = self.state_machine.handle_menu_action("9")  # End Combat
        assert result is True  # Should handle the action

        # Should transition back to exploration
        assert self.state_machine.current_state == GameState.EXPLORATION


class TestInfernalAbilities:
    """Test infernal abilities integration."""

    def setup_method(self):
        """Setup for each test."""
        reset_signal_bus()

    def test_infernal_bolt_ability_loaded(self):
        """Test infernal bolt ability loads correctly."""
        from src.game.abilities import AbilityRegistry

        registry = AbilityRegistry()
        data_path = Path("data/abilities")
        registry.load_from_directory(data_path)

        ability = registry.get_item("infernal_bolt")
        assert ability is not None
        assert ability.name == "Infernal Bolt"
        assert ability.type == "attack"

    def test_shadow_step_ability_loaded(self):
        """Test shadow step ability loads correctly."""
        from src.game.abilities import AbilityRegistry

        registry = AbilityRegistry()
        data_path = Path("data/abilities")
        registry.load_from_directory(data_path)

        ability = registry.get_item("shadow_step")
        assert ability is not None
        assert ability.name == "Shadow Step"
        assert ability.targeting == "self"

    def test_minor_curse_ability_loaded(self):
        """Test minor curse ability loads correctly."""
        from src.game.abilities import AbilityRegistry

        registry = AbilityRegistry()
        data_path = Path("data/abilities")
        registry.load_from_directory(data_path)

        ability = registry.get_item("minor_curse")
        assert ability is not None
        assert ability.name == "Minor Curse"
        assert ability.type == "attack" or ability.type == "utility"

    def test_burn_status_effect_loaded(self):
        """Test burn status effect loads correctly."""
        from src.game.state_registry import StateRegistry

        registry = StateRegistry()
        data_path = Path("data/status_effects")
        registry.load_from_directory(data_path)

        effect = registry.get_item("burn")
        assert effect is not None
        assert effect.display_name == "Burning"

    def test_weakness_status_effect_loaded(self):
        """Test weakness status effect loads correctly."""
        from src.game.state_registry import StateRegistry

        registry = StateRegistry()
        data_path = Path("data/status_effects")
        registry.load_from_directory(data_path)

        effect = registry.get_item("weakness")
        assert effect is not None
        assert effect.display_name == "Weakened"

    def test_evasion_buff_loaded(self):
        """Test evasion buff loads correctly."""
        from src.game.buff_registry import BuffRegistry

        registry = BuffRegistry()
        data_path = Path("data/buffs")
        registry.load_from_directory(data_path)

        buff = registry.get_item("evasion")
        assert buff is not None
        assert buff.display_name == "Evasive"


class TestCombatScreenEnhanced:
    """Test enhanced combat screen functionality for live demo."""

    def setup_method(self):
        """Setup for each test."""
        reset_signal_bus()
        self.state_machine = GameStateMachine()
        self.battle_manager = BattleManager()

    def test_enhanced_combat_screen_creation(self):
        """Test enhanced combat screen with real entity data."""
        # Start battle for context
        self.battle_manager.start_battle_from_registry("detective", ["imp"])

        # This will test the enhanced _create_combat_screen method
        self.state_machine.transition_to(GameState.COMBAT)
        screen = self.state_machine.get_current_screen()

        assert "Combat" in screen.title

    def test_combat_screen_entity_display(self):
        """Test combat screen shows entity status."""
        # Start battle for context
        self.battle_manager.start_battle_from_registry("detective", ["imp"])

        self.state_machine.transition_to(GameState.COMBAT)
        screen = self.state_machine.get_current_screen()

        # Should show entity information in description
        description = screen.description
        assert len(description) > 0  # Should have some description

    def test_combat_action_feedback(self):
        """Test combat screen provides action feedback."""
        self.state_machine.transition_to(GameState.COMBAT)
        screen = self.state_machine.get_current_screen()

        # Should have action feedback area
        assert len(screen.description) > 50  # Rich description with combat info


# EOF
