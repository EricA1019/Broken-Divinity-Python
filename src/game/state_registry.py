"""
StateRegistry for Broken Divinity - Status Effects

Loads status effect definitions and provides registry access.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.core.registry import BaseRegistry
from src.core.signals import CoreSignal, SignalData
from src.utils.logging import Log


@dataclass
class StatusEffect:
    """Data class representing a status effect."""

    id: str
    name: str
    description: str
    default_duration: int
    max_stacks: int
    conflicts: List[str]
    # New fields for enhanced status effects
    stat_changes: Optional[Dict[str, int]] = None
    duration_hours: int = 0
    duration_minutes: int = 0
    effect_type: str = "neutral"
    damage_over_time: int = 0
    removable: bool = True
    display_name: str = ""

    def __post_init__(self):
        """Initialize default values after object creation"""
        if self.stat_changes is None:
            self.stat_changes = {}
        if not self.display_name:
            self.display_name = self.name.title()


class StateRegistry(BaseRegistry[StatusEffect]):
    """Registry for status effect definitions."""

    def __init__(self):
        super().__init__("State")

    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> StatusEffect:
        """
        Parse a status effect definition from a dictionary.
        """
        # Required fields
        effect_id = item_data.get("id", "")  # Use id as the unique identifier
        name = item_data.get("name", "")
        description = item_data.get("description", "")
        default_duration = int(item_data.get("default_duration", 0))
        max_stacks = int(item_data.get("max_stacks", 1))
        conflicts = item_data.get("conflicts", [])
        if not isinstance(conflicts, list):
            raise ValueError(f"Conflicts must be a list: {conflicts}")

        # New fields
        stat_changes = item_data.get("stat_changes", {})
        duration_hours = int(item_data.get("duration_hours", 0))
        duration_minutes = int(item_data.get("duration_minutes", 0))
        effect_type = item_data.get("effect_type", "neutral")
        damage_over_time = int(item_data.get("damage_over_time", 0))
        removable = item_data.get("removable", True)
        display_name = item_data.get("display_name", "")

        return StatusEffect(
            id=effect_id,
            name=name,
            description=description,
            default_duration=default_duration,
            max_stacks=max_stacks,
            conflicts=conflicts,
            stat_changes=stat_changes,
            duration_hours=duration_hours,
            duration_minutes=duration_minutes,
            effect_type=effect_type,
            damage_over_time=damage_over_time,
            removable=removable,
            display_name=display_name,
        )

    def _get_item_id(self, item: StatusEffect) -> str:
        """Return the unique ID of a status effect."""
        return item.id

    def initialize(self) -> None:
        """Load definitions from the default data directory."""
        data_path = Path("data/status_effects")
        self.load_from_directory(data_path)
