"""
Base Registry System for Broken Divinity.

Provides abstract base class for all game data registries with built-in
signal integration and common functionality.

Author: GitHub Copilot
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
import json
import threading

from .signals import get_signal_bus, CoreSignal, SignalData
from src.utils.logging import Log


T = TypeVar("T")


class BaseRegistry(ABC, Generic[T]):
    """
    Abstract base class for all game data registries.

    Provides common functionality for loading JSON data, signal integration,
    and registry lifecycle management.
    """

    def __init__(self, registry_name: str):
        """
        Initialize the base registry.

        Args:
            registry_name: Human-readable name for this registry
        """
        self.registry_name = registry_name
        self._data: Dict[str, T] = {}
        self._lock = threading.Lock()
        self._initialized = False
        self._signal_bus = get_signal_bus()

        # Subscribe to hot-reload signals
        self._signal_bus.listen(
            CoreSignal.REGISTRY_RELOADED, self._handle_reload_signal
        )

        Log.p(f"{self.registry_name}Reg", ["Created registry instance"])

    @abstractmethod
    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> T:
        """
        Load a single item from dictionary data.

        Args:
            item_data: Raw dictionary data for the item

        Returns:
            Parsed item instance
        """
        pass

    @abstractmethod
    def _get_item_id(self, item: T) -> str:
        """
        Get the unique identifier for an item.

        Args:
            item: The item to get ID for

        Returns:
            Unique identifier string
        """
        pass

    def load_from_directory(self, data_path: Path) -> None:
        """
        Load registry data from JSON files in a directory.

        Args:
            data_path: Path to directory containing JSON files
        """
        if not data_path.exists() or not data_path.is_dir():
            Log.p(
                f"{self.registry_name}Reg",
                ["ERROR: Data directory not found:", str(data_path)],
            )
            self._emit_error(f"Data directory not found: {data_path}")
            return

        loaded_count = 0
        error_count = 0

        with self._lock:
            self._data.clear()

            # Recursively scan for JSON files
            for json_file in data_path.rglob("*.json"):
                try:
                    loaded_items = self._load_json_file(json_file)
                    loaded_count += loaded_items
                except Exception as e:
                    error_count += 1
                    Log.p(
                        f"{self.registry_name}Reg",
                        ["ERROR loading", str(json_file), ":", str(e)],
                    )

            self._initialized = True

        Log.p(
            f"{self.registry_name}Reg",
            ["Loaded", loaded_count, "items with", error_count, "errors"],
        )

        # Emit initialization signal
        registry_name_for_signal = self.registry_name.lower()
        if registry_name_for_signal == "ability":
            registry_name_for_signal = (
                "abilities"  # Special case for abilities registry
            )

        self._signal_bus.emit(
            CoreSignal.REGISTRY_INITIALIZED,
            f"{self.registry_name}Registry",
            {
                "registry_name": registry_name_for_signal,
                "item_count": loaded_count,
                "error_count": error_count,
                "data_path": str(data_path),
            },
        )

        if error_count > 0:
            self._emit_error(f"Failed to load {error_count} files")

    def _load_json_file(self, file_path: Path) -> int:
        """
        Load items from a single JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Number of items loaded
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        loaded_count = 0

        # Handle different JSON structures
        if isinstance(data, dict):
            # Check if the root dict itself is an item (has an 'id' field)
            if "id" in data:
                # Single item as root object
                try:
                    item = self._load_item_from_dict(data)
                    item_id = self._get_item_id(item)
                    self._data[item_id] = item
                    loaded_count += 1
                except Exception as e:
                    Log.p(
                        f"{self.registry_name}Reg",
                        ["ERROR loading item from", str(file_path), ":", str(e)],
                    )
            else:
                # Look for arrays of items or nested items
                for key, value in data.items():
                    if isinstance(value, list):
                        for item_data in value:
                            if isinstance(item_data, dict):
                                try:
                                    item = self._load_item_from_dict(item_data)
                                    item_id = self._get_item_id(item)
                                    self._data[item_id] = item
                                    loaded_count += 1
                                except Exception as e:
                                    Log.p(
                                        f"{self.registry_name}Reg",
                                        [
                                            "ERROR loading item from",
                                            str(file_path),
                                            ":",
                                            str(e),
                                        ],
                                    )
                    elif isinstance(value, dict):
                        # Single item
                        try:
                            item = self._load_item_from_dict(value)
                            item_id = self._get_item_id(item)
                            self._data[item_id] = item
                            loaded_count += 1
                        except Exception as e:
                            Log.p(
                                f"{self.registry_name}Reg",
                                [
                                    "ERROR loading item from",
                                    str(file_path),
                                    ":",
                                    str(e),
                                ],
                            )
        elif isinstance(data, list):
            # Direct array of items
            for item_data in data:
                if isinstance(item_data, dict):
                    try:
                        item = self._load_item_from_dict(item_data)
                        item_id = self._get_item_id(item)
                        self._data[item_id] = item
                        loaded_count += 1
                    except Exception as e:
                        Log.p(
                            f"{self.registry_name}Reg",
                            ["ERROR loading item from", str(file_path), ":", str(e)],
                        )

        return loaded_count

    def get_item(self, item_id: str) -> Optional[T]:
        """
        Get an item by its ID.

        Args:
            item_id: Unique identifier for the item

        Returns:
            Item instance or None if not found
        """
        with self._lock:
            return self._data.get(item_id)

    def get_all_items(self) -> Dict[str, T]:
        """
        Get all items in the registry.

        Returns:
            Dictionary mapping item IDs to items
        """
        with self._lock:
            return self._data.copy()

    def get_item_ids(self) -> List[str]:
        """
        Get all item IDs in the registry.

        Returns:
            List of item IDs
        """
        with self._lock:
            return list(self._data.keys())

    def get_item_count(self) -> int:
        """
        Get the number of items in the registry.

        Returns:
            Number of items
        """
        with self._lock:
            return len(self._data)

    def is_initialized(self) -> bool:
        """
        Check if the registry has been initialized.

        Returns:
            True if initialized, False otherwise
        """
        return self._initialized

    def reload(self, data_path: Path) -> None:
        """
        Reload registry data from disk.

        Args:
            data_path: Path to directory containing JSON files
        """
        Log.p(f"{self.registry_name}Reg", ["Reloading data from", str(data_path)])
        self.load_from_directory(data_path)

        # Emit reload signal
        self._signal_bus.emit(
            CoreSignal.REGISTRY_RELOADED,
            f"{self.registry_name}Registry",
            {
                "registry_name": self.registry_name.lower(),
                "item_count": self.get_item_count(),
                "data_path": str(data_path),
            },
        )

    def _handle_reload_signal(self, signal_data: SignalData) -> None:
        """
        Handle registry reload signals from other registries.

        Args:
            signal_data: Signal data containing reload information
        """
        # This is a placeholder for hot-reload functionality
        # Individual registries can override this to implement hot-reload
        pass

    def _emit_error(self, error_message: str) -> None:
        """
        Emit a registry error signal.

        Args:
            error_message: Description of the error
        """
        self._signal_bus.emit(
            CoreSignal.REGISTRY_ERROR,
            f"{self.registry_name}Registry",
            {
                "registry_name": self.registry_name.lower(),
                "error_message": error_message,
            },
        )

    def cleanup(self) -> None:
        """Clean up registry resources."""
        with self._lock:
            self._data.clear()
            self._initialized = False

        # Unsubscribe from signals
        self._signal_bus.unlisten(
            CoreSignal.REGISTRY_RELOADED, self._handle_reload_signal
        )

        Log.p(f"{self.registry_name}Reg", ["Registry cleaned up"])


# EOF
