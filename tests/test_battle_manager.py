"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Battle Manager Tests                                                        ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Test suite for combat battle management system             ║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.9                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List, Optional

from src.game.battle_manager import BattleManager, CombatEntity, BattleResult
from src.game.entity_registry import EntityRegistry
from src.core.signals import get_signal_bus, CoreSignal


class TestCombatEntity:
    """Test CombatEntity data structure."""

    def test_combat_entity_creation(self):
        """Test basic combat entity creation."""
        entity = CombatEntity(
            name="Detective",
            entity_type="player",
            max_hp=20,
            current_hp=20,
            max_mana=10,
            current_mana=10,
            attack=12,
            defense=8,
            speed=14,
        )

        assert entity.name == "Detective"
        assert entity.max_hp == 20
        assert entity.current_hp == 20
        assert entity.is_alive()
        assert not entity.is_dead()

    def test_combat_entity_damage(self):
        """Test combat entity damage application."""
        entity = CombatEntity(
            name="Thug",
            entity_type="enemy",
            max_hp=15,
            current_hp=15,
            max_mana=0,
            current_mana=0,
            attack=8,
            defense=3,
            speed=10,
        )

        entity.take_damage(5)
        assert entity.current_hp == 10
        assert entity.is_alive()

        entity.take_damage(10)
        assert entity.current_hp == 0
        assert entity.is_dead()

    def test_combat_entity_healing(self):
        """Test combat entity healing."""
        entity = CombatEntity(
            name="Detective",
            entity_type="player",
            max_hp=20,
            current_hp=10,
            max_mana=10,
            current_mana=5,
            attack=12,
            defense=8,
            speed=14,
        )

        entity.heal(5)
        assert entity.current_hp == 15

        entity.heal(10)  # Should cap at max_hp
        assert entity.current_hp == 20

    def test_combat_entity_mana_usage(self):
        """Test combat entity mana consumption."""
        entity = CombatEntity(
            name="Detective",
            entity_type="player",
            max_hp=20,
            current_hp=20,
            max_mana=10,
            current_mana=10,
            attack=12,
            defense=8,
            speed=14,
        )

        assert entity.can_spend_mana(5)
        entity.spend_mana(5)
        assert entity.current_mana == 5

        assert not entity.can_spend_mana(10)


class TestBattleManager:
    """Test BattleManager combat system."""

    def test_battle_manager_initialization(self):
        """Test battle manager initialization."""
        manager = BattleManager()
        assert manager.player is None
        assert len(manager.enemies) == 0
        assert not manager.is_battle_active()

    def test_start_battle_with_entities(self):
        """Test starting battle with player and enemies."""
        manager = BattleManager()

        player = CombatEntity(
            name="Detective",
            entity_type="player",
            max_hp=20,
            current_hp=20,
            max_mana=10,
            current_mana=10,
            attack=12,
            defense=8,
            speed=14,
        )

        enemy = CombatEntity(
            name="Thug",
            entity_type="enemy",
            max_hp=15,
            current_hp=15,
            max_mana=0,
            current_mana=0,
            attack=8,
            defense=3,
            speed=10,
        )

        manager.start_battle(player, [enemy])

        assert manager.is_battle_active()
        assert manager.player == player
        assert len(manager.enemies) == 1
        assert manager.enemies[0] == enemy

    def test_battle_from_registry_entities(self):
        """Test creating battle from registry entity definitions."""
        with patch("src.game.battle_manager.EntityRegistry") as mock_registry_class:
            mock_registry = Mock()
            mock_registry_class.return_value = mock_registry

            # Mock detective entity
            detective_data = Mock()
            detective_data.name = "detective"
            detective_data.hp = 20
            detective_data.mana = 10
            detective_data.attack = 12
            detective_data.defense = 8
            detective_data.speed = 14
            detective_data.entity_type = "player"

            # Mock thug entity
            thug_data = Mock()
            thug_data.name = "thug"
            thug_data.hp = 15
            thug_data.mana = 0
            thug_data.attack = 8
            thug_data.defense = 3
            thug_data.speed = 10
            thug_data.entity_type = "enemy"

            mock_registry.get_item.side_effect = lambda name: {
                "detective": detective_data,
                "thug": thug_data,
            }.get(name)

            manager = BattleManager()
            manager.start_battle_from_registry("detective", ["thug"])

            assert manager.is_battle_active()
            assert manager.player.name == "detective"
            assert len(manager.enemies) == 1
            assert manager.enemies[0].name == "thug"

    def test_battle_victory_condition(self):
        """Test battle victory when all enemies defeated."""
        manager = BattleManager()

        player = CombatEntity(
            name="Detective",
            entity_type="player",
            max_hp=20,
            current_hp=20,
            max_mana=10,
            current_mana=10,
            attack=12,
            defense=8,
            speed=14,
        )

        enemy = CombatEntity(
            name="Thug",
            entity_type="enemy",
            max_hp=15,
            current_hp=1,  # Almost dead
            max_mana=0,
            current_mana=0,
            attack=8,
            defense=3,
            speed=10,
        )

        manager.start_battle(player, [enemy])

        # Kill the enemy
        enemy.take_damage(10)

        result = manager.check_battle_end()
        assert result == BattleResult.VICTORY
        assert not manager.is_battle_active()

    def test_battle_defeat_condition(self):
        """Test battle defeat when player dies."""
        manager = BattleManager()

        player = CombatEntity(
            name="Detective",
            entity_type="player",
            max_hp=20,
            current_hp=1,  # Almost dead
            max_mana=10,
            current_mana=10,
            attack=12,
            defense=8,
            speed=14,
        )

        enemy = CombatEntity(
            name="Thug",
            entity_type="enemy",
            max_hp=15,
            current_hp=15,
            max_mana=0,
            current_mana=0,
            attack=8,
            defense=3,
            speed=10,
        )

        manager.start_battle(player, [enemy])

        # Kill the player
        player.take_damage(10)

        result = manager.check_battle_end()
        assert result == BattleResult.DEFEAT
        assert not manager.is_battle_active()

    def test_get_living_enemies(self):
        """Test getting only living enemies."""
        manager = BattleManager()

        player = CombatEntity(
            name="Detective",
            entity_type="player",
            max_hp=20,
            current_hp=20,
            max_mana=10,
            current_mana=10,
            attack=12,
            defense=8,
            speed=14,
        )

        enemy1 = CombatEntity(
            name="Thug1",
            entity_type="enemy",
            max_hp=15,
            current_hp=15,
            max_mana=0,
            current_mana=0,
            attack=8,
            defense=3,
            speed=10,
        )

        enemy2 = CombatEntity(
            name="Thug2",
            entity_type="enemy",
            max_hp=15,
            current_hp=0,  # Dead
            max_mana=0,
            current_mana=0,
            attack=8,
            defense=3,
            speed=10,
        )

        manager.start_battle(player, [enemy1, enemy2])

        living_enemies = manager.get_living_enemies()
        assert len(living_enemies) == 1
        assert living_enemies[0].name == "Thug1"


# EOF
