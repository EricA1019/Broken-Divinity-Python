"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  BuffRegistry Tests                                                          ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Comprehensive tests for BuffRegistry and Buff dataclass    ║
║  Last-Updated  : 2025-08-03                                                 ║
║  Version       : v0.0.4                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List

from src.game.buff_registry import BuffRegistry, Buff
from src.core.signals import CoreSignal, get_signal_bus, reset_signal_bus


class TestBuff(unittest.TestCase):
    """Test the Buff dataclass functionality."""

    def test_buff_dataclass_creation(self):
        """Test basic Buff dataclass creation."""
        buff = Buff(
            id="defense_boost",
            name="Defense Boost",
            description="Increases defense rating",
            stat_modifiers={"defense": 5},
            default_duration=3,
            max_stacks=2,
        )

        self.assertEqual(buff.id, "defense_boost")
        self.assertEqual(buff.name, "Defense Boost")
        self.assertEqual(buff.stat_modifiers["defense"], 5)
        self.assertEqual(buff.default_duration, 3)
        self.assertEqual(buff.max_stacks, 2)
        self.assertEqual(buff.buff_type, "temporary")  # default
        self.assertFalse(buff.is_permanent)  # default

    def test_permanent_buff_creation(self):
        """Test permanent buff creation."""
        buff = Buff(
            id="strength_training",
            name="Strength Training",
            description="Permanent strength increase",
            stat_modifiers={"attack": 2},
            buff_type="permanent",
            is_permanent=True,
        )

        self.assertEqual(buff.buff_type, "permanent")
        self.assertTrue(buff.is_permanent)
        self.assertEqual(buff.default_duration, -1)  # permanent
        self.assertEqual(buff.max_stacks, 999)  # high default for permanent

    def test_buff_stat_calculation(self):
        """Test buff stat modifier calculations."""
        buff = Buff(
            id="combat_expertise",
            name="Combat Expertise",
            description="Improves attack and defense",
            stat_modifiers={"attack": 3, "defense": 2, "speed": 1},
            max_stacks=3,
        )

        # Test single stack
        total_mods = buff.calculate_total_modifiers(1)
        self.assertEqual(total_mods["attack"], 3)
        self.assertEqual(total_mods["defense"], 2)
        self.assertEqual(total_mods["speed"], 1)

        # Test multiple stacks
        total_mods = buff.calculate_total_modifiers(2)
        self.assertEqual(total_mods["attack"], 6)
        self.assertEqual(total_mods["defense"], 4)
        self.assertEqual(total_mods["speed"], 2)

    def test_buff_stack_validation(self):
        """Test buff stacking validation."""
        buff = Buff(
            id="haste",
            name="Haste",
            description="Increases speed",
            stat_modifiers={"speed": 5},
            max_stacks=1,
        )

        self.assertTrue(buff.can_stack_to(1))
        self.assertFalse(buff.can_stack_to(2))  # exceeds max_stacks


class TestBuffRegistry(unittest.TestCase):
    """Test the BuffRegistry functionality."""

    def setUp(self):
        """Set up test fixtures."""
        reset_signal_bus()
        self.signal_bus = get_signal_bus()
        self.registry = BuffRegistry()

    def tearDown(self):
        """Clean up after tests."""
        reset_signal_bus()

    def test_registry_initialization(self):
        """Test BuffRegistry initialization."""
        self.assertIsInstance(self.registry, BuffRegistry)
        self.assertEqual(self.registry.registry_name, "Buff")
        self.assertFalse(self.registry.is_initialized())

    def test_load_single_buff(self):
        """Test loading a single buff from JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            buff_file = Path(temp_dir) / "shield_wall.json"
            buff_data = {
                "id": "shield_wall",
                "name": "Shield Wall",
                "description": "Greatly increases defense",
                "stat_modifiers": {"defense": 10},
                "default_duration": 5,
                "max_stacks": 1,
                "buff_type": "temporary",
            }

            with open(buff_file, "w") as f:
                json.dump(buff_data, f)

            self.registry.load_from_directory(Path(temp_dir))

            self.assertTrue(self.registry.is_initialized())
            self.assertEqual(self.registry.get_item_count(), 1)

            buff = self.registry.get_item("shield_wall")
            self.assertIsNotNone(buff)
            self.assertEqual(buff.name, "Shield Wall")
            self.assertEqual(buff.stat_modifiers["defense"], 10)

    def test_load_all_buff_types(self):
        """Test loading multiple buff types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Attack buff
            attack_file = Path(temp_dir) / "rage.json"
            with open(attack_file, "w") as f:
                json.dump(
                    {
                        "id": "rage",
                        "name": "Rage",
                        "description": "Increases attack power",
                        "stat_modifiers": {"attack": 5},
                        "default_duration": 3,
                        "max_stacks": 2,
                    },
                    f,
                )

            # Defense buff
            defense_file = Path(temp_dir) / "armor.json"
            with open(defense_file, "w") as f:
                json.dump(
                    {
                        "id": "armor",
                        "name": "Armor",
                        "description": "Increases defense",
                        "stat_modifiers": {"defense": 3},
                        "default_duration": 5,
                        "max_stacks": 3,
                    },
                    f,
                )

            # Speed buff
            speed_file = Path(temp_dir) / "sprint.json"
            with open(speed_file, "w") as f:
                json.dump(
                    {
                        "id": "sprint",
                        "name": "Sprint",
                        "description": "Increases movement speed",
                        "stat_modifiers": {"speed": 2},
                        "default_duration": 2,
                        "max_stacks": 1,
                    },
                    f,
                )

            self.registry.load_from_directory(Path(temp_dir))

            self.assertEqual(self.registry.get_item_count(), 3)
            self.assertIsNotNone(self.registry.get_item("rage"))
            self.assertIsNotNone(self.registry.get_item("armor"))
            self.assertIsNotNone(self.registry.get_item("sprint"))

    def test_buff_with_missing_optional_fields(self):
        """Test buff loading with missing optional fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            buff_file = Path(temp_dir) / "basic_buff.json"
            buff_data = {
                "id": "basic_buff",
                "name": "Basic Buff",
                "description": "Simple stat boost",
                "stat_modifiers": {"attack": 1},
                # Missing optional fields
            }

            with open(buff_file, "w") as f:
                json.dump(buff_data, f)

            self.registry.load_from_directory(Path(temp_dir))

            buff = self.registry.get_item("basic_buff")
            self.assertIsNotNone(buff)
            self.assertEqual(buff.default_duration, 1)  # default
            self.assertEqual(buff.max_stacks, 1)  # default
            self.assertEqual(buff.buff_type, "temporary")  # default

    def test_permanent_buff_loading(self):
        """Test loading permanent buffs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            buff_file = Path(temp_dir) / "training.json"
            buff_data = {
                "id": "training",
                "name": "Combat Training",
                "description": "Permanent skill improvement",
                "stat_modifiers": {"attack": 1, "defense": 1},
                "buff_type": "permanent",
                "is_permanent": True,
            }

            with open(buff_file, "w") as f:
                json.dump(buff_data, f)

            self.registry.load_from_directory(Path(temp_dir))

            buff = self.registry.get_item("training")
            self.assertIsNotNone(buff)
            self.assertTrue(buff.is_permanent)
            self.assertEqual(buff.buff_type, "permanent")
            self.assertEqual(buff.default_duration, -1)

    def test_signal_emission_on_initialization(self):
        """Test signal emission when registry initializes."""
        signal_received = []

        def signal_handler(signal_data):
            signal_received.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, signal_handler)

        with tempfile.TemporaryDirectory() as temp_dir:
            buff_file = Path(temp_dir) / "test_buff.json"
            with open(buff_file, "w") as f:
                json.dump(
                    {
                        "id": "test_buff",
                        "name": "Test Buff",
                        "description": "Test buff",
                        "stat_modifiers": {"attack": 1},
                    },
                    f,
                )

            self.registry.load_from_directory(Path(temp_dir))

            # Verify signal was emitted
            self.assertEqual(len(signal_received), 1)
            signal_data = signal_received[0]
            self.assertEqual(signal_data.signal_type, CoreSignal.REGISTRY_INITIALIZED)
            self.assertEqual(signal_data.source, "BuffRegistry")
            self.assertEqual(signal_data.data["registry_name"], "buff")
            self.assertEqual(signal_data.data["item_count"], 1)
            self.assertEqual(signal_data.data["error_count"], 0)

    def test_signal_emission_on_error(self):
        """Test signal emission when registry encounters errors."""
        signal_received = []

        def signal_handler(signal_data):
            signal_received.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_ERROR, signal_handler)

        # Try to load from non-existent directory
        non_existent_dir = Path("/non/existent/directory")
        self.registry.load_from_directory(non_existent_dir)

        # Verify error signal was emitted
        self.assertEqual(len(signal_received), 1)
        signal_data = signal_received[0]
        self.assertEqual(signal_data.signal_type, CoreSignal.REGISTRY_ERROR)
        self.assertEqual(signal_data.source, "BuffRegistry")
        self.assertIn("Data directory not found", signal_data.data["error_message"])

    def test_get_buffs_by_type(self):
        """Test filtering buffs by type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temporary buff
            temp_file = Path(temp_dir) / "temp_buff.json"
            with open(temp_file, "w") as f:
                json.dump(
                    {
                        "id": "temp_buff",
                        "name": "Temporary Buff",
                        "description": "Temporary effect",
                        "stat_modifiers": {"attack": 2},
                        "buff_type": "temporary",
                    },
                    f,
                )

            # Permanent buff
            perm_file = Path(temp_dir) / "perm_buff.json"
            with open(perm_file, "w") as f:
                json.dump(
                    {
                        "id": "perm_buff",
                        "name": "Permanent Buff",
                        "description": "Permanent effect",
                        "stat_modifiers": {"defense": 1},
                        "buff_type": "permanent",
                        "is_permanent": True,
                    },
                    f,
                )

            self.registry.load_from_directory(Path(temp_dir))

            temp_buffs = self.registry.get_buffs_by_type("temporary")
            perm_buffs = self.registry.get_buffs_by_type("permanent")

            self.assertEqual(len(temp_buffs), 1)
            self.assertEqual(len(perm_buffs), 1)
            self.assertEqual(temp_buffs[0].id, "temp_buff")
            self.assertEqual(perm_buffs[0].id, "perm_buff")

    def test_get_stat_modifying_buffs(self):
        """Test getting buffs that modify specific stats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Attack buff
            attack_file = Path(temp_dir) / "attack_buff.json"
            with open(attack_file, "w") as f:
                json.dump(
                    {
                        "id": "attack_buff",
                        "name": "Attack Buff",
                        "description": "Boosts attack",
                        "stat_modifiers": {"attack": 3},
                    },
                    f,
                )

            # Defense buff
            defense_file = Path(temp_dir) / "defense_buff.json"
            with open(defense_file, "w") as f:
                json.dump(
                    {
                        "id": "defense_buff",
                        "name": "Defense Buff",
                        "description": "Boosts defense",
                        "stat_modifiers": {"defense": 2},
                    },
                    f,
                )

            # Multi-stat buff
            multi_file = Path(temp_dir) / "multi_buff.json"
            with open(multi_file, "w") as f:
                json.dump(
                    {
                        "id": "multi_buff",
                        "name": "Multi Buff",
                        "description": "Boosts multiple stats",
                        "stat_modifiers": {"attack": 1, "defense": 1},
                    },
                    f,
                )

            self.registry.load_from_directory(Path(temp_dir))

            attack_buffs = self.registry.get_stat_modifying_buffs("attack")
            defense_buffs = self.registry.get_stat_modifying_buffs("defense")

            self.assertEqual(len(attack_buffs), 2)  # attack_buff + multi_buff
            self.assertEqual(len(defense_buffs), 2)  # defense_buff + multi_buff

    def test_real_data_loading(self):
        """Test loading from actual data directory."""
        # This will test against the real data files we'll create
        data_dir = Path("data/buffs")
        if data_dir.exists():
            self.registry.initialize()
            self.assertTrue(self.registry.is_initialized())
            self.assertGreater(self.registry.get_item_count(), 0)


if __name__ == "__main__":
    unittest.main()

# EOF
