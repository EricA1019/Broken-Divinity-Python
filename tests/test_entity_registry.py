"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  EntityRegistry Tests - Comprehensive Test Suite                            ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Test entity data management and stat calculations          ║
║  Last-Updated  : 2025-08-03                                                 ║
║  Version       : v0.0.5                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import unittest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any

from src.game.entity_registry import Entity, EntityRegistry
from src.core.signals import CoreSignal, get_signal_bus, reset_signal_bus


class TestEntity(unittest.TestCase):
    """Test Entity dataclass functionality."""

    def test_entity_dataclass_creation(self):
        """Test basic Entity creation with required fields."""
        entity = Entity(
            id="detective",
            name="Detective",
            description="Experienced investigator",
            entity_type="player",
        )

        self.assertEqual(entity.id, "detective")
        self.assertEqual(entity.name, "Detective")
        self.assertEqual(entity.description, "Experienced investigator")
        self.assertEqual(entity.entity_type, "player")

        # Test default stats
        self.assertEqual(entity.base_health, 100)
        self.assertEqual(entity.base_attack, 10)
        self.assertEqual(entity.base_defense, 10)
        self.assertEqual(entity.base_speed, 10)
        self.assertEqual(entity.base_mana, 50)
        self.assertEqual(entity.flee_chance, 0.0)
        self.assertFalse(entity.is_boss)
        self.assertFalse(entity.is_elite)

    def test_entity_custom_stats(self):
        """Test Entity creation with custom stat values."""
        entity = Entity(
            id="tank_boss",
            name="Iron Colossus",
            description="Massive mechanical guardian",
            entity_type="boss",
            base_health=500,
            base_attack=25,
            base_defense=30,
            base_speed=5,
            base_mana=0,
            flee_chance=0.0,
            is_boss=True,
            immunities=["stun", "bleed"],
        )

        self.assertEqual(entity.base_health, 500)
        self.assertEqual(entity.base_attack, 25)
        self.assertEqual(entity.base_defense, 30)
        self.assertEqual(entity.base_speed, 5)
        self.assertEqual(entity.base_mana, 0)
        self.assertTrue(entity.is_boss)
        self.assertIn("stun", entity.immunities)
        self.assertIn("bleed", entity.immunities)

    def test_entity_stat_calculation(self):
        """Test stat calculations with modifiers."""
        entity = Entity(
            id="soldier",
            name="Elite Soldier",
            description="Well-trained combatant",
            entity_type="elite",
            base_attack=15,
            base_defense=12,
        )

        # Test base stats without modifiers
        stats = entity.calculate_stats()
        self.assertEqual(stats["attack"], 15)
        self.assertEqual(stats["defense"], 12)

        # Test stats with modifiers
        modifiers = {"attack": 5, "defense": -2, "speed": 3}
        modified_stats = entity.calculate_stats(modifiers)
        self.assertEqual(modified_stats["attack"], 20)
        self.assertEqual(modified_stats["defense"], 10)
        self.assertEqual(modified_stats["speed"], 13)  # 10 base + 3 modifier

    def test_entity_flee_chance_calculation(self):
        """Test flee chance calculations based on health."""
        entity = Entity(
            id="coward",
            name="Weak Bandit",
            description="Low-health enemy",
            entity_type="normal",
            flee_chance=0.3,
        )

        # At full health, use base flee chance
        chance = entity.calculate_flee_chance(100, 100)
        self.assertAlmostEqual(chance, 0.3, places=2)

        # At 25% health, flee chance should increase
        chance = entity.calculate_flee_chance(25, 100)
        self.assertGreater(chance, 0.3)
        self.assertLessEqual(chance, 1.0)

        # Bosses never flee regardless of health
        boss = Entity(
            id="boss",
            name="Final Boss",
            description="Never retreats",
            entity_type="boss",
            is_boss=True,
            flee_chance=0.5,
        )
        chance = boss.calculate_flee_chance(1, 100)
        self.assertEqual(chance, 0.0)

    def test_entity_immunity_check(self):
        """Test immunity system for status effects."""
        entity = Entity(
            id="immune_enemy",
            name="Poison Immunity",
            description="Cannot be poisoned",
            entity_type="elite",
            immunities=["poison", "bleed"],
        )

        self.assertTrue(entity.is_immune_to("poison"))
        self.assertTrue(entity.is_immune_to("bleed"))
        self.assertFalse(entity.is_immune_to("stun"))
        self.assertFalse(entity.is_immune_to("slow"))


class TestEntityRegistry(unittest.TestCase):
    """Test EntityRegistry functionality."""

    def setUp(self):
        """Set up test environment with clean signal bus."""
        reset_signal_bus()
        self.signal_bus = get_signal_bus()

        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.entities_path = Path(self.temp_dir) / "entities"
        self.entities_path.mkdir()

    def test_registry_initialization(self):
        """Test EntityRegistry initialization."""
        registry = EntityRegistry(self.entities_path)
        self.assertEqual(registry.registry_name, "Entity")
        self.assertEqual(len(registry.get_all_items()), 0)

    def test_load_single_entity(self):
        """Test loading a single entity from JSON."""
        entity_data = {
            "id": "detective",
            "name": "Detective",
            "description": "Experienced investigator",
            "entity_type": "player",
            "base_health": 120,
            "base_attack": 12,
            "base_defense": 8,
            "base_speed": 15,
            "base_mana": 75,
        }

        entity_file = self.entities_path / "detective.json"
        with open(entity_file, "w") as f:
            json.dump(entity_data, f)

        registry = EntityRegistry(self.entities_path)
        registry.initialize()

        detective = registry.get_item("detective")
        self.assertIsNotNone(detective)
        self.assertEqual(detective.name, "Detective")
        self.assertEqual(detective.base_health, 120)
        self.assertEqual(detective.base_attack, 12)
        self.assertEqual(detective.entity_type, "player")

    def test_load_multiple_entity_types(self):
        """Test loading different entity types."""
        entities = [
            {
                "id": "detective",
                "name": "Detective",
                "description": "Player character",
                "entity_type": "player",
                "base_health": 100,
            },
            {
                "id": "goblin",
                "name": "Goblin Scout",
                "description": "Weak but fast enemy",
                "entity_type": "normal",
                "base_health": 40,
                "base_speed": 18,
                "flee_chance": 0.4,
            },
            {
                "id": "orc_chief",
                "name": "Orc Chieftain",
                "description": "Powerful elite enemy",
                "entity_type": "elite",
                "base_health": 200,
                "base_attack": 20,
                "is_elite": True,
                "immunities": ["stun"],
            },
            {
                "id": "dragon",
                "name": "Ancient Dragon",
                "description": "Legendary boss creature",
                "entity_type": "boss",
                "base_health": 800,
                "base_attack": 35,
                "base_defense": 25,
                "is_boss": True,
                "immunities": ["poison", "bleed", "stun"],
            },
        ]

        for entity in entities:
            entity_file = self.entities_path / f"{entity['id']}.json"
            with open(entity_file, "w") as f:
                json.dump(entity, f)

        registry = EntityRegistry(self.entities_path)
        registry.initialize()

        # Test all entities loaded
        self.assertEqual(len(registry.get_all_items()), 4)

        # Test specific entities
        detective = registry.get_item("detective")
        self.assertEqual(detective.entity_type, "player")

        goblin = registry.get_item("goblin")
        self.assertEqual(goblin.flee_chance, 0.4)

        orc = registry.get_item("orc_chief")
        self.assertTrue(orc.is_elite)
        self.assertIn("stun", orc.immunities)

        dragon = registry.get_item("dragon")
        self.assertTrue(dragon.is_boss)
        self.assertEqual(len(dragon.immunities), 3)

    def test_get_entities_by_type(self):
        """Test filtering entities by type."""
        entities = [
            {
                "id": "player1",
                "name": "Player",
                "description": "PC",
                "entity_type": "player",
            },
            {
                "id": "enemy1",
                "name": "Enemy 1",
                "description": "Normal",
                "entity_type": "normal",
            },
            {
                "id": "enemy2",
                "name": "Enemy 2",
                "description": "Normal",
                "entity_type": "normal",
            },
            {
                "id": "elite1",
                "name": "Elite",
                "description": "Elite",
                "entity_type": "elite",
                "is_elite": True,
            },
            {
                "id": "boss1",
                "name": "Boss",
                "description": "Boss",
                "entity_type": "boss",
                "is_boss": True,
            },
        ]

        for entity in entities:
            entity_file = self.entities_path / f"{entity['id']}.json"
            with open(entity_file, "w") as f:
                json.dump(entity, f)

        registry = EntityRegistry(self.entities_path)
        registry.initialize()

        # Test filtering
        players = registry.get_entities_by_type("player")
        self.assertEqual(len(players), 1)
        self.assertEqual(players[0].id, "player1")

        normals = registry.get_entities_by_type("normal")
        self.assertEqual(len(normals), 2)

        elites = registry.get_entities_by_type("elite")
        self.assertEqual(len(elites), 1)
        self.assertTrue(elites[0].is_elite)

        bosses = registry.get_entities_by_type("boss")
        self.assertEqual(len(bosses), 1)
        self.assertTrue(bosses[0].is_boss)

    def test_get_entities_with_immunity(self):
        """Test finding entities with specific immunities."""
        entities = [
            {
                "id": "normal",
                "name": "Normal",
                "description": "No immunities",
                "entity_type": "normal",
            },
            {
                "id": "poison_immune",
                "name": "Undead",
                "description": "Poison immune",
                "entity_type": "elite",
                "immunities": ["poison"],
            },
            {
                "id": "multi_immune",
                "name": "Golem",
                "description": "Multiple immunities",
                "entity_type": "boss",
                "immunities": ["poison", "bleed", "stun"],
            },
        ]

        for entity in entities:
            entity_file = self.entities_path / f"{entity['id']}.json"
            with open(entity_file, "w") as f:
                json.dump(entity, f)

        registry = EntityRegistry(self.entities_path)
        registry.initialize()

        # Test immunity filtering
        poison_immune = registry.get_entities_with_immunity("poison")
        self.assertEqual(len(poison_immune), 2)

        stun_immune = registry.get_entities_with_immunity("stun")
        self.assertEqual(len(stun_immune), 1)
        self.assertEqual(stun_immune[0].id, "multi_immune")

        nonexistent_immune = registry.get_entities_with_immunity("fake_status")
        self.assertEqual(len(nonexistent_immune), 0)

    def test_entity_with_missing_optional_fields(self):
        """Test entity loading with missing optional fields uses defaults."""
        minimal_entity = {
            "id": "minimal",
            "name": "Minimal Entity",
            "description": "Only required fields",
            "entity_type": "normal",
        }

        entity_file = self.entities_path / "minimal.json"
        with open(entity_file, "w") as f:
            json.dump(minimal_entity, f)

        registry = EntityRegistry(self.entities_path)
        registry.initialize()

        entity = registry.get_item("minimal")
        # Should use default values
        self.assertEqual(entity.base_health, 100)
        self.assertEqual(entity.base_attack, 10)
        self.assertEqual(entity.flee_chance, 0.0)
        self.assertFalse(entity.is_boss)
        self.assertEqual(len(entity.immunities), 0)

    def test_signal_emission_on_initialization(self):
        """Test that EntityRegistry emits signals when initialized."""
        # Create test entity
        entity_data = {
            "id": "test",
            "name": "Test",
            "description": "Test entity",
            "entity_type": "normal",
        }
        entity_file = self.entities_path / "test.json"
        with open(entity_file, "w") as f:
            json.dump(entity_data, f)

        # Listen for initialization signal
        signals_received = []

        def signal_listener(signal_data):
            signals_received.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, signal_listener)

        registry = EntityRegistry(self.entities_path)
        registry.initialize()

        # Verify signal was emitted
        self.assertEqual(len(signals_received), 1)
        self.assertEqual(
            signals_received[0].signal_type, CoreSignal.REGISTRY_INITIALIZED
        )
        self.assertEqual(signals_received[0].source, "EntityRegistry")

    def test_signal_emission_on_error(self):
        """Test signal emission when initialization fails."""
        # Listen for error signal
        signals_received = []

        def signal_listener(signal_data):
            signals_received.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_ERROR, signal_listener)

        # Try to initialize with nonexistent directory
        nonexistent_path = Path(self.temp_dir) / "nonexistent"
        registry = EntityRegistry(nonexistent_path)
        registry.initialize()

        # Verify error signal was emitted
        self.assertEqual(len(signals_received), 1)
        self.assertEqual(signals_received[0].signal_type, CoreSignal.REGISTRY_ERROR)
        self.assertEqual(signals_received[0].source, "EntityRegistry")

    def test_real_data_loading(self):
        """Test loading entities from actual data directory structure."""
        # This test will use real entity data once we create the JSON files
        # Create a representative set of real entity data
        real_entities = [
            {
                "id": "detective",
                "name": "Detective",
                "description": "Experienced investigator with training in combat and investigation",
                "entity_type": "player",
                "base_health": 100,
                "base_attack": 12,
                "base_defense": 8,
                "base_speed": 14,
                "base_mana": 60,
                "flee_chance": 0.0,
                "is_boss": False,
                "is_elite": False,
                "immunities": [],
            },
            {
                "id": "street_thug",
                "name": "Street Thug",
                "description": "Common criminal with basic combat skills",
                "entity_type": "normal",
                "base_health": 60,
                "base_attack": 8,
                "base_defense": 5,
                "base_speed": 12,
                "base_mana": 0,
                "flee_chance": 0.3,
                "is_boss": False,
                "is_elite": False,
                "immunities": [],
            },
            {
                "id": "gang_lieutenant",
                "name": "Gang Lieutenant",
                "description": "Experienced criminal leader with tactical training",
                "entity_type": "elite",
                "base_health": 120,
                "base_attack": 15,
                "base_defense": 10,
                "base_speed": 13,
                "base_mana": 20,
                "flee_chance": 0.1,
                "is_boss": False,
                "is_elite": True,
                "immunities": ["stun"],
            },
            {
                "id": "crime_boss",
                "name": "Crime Boss",
                "description": "Powerful criminal mastermind with extensive resources",
                "entity_type": "boss",
                "base_health": 300,
                "base_attack": 22,
                "base_defense": 18,
                "base_speed": 10,
                "base_mana": 50,
                "flee_chance": 0.0,
                "is_boss": True,
                "is_elite": False,
                "immunities": ["stun", "poison"],
            },
            {
                "id": "corrupt_officer",
                "name": "Corrupt Police Officer",
                "description": "Former law enforcement turned to crime",
                "entity_type": "elite",
                "base_health": 100,
                "base_attack": 14,
                "base_defense": 12,
                "base_speed": 11,
                "base_mana": 30,
                "flee_chance": 0.2,
                "is_boss": False,
                "is_elite": True,
                "immunities": [],
            },
        ]

        for entity in real_entities:
            entity_file = self.entities_path / f"{entity['id']}.json"
            with open(entity_file, "w") as f:
                json.dump(entity, f, indent=2)

        registry = EntityRegistry(self.entities_path)
        registry.initialize()

        # Verify all entities loaded correctly
        self.assertEqual(len(registry.get_all_items()), 5)

        # Test specific entity properties
        detective = registry.get_item("detective")
        self.assertEqual(detective.entity_type, "player")
        self.assertEqual(detective.base_mana, 60)

        boss = registry.get_item("crime_boss")
        self.assertTrue(boss.is_boss)
        self.assertIn("stun", boss.immunities)
        self.assertIn("poison", boss.immunities)

        # Test filtering
        elites = registry.get_entities_by_type("elite")
        self.assertEqual(len(elites), 2)

        bosses = registry.get_entities_by_type("boss")
        self.assertEqual(len(bosses), 1)


if __name__ == "__main__":
    unittest.main()
