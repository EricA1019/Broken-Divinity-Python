"""
Test suite for SuffixRegistry - Procedural Generation System.

Tests for the affix system that provides prefix/suffix modifiers for entities,
weapons, and NPCs using Diablo/Borderlands-style procedural generation.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any

from src.game.suffix_registry import SuffixRegistry, Suffix, SuffixType, SuffixRarity
from src.core.signals import get_signal_bus, CoreSignal


class TestSuffix:
    """Test the Suffix dataclass."""

    def test_suffix_dataclass_creation(self):
        """Test basic suffix creation."""
        suffix = Suffix(
            id="brave",
            name="Brave",
            description="Increases courage and attack power",
            type=SuffixType.PREFIX,
            rarity=SuffixRarity.COMMON,
            stat_modifiers={"attack": 3, "courage": 5},
            weight=100,
        )

        assert suffix.id == "brave"
        assert suffix.name == "Brave"
        assert suffix.type == SuffixType.PREFIX
        assert suffix.rarity == SuffixRarity.COMMON
        assert suffix.stat_modifiers["attack"] == 3
        assert suffix.weight == 100

    def test_suffix_with_special_effects(self):
        """Test suffix with special effects beyond stat modifiers."""
        suffix = Suffix(
            id="of_fire",
            name="of Fire",
            description="Grants fire immunity and flame attacks",
            type=SuffixType.SUFFIX,
            rarity=SuffixRarity.RARE,
            stat_modifiers={"attack": 2},
            special_effects=["fire_immunity", "flame_weapon"],
            restrictions=["weapon", "entity"],
            weight=25,
        )

        assert suffix.special_effects == ["fire_immunity", "flame_weapon"]
        assert suffix.restrictions == ["weapon", "entity"]
        assert suffix.rarity == SuffixRarity.RARE

    def test_suffix_can_apply_to(self):
        """Test suffix application restrictions."""
        entity_suffix = Suffix(
            id="vile",
            name="Vile",
            type=SuffixType.PREFIX,
            rarity=SuffixRarity.UNCOMMON,
            restrictions=["entity"],
            stat_modifiers={"corruption": 2},
        )

        weapon_suffix = Suffix(
            id="sharp",
            name="Sharp",
            type=SuffixType.PREFIX,
            rarity=SuffixRarity.COMMON,
            restrictions=["weapon"],
            stat_modifiers={"attack": 1, "accuracy": 5},
        )

        universal_suffix = Suffix(
            id="blessed",
            name="Blessed",
            type=SuffixType.PREFIX,
            rarity=SuffixRarity.RARE,
            stat_modifiers={"holy_power": 3},
        )

        assert entity_suffix.can_apply_to("entity")
        assert not entity_suffix.can_apply_to("weapon")
        assert weapon_suffix.can_apply_to("weapon")
        assert not weapon_suffix.can_apply_to("entity")
        assert universal_suffix.can_apply_to("entity")
        assert universal_suffix.can_apply_to("weapon")


class TestSuffixRegistry:
    """Test SuffixRegistry functionality."""

    def test_registry_initialization(self):
        """Test registry creates properly."""
        registry = SuffixRegistry()
        assert registry.get_item_count() == 0
        assert registry.is_initialized() == False

    def test_load_entity_suffixes(self):
        """Test loading entity prefix/suffix modifiers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test suffix data
            suffix_data = {
                "entity_prefixes": [
                    {
                        "id": "brave",
                        "name": "Brave",
                        "description": "Courageous and bold",
                        "type": "prefix",
                        "rarity": "common",
                        "stat_modifiers": {"attack": 2, "courage": 5},
                        "restrictions": ["entity"],
                        "weight": 100,
                    }
                ],
                "entity_suffixes": [
                    {
                        "id": "of_blight",
                        "name": "of Blight",
                        "description": "Corrupted by dark magic",
                        "type": "suffix",
                        "rarity": "uncommon",
                        "stat_modifiers": {"corruption": 3, "poison_resist": 10},
                        "special_effects": ["poison_immunity"],
                        "restrictions": ["entity"],
                        "weight": 60,
                    }
                ],
            }

            file_path = os.path.join(temp_dir, "entity_suffixes.json")
            with open(file_path, "w") as f:
                json.dump(suffix_data, f)

            registry = SuffixRegistry()
            registry.load_from_directory(Path(temp_dir))

            assert registry.get_item_count() == 2

            brave = registry.get_item("brave")
            assert brave is not None
            assert brave.name == "Brave"
            assert brave.type == SuffixType.PREFIX
            assert brave.stat_modifiers["attack"] == 2

            blight = registry.get_item("of_blight")
            assert blight is not None
            assert blight.type == SuffixType.SUFFIX
            assert "poison_immunity" in blight.special_effects

    def test_load_weapon_suffixes(self):
        """Test loading weapon part suffixes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            weapon_data = {
                "weapon_suffixes": [
                    {
                        "id": "sharp",
                        "name": "Sharp",
                        "description": "Honed to a razor edge",
                        "type": "prefix",
                        "rarity": "common",
                        "stat_modifiers": {"attack": 1, "accuracy": 5},
                        "restrictions": ["weapon"],
                        "weight": 80,
                    },
                    {
                        "id": "of_flame",
                        "name": "of Flame",
                        "description": "Wreathed in eternal fire",
                        "type": "suffix",
                        "rarity": "rare",
                        "stat_modifiers": {"fire_damage": 5},
                        "special_effects": ["ignite_chance"],
                        "restrictions": ["weapon"],
                        "weight": 15,
                    },
                ]
            }

            file_path = os.path.join(temp_dir, "weapon_suffixes.json")
            with open(file_path, "w") as f:
                json.dump(weapon_data, f)

            registry = SuffixRegistry()
            registry.load_from_directory(Path(temp_dir))

            assert registry.get_item_count() == 2

            sharp = registry.get_item("sharp")
            assert sharp.restrictions == ["weapon"]
            assert sharp.rarity == SuffixRarity.COMMON

    def test_get_suffixes_by_type(self):
        """Test filtering suffixes by prefix/suffix type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "suffixes": [
                    {
                        "id": "brave",
                        "name": "Brave",
                        "type": "prefix",
                        "rarity": "common",
                        "stat_modifiers": {"attack": 1},
                    },
                    {
                        "id": "swift",
                        "name": "Swift",
                        "type": "prefix",
                        "rarity": "common",
                        "stat_modifiers": {"speed": 2},
                    },
                    {
                        "id": "of_power",
                        "name": "of Power",
                        "type": "suffix",
                        "rarity": "uncommon",
                        "stat_modifiers": {"attack": 3},
                    },
                ]
            }

            file_path = os.path.join(temp_dir, "test_suffixes.json")
            with open(file_path, "w") as f:
                json.dump(data, f)

            registry = SuffixRegistry()
            registry.load_from_directory(Path(temp_dir))

            prefixes = registry.get_prefixes()
            suffixes = registry.get_suffixes()

            assert len(prefixes) == 2
            assert len(suffixes) == 1
            assert all(s.type == SuffixType.PREFIX for s in prefixes)
            assert all(s.type == SuffixType.SUFFIX for s in suffixes)

    def test_get_suffixes_by_rarity(self):
        """Test filtering suffixes by rarity tier."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "suffixes": [
                    {
                        "id": "common1",
                        "name": "Common 1",
                        "type": "prefix",
                        "rarity": "common",
                        "stat_modifiers": {"attack": 1},
                    },
                    {
                        "id": "rare1",
                        "name": "Rare 1",
                        "type": "suffix",
                        "rarity": "rare",
                        "stat_modifiers": {"attack": 5},
                    },
                    {
                        "id": "legendary1",
                        "name": "Legendary 1",
                        "type": "prefix",
                        "rarity": "legendary",
                        "stat_modifiers": {"attack": 10},
                    },
                ]
            }

            file_path = os.path.join(temp_dir, "rarity_test.json")
            with open(file_path, "w") as f:
                json.dump(data, f)

            registry = SuffixRegistry()
            registry.load_from_directory(Path(temp_dir))

            common_suffixes = registry.get_suffixes_by_rarity(SuffixRarity.COMMON)
            rare_suffixes = registry.get_suffixes_by_rarity(SuffixRarity.RARE)
            legendary_suffixes = registry.get_suffixes_by_rarity(SuffixRarity.LEGENDARY)

            assert len(common_suffixes) == 1
            assert len(rare_suffixes) == 1
            assert len(legendary_suffixes) == 1
            assert common_suffixes[0].id == "common1"
            assert rare_suffixes[0].id == "rare1"

    def test_get_applicable_suffixes(self):
        """Test getting suffixes that can apply to specific targets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "suffixes": [
                    {
                        "id": "entity_only",
                        "name": "Entity Only",
                        "type": "prefix",
                        "rarity": "common",
                        "restrictions": ["entity"],
                        "stat_modifiers": {"hp": 5},
                    },
                    {
                        "id": "weapon_only",
                        "name": "Weapon Only",
                        "type": "suffix",
                        "rarity": "common",
                        "restrictions": ["weapon"],
                        "stat_modifiers": {"attack": 2},
                    },
                    {
                        "id": "universal",
                        "name": "Universal",
                        "type": "prefix",
                        "rarity": "common",
                        "stat_modifiers": {"speed": 1},
                    },
                ]
            }

            file_path = os.path.join(temp_dir, "restriction_test.json")
            with open(file_path, "w") as f:
                json.dump(data, f)

            registry = SuffixRegistry()
            registry.load_from_directory(Path(temp_dir))

            entity_suffixes = registry.get_applicable_suffixes("entity")
            weapon_suffixes = registry.get_applicable_suffixes("weapon")

            # Entity should get entity_only and universal
            assert len(entity_suffixes) == 2
            entity_ids = [s.id for s in entity_suffixes]
            assert "entity_only" in entity_ids
            assert "universal" in entity_ids

            # Weapon should get weapon_only and universal
            assert len(weapon_suffixes) == 2
            weapon_ids = [s.id for s in weapon_suffixes]
            assert "weapon_only" in weapon_ids
            assert "universal" in weapon_ids

    def test_weighted_suffix_selection(self):
        """Test weighted random suffix selection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "suffixes": [
                    {
                        "id": "common",
                        "name": "Common",
                        "type": "prefix",
                        "rarity": "common",
                        "weight": 100,
                        "stat_modifiers": {"attack": 1},
                    },
                    {
                        "id": "rare",
                        "name": "Rare",
                        "type": "suffix",
                        "rarity": "rare",
                        "weight": 10,
                        "stat_modifiers": {"attack": 5},
                    },
                ]
            }

            file_path = os.path.join(temp_dir, "weight_test.json")
            with open(file_path, "w") as f:
                json.dump(data, f)

            registry = SuffixRegistry()
            registry.load_from_directory(Path(temp_dir))

            # Test multiple selections to check weighting works
            selections = []
            for _ in range(100):
                chosen = registry.select_random_suffix()
                if chosen:
                    selections.append(chosen.id)

            # Common should appear much more often than rare
            common_count = selections.count("common")
            rare_count = selections.count("rare")

            # With 100:10 weight ratio, common should dominate
            assert common_count > rare_count
            assert common_count > 50  # Should be majority

    def test_generate_entity_variant(self):
        """Test generating entity variants with suffix combinations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "entity_modifiers": [
                    {
                        "id": "brave",
                        "name": "Brave",
                        "type": "prefix",
                        "rarity": "common",
                        "restrictions": ["entity"],
                        "stat_modifiers": {"attack": 2, "courage": 5},
                        "weight": 100,
                    },
                    {
                        "id": "of_blight",
                        "name": "of Blight",
                        "type": "suffix",
                        "rarity": "uncommon",
                        "restrictions": ["entity"],
                        "stat_modifiers": {"corruption": 3},
                        "weight": 50,
                    },
                ]
            }

            file_path = os.path.join(temp_dir, "entity_test.json")
            with open(file_path, "w") as f:
                json.dump(data, f)

            registry = SuffixRegistry()
            registry.load_from_directory(Path(temp_dir))

            # Generate variant with base entity stats
            base_stats = {"hp": 20, "attack": 8, "defense": 5, "speed": 10}
            variant = registry.generate_entity_variant("imp", base_stats)

            assert variant is not None
            assert "name" in variant
            assert "stats" in variant
            assert "applied_suffixes" in variant

            # Stats should be modified from base
            if variant["applied_suffixes"]:
                # Should have modifications if suffixes applied
                total_attack_mod = sum(
                    suffix.stat_modifiers.get("attack", 0)
                    for suffix in variant["applied_suffixes"]
                )
                expected_attack = base_stats["attack"] + total_attack_mod
                assert variant["stats"]["attack"] == expected_attack


class TestSuffixRegistryIntegration:
    """Test SuffixRegistry integration with signal bus and other systems."""

    def test_registry_signals(self):
        """Test signal emission during registry operations."""
        signal_bus = get_signal_bus()
        signals_received = []

        def capture_signal(signal_data):
            signals_received.append(signal_data)

        signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, capture_signal)

        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "suffixes": [
                    {
                        "id": "test",
                        "name": "Test",
                        "type": "prefix",
                        "rarity": "common",
                        "stat_modifiers": {},
                    }
                ]
            }

            file_path = os.path.join(temp_dir, "test.json")
            with open(file_path, "w") as f:
                json.dump(data, f)

            registry = SuffixRegistry()
            registry.load_from_directory(Path(temp_dir))

            # Should have received initialization signal
            assert len(signals_received) > 0
            init_signal = signals_received[-1]
            assert "registry_name" in init_signal.data
            assert init_signal.data["item_count"] == 1

    def test_real_data_loading(self):
        """Test loading real suffix data from data directory."""
        # This test will work once we create real data files
        # For now, verify registry can be created without errors
        registry = SuffixRegistry()
        assert registry.get_item_count() == 0

        # Try loading from non-existent directory (should not crash)
        fake_path = Path("/nonexistent/path")
        registry.load_from_directory(fake_path)
        assert registry.get_item_count() == 0


if __name__ == "__main__":
    pytest.main([__file__])
