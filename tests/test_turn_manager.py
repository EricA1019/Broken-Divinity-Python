"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Turn Manager Tests                                                          ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Test suite for turn-based combat initiative system         ║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.9                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pytest
from unittest.mock import Mock, patch
from typing import List

from src.game.turn_manager import TurnManager, TurnOrder, CombatAction
from src.game.battle_manager import CombatEntity


class TestTurnOrder:
    """Test TurnOrder data structure."""

    def test_turn_order_creation(self):
        """Test basic turn order creation."""
        entity = Mock()
        entity.name = "Detective"
        entity.speed = 14

        turn_order = TurnOrder(entity=entity, initiative=18)

        assert turn_order.entity == entity
        assert turn_order.initiative == 18

    def test_turn_order_comparison(self):
        """Test turn order sorting by initiative."""
        entity1 = Mock()
        entity1.name = "Detective"
        entity1.speed = 14

        entity2 = Mock()
        entity2.name = "Thug"
        entity2.speed = 10

        turn1 = TurnOrder(entity=entity1, initiative=18)
        turn2 = TurnOrder(entity=entity2, initiative=15)

        # Higher initiative should come first
        assert turn1 > turn2
        assert turn2 < turn1


class TestCombatAction:
    """Test CombatAction data structure."""

    def test_combat_action_creation(self):
        """Test basic combat action creation."""
        action = CombatAction(
            action_type="attack",
            actor_name="Detective",
            target_name="Thug",
            damage=8,
            description="Detective attacks Thug for 8 damage",
        )

        assert action.action_type == "attack"
        assert action.actor_name == "Detective"
        assert action.target_name == "Thug"
        assert action.damage == 8


class TestTurnManager:
    """Test TurnManager combat turn system."""

    def test_turn_manager_initialization(self):
        """Test turn manager initialization."""
        manager = TurnManager()
        assert len(manager.turn_order) == 0
        assert manager.current_turn_index == 0
        assert manager.turn_number == 0

    def test_calculate_initiative(self):
        """Test initiative calculation from entity speed."""
        manager = TurnManager()

        entity = Mock()
        entity.speed = 14
        entity.name = "Detective"

        with patch("random.randint", return_value=5):
            initiative = manager.calculate_initiative(entity)
            # Should be speed (14) + random roll (5) = 19
            assert initiative == 19

    def test_setup_turn_order(self):
        """Test setting up turn order for battle participants."""
        manager = TurnManager()

        player = Mock()
        player.name = "Detective"
        player.speed = 14
        player.is_alive.return_value = True

        enemy1 = Mock()
        enemy1.name = "Thug1"
        enemy1.speed = 10
        enemy1.is_alive.return_value = True

        enemy2 = Mock()
        enemy2.name = "Thug2"
        enemy2.speed = 12
        enemy2.is_alive.return_value = True

        entities = [player, enemy1, enemy2]

        with patch("random.randint") as mock_random:
            # Mock initiative rolls: Detective=6, Thug1=3, Thug2=4
            mock_random.side_effect = [6, 3, 4]

            manager.setup_turn_order(entities)

            # Should be sorted by initiative: Detective(20), Thug2(16), Thug1(13)
            assert len(manager.turn_order) == 3
            assert manager.turn_order[0].entity.name == "Detective"
            assert manager.turn_order[1].entity.name == "Thug2"
            assert manager.turn_order[2].entity.name == "Thug1"

    def test_get_current_actor(self):
        """Test getting current turn actor."""
        manager = TurnManager()

        entity1 = Mock()
        entity1.name = "Detective"
        entity1.speed = 14

        entity2 = Mock()
        entity2.name = "Thug"
        entity2.speed = 10

        manager.turn_order = [
            TurnOrder(entity=entity1, initiative=20),
            TurnOrder(entity=entity2, initiative=15),
        ]

        # First turn should be Detective
        current_actor = manager.get_current_actor()
        assert current_actor.name == "Detective"

    def test_advance_turn(self):
        """Test advancing to next turn."""
        manager = TurnManager()

        entity1 = Mock()
        entity1.name = "Detective"
        entity1.speed = 14

        entity2 = Mock()
        entity2.name = "Thug"
        entity2.speed = 10

        manager.turn_order = [
            TurnOrder(entity=entity1, initiative=20),
            TurnOrder(entity=entity2, initiative=15),
        ]

        # Start with Detective (index 0)
        assert manager.current_turn_index == 0

        # Advance to Thug (index 1)
        manager.advance_turn()
        assert manager.current_turn_index == 1
        current_actor = manager.get_current_actor()
        assert current_actor.name == "Thug"

        # Advance back to Detective (index 0) and increment turn number
        manager.advance_turn()
        assert manager.current_turn_index == 0
        assert manager.turn_number == 1
        current_actor = manager.get_current_actor()
        assert current_actor.name == "Detective"

    def test_is_player_turn(self):
        """Test checking if it's the player's turn."""
        manager = TurnManager()

        player = Mock()
        player.name = "Detective"
        player.entity_type = "player"
        player.speed = 14

        enemy = Mock()
        enemy.name = "Thug"
        enemy.entity_type = "enemy"
        enemy.speed = 10

        manager.turn_order = [
            TurnOrder(entity=player, initiative=20),
            TurnOrder(entity=enemy, initiative=15),
        ]

        # Should be player turn at index 0
        assert manager.is_player_turn()

        # Advance to enemy turn
        manager.advance_turn()
        assert not manager.is_player_turn()

    def test_skip_dead_entities(self):
        """Test skipping dead entities in turn order."""
        manager = TurnManager()

        player = Mock()
        player.name = "Detective"
        player.entity_type = "player"
        player.speed = 14
        player.is_alive.return_value = True

        dead_enemy = Mock()
        dead_enemy.name = "DeadThug"
        dead_enemy.entity_type = "enemy"
        dead_enemy.speed = 12
        dead_enemy.is_alive.return_value = False

        alive_enemy = Mock()
        alive_enemy.name = "AliveThug"
        alive_enemy.entity_type = "enemy"
        alive_enemy.speed = 10
        alive_enemy.is_alive.return_value = True

        manager.turn_order = [
            TurnOrder(entity=player, initiative=20),
            TurnOrder(entity=dead_enemy, initiative=16),
            TurnOrder(entity=alive_enemy, initiative=15),
        ]

        # Start with player (alive)
        current_actor = manager.get_current_actor()
        assert current_actor.name == "Detective"

        # Advance should skip dead enemy and go to alive enemy
        manager.advance_turn()
        current_actor = manager.get_current_actor()
        assert current_actor.name == "AliveThug"

    def test_record_action(self):
        """Test recording combat actions."""
        manager = TurnManager()

        action = CombatAction(
            action_type="attack",
            actor_name="Detective",
            target_name="Thug",
            damage=8,
            description="Detective attacks Thug for 8 damage",
        )

        manager.record_action(action)

        assert len(manager.action_history) == 1
        assert manager.action_history[0] == action

    def test_get_recent_actions(self):
        """Test getting recent combat actions."""
        manager = TurnManager()

        # Add multiple actions
        for i in range(5):
            action = CombatAction(
                action_type="attack",
                actor_name=f"Actor{i}",
                target_name=f"Target{i}",
                damage=i,
                description=f"Action {i}",
            )
            manager.record_action(action)

        # Get last 3 actions
        recent = manager.get_recent_actions(3)
        assert len(recent) == 3
        assert recent[0].description == "Action 4"  # Most recent first
        assert recent[2].description == "Action 2"


# EOF
