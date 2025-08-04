"""
StateRegistry for Broken Divinity - Status Effects

Loads status effect definitions and provides registry access.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

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


class StateRegistry(BaseRegistry[StatusEffect]):
    """Registry for status effect definitions."""

    def __init__(self):
        super().__init__("State")

    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> StatusEffect:
        """
        Parse a status effect definition from a dictionary.
        """
        # Required fields
        effect_id = item_data["id"]
        name = item_data.get("name", "")
        description = item_data.get("description", "")
        default_duration = int(item_data.get("default_duration", 0))
        max_stacks = int(item_data.get("max_stacks", 1))
        conflicts = item_data.get("conflicts", [])
        if not isinstance(conflicts, list):
            raise ValueError(f"Conflicts must be a list: {conflicts}")

        return StatusEffect(
            id=effect_id,
            name=name,
            description=description,
            default_duration=default_duration,
            max_stacks=max_stacks,
            conflicts=conflicts,
        )

    def _get_item_id(self, item: StatusEffect) -> str:
        """Return the unique ID of a status effect."""
        return item.id

    def initialize(self) -> None:
        """Load definitions from the default data directory."""
        data_path = Path("data/status_effects")
        self.load_from_directory(data_path)
