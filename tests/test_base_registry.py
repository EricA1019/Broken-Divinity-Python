"""
Tests for the BaseRegistry system.

Tests the abstract registry functionality, signal integration, and
JSON loading capabilities following the "public API only" testing approach.

Author: GitHub Copilot
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

from src.core.registry import BaseRegistry
from src.core.signals import get_signal_bus, reset_signal_bus, CoreSignal


class TestItem:
    """Simple test item class for registry testing."""

    def __init__(self, id: str, name: str, value: int = 0):
        self.id = id
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, TestItem):
            return False
        return (
            self.id == other.id
            and self.name == other.name
            and self.value == other.value
        )


class TestRegistry(BaseRegistry[TestItem]):
    """Concrete implementation of BaseRegistry for testing."""

    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> TestItem:
        """Load a TestItem from dictionary data."""
        return TestItem(
            id=item_data["id"], name=item_data["name"], value=item_data.get("value", 0)
        )

    def _get_item_id(self, item: TestItem) -> str:
        """Get the ID of a TestItem."""
        return item.id


class TestBaseRegistry:
    """Test BaseRegistry functionality."""

    def setup_method(self):
        """Set up test environment."""
        reset_signal_bus()
        self.signal_bus = get_signal_bus()
        self.registry = TestRegistry("Test")

    def teardown_method(self):
        """Clean up test environment."""
        self.registry.cleanup()
        reset_signal_bus()

    def test_registry_initialization(self):
        """Test basic registry initialization."""
        assert self.registry.registry_name == "Test"
        assert not self.registry.is_initialized()
        assert self.registry.get_item_count() == 0
        assert self.registry.get_all_items() == {}
        assert self.registry.get_item_ids() == []

    def test_load_from_single_json_file(self):
        """Test loading items from a single JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = {
                "test_items": [
                    {"id": "item1", "name": "Test Item 1", "value": 10},
                    {"id": "item2", "name": "Test Item 2", "value": 20},
                ]
            }

            file_path = Path(temp_dir) / "test.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            # Load data
            self.registry.load_from_directory(Path(temp_dir))

            # Verify loading
            assert self.registry.is_initialized()
            assert self.registry.get_item_count() == 2

            item1 = self.registry.get_item("item1")
            assert item1 is not None
            assert item1.name == "Test Item 1"
            assert item1.value == 10

            item2 = self.registry.get_item("item2")
            assert item2 is not None
            assert item2.name == "Test Item 2"
            assert item2.value == 20

    def test_load_from_multiple_json_files(self):
        """Test loading items from multiple JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first file
            data1 = {"items": [{"id": "file1_item1", "name": "File 1 Item 1"}]}
            file1_path = Path(temp_dir) / "file1.json"
            with open(file1_path, "w") as f:
                json.dump(data1, f)

            # Create second file
            data2 = {"items": [{"id": "file2_item1", "name": "File 2 Item 1"}]}
            file2_path = Path(temp_dir) / "file2.json"
            with open(file2_path, "w") as f:
                json.dump(data2, f)

            # Load data
            self.registry.load_from_directory(Path(temp_dir))

            # Verify both files were loaded
            assert self.registry.get_item_count() == 2
            assert self.registry.get_item("file1_item1") is not None
            assert self.registry.get_item("file2_item1") is not None

    def test_load_from_nested_directories(self):
        """Test loading from nested directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested directory structure
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()

            # Create file in subdirectory
            data = {"items": [{"id": "nested_item", "name": "Nested Item"}]}
            file_path = subdir / "nested.json"
            with open(file_path, "w") as f:
                json.dump(data, f)

            # Load data
            self.registry.load_from_directory(Path(temp_dir))

            # Verify nested file was loaded
            assert self.registry.get_item_count() == 1
            assert self.registry.get_item("nested_item") is not None

    def test_load_direct_array_format(self):
        """Test loading from JSON files with direct array format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data as direct array
            test_data = [
                {"id": "array_item1", "name": "Array Item 1"},
                {"id": "array_item2", "name": "Array Item 2"},
            ]

            file_path = Path(temp_dir) / "array.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            # Load data
            self.registry.load_from_directory(Path(temp_dir))

            # Verify loading
            assert self.registry.get_item_count() == 2
            assert self.registry.get_item("array_item1") is not None
            assert self.registry.get_item("array_item2") is not None

    def test_load_single_item_format(self):
        """Test loading single item objects (not in arrays)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data as single item
            test_data = {"single_item": {"id": "solo", "name": "Solo Item"}}

            file_path = Path(temp_dir) / "single.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            # Load data
            self.registry.load_from_directory(Path(temp_dir))

            # Verify loading
            assert self.registry.get_item_count() == 1
            assert self.registry.get_item("solo") is not None

    def test_get_item_operations(self):
        """Test item retrieval operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = {
                "items": [
                    {"id": "test1", "name": "Test 1"},
                    {"id": "test2", "name": "Test 2"},
                    {"id": "test3", "name": "Test 3"},
                ]
            }

            file_path = Path(temp_dir) / "test.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            self.registry.load_from_directory(Path(temp_dir))

            # Test get_item
            item = self.registry.get_item("test1")
            assert item is not None
            assert item.name == "Test 1"

            # Test get_item with nonexistent ID
            assert self.registry.get_item("nonexistent") is None

            # Test get_all_items
            all_items = self.registry.get_all_items()
            assert len(all_items) == 3
            assert "test1" in all_items
            assert "test2" in all_items
            assert "test3" in all_items

            # Test get_item_ids
            ids = self.registry.get_item_ids()
            assert sorted(ids) == ["test1", "test2", "test3"]

            # Test get_item_count
            assert self.registry.get_item_count() == 3

    def test_registry_initialization_signal(self):
        """Test that registry emits initialization signal."""
        received_signals = []

        def signal_listener(signal_data):
            received_signals.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, signal_listener)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = {"items": [{"id": "test", "name": "Test"}]}
            file_path = Path(temp_dir) / "test.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            # Load data (should emit signal)
            self.registry.load_from_directory(Path(temp_dir))

            # Verify signal was emitted
            assert len(received_signals) == 1
            signal = received_signals[0]
            assert signal.signal_type == CoreSignal.REGISTRY_INITIALIZED
            assert signal.source == "TestRegistry"
            assert signal.data["registry_name"] == "test"
            assert signal.data["item_count"] == 1
            assert signal.data["error_count"] == 0

    def test_registry_reload(self):
        """Test registry reload functionality."""
        received_signals = []

        def signal_listener(signal_data):
            received_signals.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_RELOADED, signal_listener)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Initial load
            test_data = {"items": [{"id": "initial", "name": "Initial"}]}
            file_path = Path(temp_dir) / "test.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            self.registry.load_from_directory(Path(temp_dir))
            assert self.registry.get_item_count() == 1

            # Modify data and reload
            new_data = {
                "items": [
                    {"id": "new1", "name": "New 1"},
                    {"id": "new2", "name": "New 2"},
                ]
            }
            with open(file_path, "w") as f:
                json.dump(new_data, f)

            self.registry.reload(Path(temp_dir))

            # Verify reload
            assert self.registry.get_item_count() == 2
            assert self.registry.get_item("initial") is None
            assert self.registry.get_item("new1") is not None
            assert self.registry.get_item("new2") is not None

            # Verify reload signal was emitted
            reload_signals = [
                s
                for s in received_signals
                if s.signal_type == CoreSignal.REGISTRY_RELOADED
            ]
            assert len(reload_signals) == 1

    def test_load_nonexistent_directory(self):
        """Test loading from nonexistent directory."""
        received_signals = []

        def signal_listener(signal_data):
            received_signals.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_ERROR, signal_listener)

        nonexistent_path = Path("/nonexistent/directory")
        self.registry.load_from_directory(nonexistent_path)

        # Should not be initialized and should emit error
        assert not self.registry.is_initialized()
        assert self.registry.get_item_count() == 0

        # Verify error signal was emitted
        assert len(received_signals) == 1
        signal = received_signals[0]
        assert signal.signal_type == CoreSignal.REGISTRY_ERROR
        assert "not found" in signal.data["error_message"]

    def test_load_invalid_json(self):
        """Test handling of invalid JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid JSON file
            file_path = Path(temp_dir) / "invalid.json"
            with open(file_path, "w") as f:
                f.write("{ invalid json }")

            # Should not crash, but should log errors
            self.registry.load_from_directory(Path(temp_dir))

            # Registry should still be initialized (even with errors)
            assert self.registry.is_initialized()
            assert self.registry.get_item_count() == 0

    def test_load_item_creation_error(self):
        """Test handling of errors during item creation."""

        class FailingRegistry(BaseRegistry[TestItem]):
            def _load_item_from_dict(self, item_data: Dict[str, Any]) -> TestItem:
                raise ValueError("Test error")

            def _get_item_id(self, item: TestItem) -> str:
                return item.id

        failing_registry = FailingRegistry("Failing")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create valid JSON that will fail during item creation
            test_data = {"items": [{"id": "test", "name": "Test"}]}
            file_path = Path(temp_dir) / "test.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            # Should not crash
            failing_registry.load_from_directory(Path(temp_dir))

            # No items should be loaded
            assert failing_registry.get_item_count() == 0

        failing_registry.cleanup()

    def test_registry_cleanup(self):
        """Test registry cleanup functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Load some data
            test_data = {"items": [{"id": "test", "name": "Test"}]}
            file_path = Path(temp_dir) / "test.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            self.registry.load_from_directory(Path(temp_dir))
            assert self.registry.is_initialized()
            assert self.registry.get_item_count() == 1

            # Cleanup
            self.registry.cleanup()

            # Should be reset
            assert not self.registry.is_initialized()
            assert self.registry.get_item_count() == 0
            assert self.registry.get_all_items() == {}

    def test_thread_safety(self):
        """Test basic thread safety of registry operations."""
        import threading

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            test_data = {
                "items": [{"id": f"item{i}", "name": f"Item {i}"} for i in range(100)]
            }
            file_path = Path(temp_dir) / "test.json"
            with open(file_path, "w") as f:
                json.dump(test_data, f)

            self.registry.load_from_directory(Path(temp_dir))

            # Test concurrent access
            results = []

            def access_items():
                for i in range(50):
                    item = self.registry.get_item(f"item{i}")
                    if item:
                        results.append(item.id)

            threads = []
            for _ in range(5):
                thread = threading.Thread(target=access_items)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Should have accessed many items without crashing
            assert len(results) > 0


# EOF
