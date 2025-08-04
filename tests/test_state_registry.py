"""
Tests for the StateRegistry system.

Tests the status effects registry functionality, JSON loading, and
signal integration following the "public API only" testing approach.

Author: GitHub Copilot
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

from src.game.state_registry import StateRegistry, StatusEffect
from src.core.signals import get_signal_bus, reset_signal_bus, CoreSignal


class TestStateRegistry:
    """Test StateRegistry functionality."""

    def setup_method(self):
        """Set up test environment."""
        reset_signal_bus()
        self.signal_bus = get_signal_bus()
        self.registry = StateRegistry()

    def teardown_method(self):
        """Clean up test environment."""
        self.registry.cleanup()
        reset_signal_bus()

    def test_registry_initialization(self):
        """Test basic registry initialization."""
        assert self.registry.registry_name == "State"
        assert not self.registry.is_initialized()
        assert self.registry.get_item_count() == 0
        assert self.registry.get_all_items() == {}
        assert self.registry.get_item_ids() == []

    def test_status_effect_dataclass(self):
        """Test StatusEffect dataclass creation."""
        effect = StatusEffect(
            id="test_effect",
            name="Test Effect",
            description="A test status effect",
            default_duration=3,
            max_stacks=2,
            conflicts=["other_effect"],
        )

        assert effect.id == "test_effect"
        assert effect.name == "Test Effect"
        assert effect.description == "A test status effect"
        assert effect.default_duration == 3
        assert effect.max_stacks == 2
        assert effect.conflicts == ["other_effect"]

    def test_load_single_status_effect(self):
        """Test loading a single status effect from JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = {
                "id": "stun",
                "name": "Stunned",
                "description": "Unable to take actions",
                "default_duration": 2,
                "max_stacks": 1,
                "conflicts": ["haste"],
            }

            file_path = Path(temp_dir) / "stun.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            # Load data
            self.registry.load_from_directory(Path(temp_dir))

            # Verify loading
            assert self.registry.is_initialized()
            assert self.registry.get_item_count() == 1

            effect = self.registry.get_item("stun")
            assert effect is not None
            assert effect.name == "Stunned"
            assert effect.description == "Unable to take actions"
            assert effect.default_duration == 2
            assert effect.max_stacks == 1
            assert effect.conflicts == ["haste"]

    def test_load_all_status_effects(self):
        """Test loading all required status effects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data for all required effects
            effects_data = [
                {
                    "id": "stun",
                    "name": "Stunned",
                    "description": "Unable to take actions",
                    "default_duration": 2,
                    "max_stacks": 1,
                    "conflicts": ["haste"],
                },
                {
                    "id": "bleed",
                    "name": "Bleeding",
                    "description": "Taking damage over time",
                    "default_duration": 3,
                    "max_stacks": 5,
                    "conflicts": [],
                },
                {
                    "id": "poison",
                    "name": "Poisoned",
                    "description": "Taking poison damage over time",
                    "default_duration": 4,
                    "max_stacks": 3,
                    "conflicts": [],
                },
                {
                    "id": "slow",
                    "name": "Slowed",
                    "description": "Reduced movement and action speed",
                    "default_duration": 3,
                    "max_stacks": 1,
                    "conflicts": ["haste"],
                },
                {
                    "id": "haste",
                    "name": "Hastened",
                    "description": "Increased movement and action speed",
                    "default_duration": 3,
                    "max_stacks": 1,
                    "conflicts": ["stun", "slow"],
                },
            ]

            # Create individual JSON files
            for effect_data in effects_data:
                file_path = Path(temp_dir) / f"{effect_data['id']}.json"
                with open(file_path, "w") as f:
                    json.dump(effect_data, f)

            # Load data
            self.registry.load_from_directory(Path(temp_dir))

            # Verify all effects loaded
            assert self.registry.get_item_count() == 5
            assert "stun" in self.registry.get_item_ids()
            assert "bleed" in self.registry.get_item_ids()
            assert "poison" in self.registry.get_item_ids()
            assert "slow" in self.registry.get_item_ids()
            assert "haste" in self.registry.get_item_ids()

            # Verify specific effects
            stun = self.registry.get_item("stun")
            assert stun.max_stacks == 1
            assert "haste" in stun.conflicts

            bleed = self.registry.get_item("bleed")
            assert bleed.max_stacks == 5
            assert bleed.conflicts == []

            haste = self.registry.get_item("haste")
            assert "stun" in haste.conflicts
            assert "slow" in haste.conflicts

    def test_status_effect_conflicts(self):
        """Test that conflicts are properly loaded and accessible."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create effects with various conflict patterns
            effects_data = [
                {
                    "id": "effect1",
                    "name": "Effect 1",
                    "description": "First effect",
                    "default_duration": 1,
                    "max_stacks": 1,
                    "conflicts": ["effect2", "effect3"],
                },
                {
                    "id": "effect2",
                    "name": "Effect 2",
                    "description": "Second effect",
                    "default_duration": 1,
                    "max_stacks": 1,
                    "conflicts": ["effect1"],
                },
                {
                    "id": "effect3",
                    "name": "Effect 3",
                    "description": "Third effect",
                    "default_duration": 1,
                    "max_stacks": 1,
                    "conflicts": [],
                },
            ]

            for effect_data in effects_data:
                file_path = Path(temp_dir) / f"{effect_data['id']}.json"
                with open(file_path, "w") as f:
                    json.dump(effect_data, f)

            self.registry.load_from_directory(Path(temp_dir))

            effect1 = self.registry.get_item("effect1")
            effect2 = self.registry.get_item("effect2")
            effect3 = self.registry.get_item("effect3")

            assert "effect2" in effect1.conflicts
            assert "effect3" in effect1.conflicts
            assert "effect1" in effect2.conflicts
            assert effect3.conflicts == []

    def test_load_with_missing_optional_fields(self):
        """Test loading effects with missing optional fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal effect (only required field is id)
            test_data = {"id": "minimal_effect"}

            file_path = Path(temp_dir) / "minimal.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            self.registry.load_from_directory(Path(temp_dir))

            effect = self.registry.get_item("minimal_effect")
            assert effect is not None
            assert effect.id == "minimal_effect"
            assert effect.name == ""  # Default value
            assert effect.description == ""  # Default value
            assert effect.default_duration == 0  # Default value
            assert effect.max_stacks == 1  # Default value
            assert effect.conflicts == []  # Default value

    def test_load_with_invalid_conflicts_type(self):
        """Test error handling for invalid conflicts field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create effect with invalid conflicts (not a list)
            test_data = {
                "id": "invalid_effect",
                "conflicts": "not_a_list",  # Should be a list
            }

            file_path = Path(temp_dir) / "invalid.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            # Loading should handle the error gracefully
            self.registry.load_from_directory(Path(temp_dir))

            # Should not have loaded the invalid effect
            assert self.registry.get_item("invalid_effect") is None
            assert self.registry.get_item_count() == 0

    def test_signal_emission_on_initialization(self):
        """Test that registry emits signal when initialized."""
        signal_received = []

        def signal_handler(signal_data):
            signal_received.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, signal_handler)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test effect
            test_data = {"id": "test_effect"}
            file_path = Path(temp_dir) / "test.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            self.registry.load_from_directory(Path(temp_dir))

        # Verify signal was emitted
        assert len(signal_received) == 1
        signal_data = signal_received[0]
        assert signal_data.signal_type == CoreSignal.REGISTRY_INITIALIZED
        assert signal_data.source == "StateRegistry"
        assert signal_data.data["registry_name"] == "state"
        assert signal_data.data["item_count"] == 1

    def test_signal_emission_on_error(self):
        """Test that registry emits error signal when loading fails."""
        signal_received = []

        def signal_handler(signal_data):
            signal_received.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_ERROR, signal_handler)

        # Try to load from non-existent directory
        self.registry.load_from_directory(Path("/non/existent/path"))

        # Verify error signal was emitted
        assert len(signal_received) == 1
        signal_data = signal_received[0]
        assert signal_data.signal_type == CoreSignal.REGISTRY_ERROR
        assert signal_data.source == "StateRegistry"

    def test_initialize_method(self):
        """Test the initialize convenience method."""
        # Mock the actual data directory to avoid dependency on real files
        with patch.object(self.registry, "load_from_directory") as mock_load:
            self.registry.initialize()
            mock_load.assert_called_once_with(Path("data/status_effects"))

    def test_get_nonexistent_item(self):
        """Test getting an item that doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.registry.load_from_directory(Path(temp_dir))

            result = self.registry.get_item("nonexistent")
            assert result is None

    def test_duration_and_stacks_validation(self):
        """Test that duration and stack values are properly converted to integers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create effect with string values that should be converted to int
            test_data = {
                "id": "numeric_test",
                "default_duration": "5",  # String that should become int
                "max_stacks": "3",  # String that should become int
            }

            file_path = Path(temp_dir) / "numeric.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            self.registry.load_from_directory(Path(temp_dir))

            effect = self.registry.get_item("numeric_test")
            assert effect is not None
            assert isinstance(effect.default_duration, int)
            assert isinstance(effect.max_stacks, int)
            assert effect.default_duration == 5
            assert effect.max_stacks == 3

    def test_real_data_loading(self):
        """Test loading from the actual data directory if it exists."""
        data_path = Path("data/status_effects")
        if data_path.exists():
            self.registry.initialize()

            # Should have loaded all required effects
            required_effects = ["stun", "bleed", "poison", "slow", "haste"]
            for effect_id in required_effects:
                effect = self.registry.get_item(effect_id)
                assert effect is not None, f"Required effect '{effect_id}' not found"
                assert effect.id == effect_id
                assert effect.name != ""  # Should have meaningful names
                assert effect.description != ""  # Should have descriptions
                assert effect.default_duration > 0  # Should have positive duration
                assert effect.max_stacks > 0  # Should allow at least 1 stack
