"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  BuffRegistry - Stat Modification System                                    ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Registry for buff effects (positive stat modifications)    ║
║  Last-Updated  : 2025-08-03                                                 ║
║  Version       : v0.0.4                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.core.registry import BaseRegistry
from src.utils.logging import Log


@dataclass
class Buff:
    """
    Represents a buff effect that modifies entity stats.

    Buffs can be temporary (duration-based) or permanent.
    They modify stats like attack, defense, speed, etc.
    """

    id: str
    name: str
    description: str
    stat_modifiers: Dict[str, int] = field(default_factory=dict)
    default_duration: int = 1
    max_stacks: int = 1
    buff_type: str = "temporary"  # "temporary" or "permanent"
    is_permanent: bool = False
    display_name: str = ""  # Human-readable name for UI display
    effect_type: str = "buff"  # Type of effect for categorization
    duration: int = 0  # Alternative duration field for compatibility
    stacks: bool = True  # Whether this buff can stack
    conflicts: List[str] = field(default_factory=list)  # Conflicting buffs
    visual_indicator: str = ""  # Icon or symbol for UI

    def __post_init__(self):
        """Post-initialization processing."""
        # Set permanent buff defaults
        if self.is_permanent or self.buff_type == "permanent":
            self.is_permanent = True
            self.buff_type = "permanent"
            if self.default_duration == 1:  # Only set if default
                self.default_duration = -1  # -1 indicates permanent
            if self.max_stacks == 1:  # Only set if default
                self.max_stacks = 999  # High number for permanent buffs

    def calculate_total_modifiers(self, stack_count: int) -> Dict[str, int]:
        """
        Calculate total stat modifiers for given stack count.

        Args:
            stack_count: Number of stacks of this buff

        Returns:
            Dictionary of stat names to total modifier values
        """
        return {
            stat: modifier * min(stack_count, self.max_stacks)
            for stat, modifier in self.stat_modifiers.items()
        }

    def can_stack_to(self, target_stacks: int) -> bool:
        """
        Check if this buff can be stacked to the target number.

        Args:
            target_stacks: Desired number of stacks

        Returns:
            True if stacking is allowed, False otherwise
        """
        return target_stacks <= self.max_stacks


class BuffRegistry(BaseRegistry[Buff]):
    """
    Registry for managing buff definitions.

    Loads buff data from JSON files and provides access to buff definitions.
    Supports both temporary and permanent buffs with stat modifications.
    """

    def __init__(self):
        """Initialize the BuffRegistry."""
        super().__init__("Buff")

    def _get_data_directory(self) -> Path:
        """Return the data directory path for buffs."""
        return Path("data/buffs")

    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> Buff:
        """
        Create a Buff instance from dictionary data.

        Args:
            item_data: Dictionary containing buff data

        Returns:
            Buff instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ["id", "name", "description", "stat_modifiers"]
        for field in required_fields:
            if field not in item_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate stat_modifiers is a dictionary
        if not isinstance(item_data["stat_modifiers"], dict):
            raise ValueError("stat_modifiers must be a dictionary")

        return Buff(**item_data)

    def _get_item_id(self, item: Buff) -> str:
        """Get the unique identifier for a buff."""
        return item.id

    def get_buffs_by_type(self, buff_type: str) -> List[Buff]:
        """
        Get all buffs of a specific type.

        Args:
            buff_type: Type of buff ("temporary" or "permanent")

        Returns:
            List of buffs matching the type
        """
        return [
            buff
            for buff in self.get_all_items().values()
            if buff.buff_type == buff_type
        ]

    def get_stat_modifying_buffs(self, stat_name: str) -> List[Buff]:
        """
        Get all buffs that modify a specific stat.

        Args:
            stat_name: Name of the stat (e.g., "attack", "defense", "speed")

        Returns:
            List of buffs that modify the specified stat
        """
        return [
            buff
            for buff in self.get_all_items().values()
            if stat_name in buff.stat_modifiers
        ]

    def get_temporary_buffs(self) -> List[Buff]:
        """Get all temporary buffs."""
        return self.get_buffs_by_type("temporary")

    def get_permanent_buffs(self) -> List[Buff]:
        """Get all permanent buffs."""
        return self.get_buffs_by_type("permanent")

    def initialize(self) -> None:
        """Initialize the BuffRegistry by loading data."""
        Log.p(f"{self.registry_name}Reg", ["Initializing BuffRegistry"])
        data_dir = self._get_data_directory()
        self.load_from_directory(data_dir)


# EOF
