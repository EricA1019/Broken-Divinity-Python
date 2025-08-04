"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  EntityRegistry - Character and Enemy Data Management                       ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Registry for entity data (creatures, stats, types)         ║
║  Last-Updated  : 2025-08-03                                                 ║
║  Version       : v0.0.5                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.core.registry import BaseRegistry
from src.utils.logging import Log


@dataclass
class Entity:
    """
    Represents a game entity (player character, enemy, boss, etc.).

    Entities have base stats, types, and special properties like boss immunity.
    They can calculate modified stats and flee chances based on conditions.
    """

    id: str
    name: str
    description: str
    entity_type: str  # "player", "normal", "elite", "boss"

    # Base stats
    base_health: int = 100
    base_attack: int = 10
    base_defense: int = 10
    base_speed: int = 10
    base_mana: int = 50

    # Behavioral properties
    flee_chance: float = 0.0  # Base flee chance when health is low
    is_boss: bool = False
    is_elite: bool = False
    immunities: List[str] = field(default_factory=list)

    def calculate_stats(
        self, modifiers: Optional[Dict[str, int]] = None
    ) -> Dict[str, int]:
        """
        Calculate final stats applying any modifiers.

        Args:
            modifiers: Dict of stat modifications (e.g., {"attack": 5, "defense": -2})

        Returns:
            Dict with final calculated stats
        """
        if modifiers is None:
            modifiers = {}

        stats = {
            "health": self.base_health,
            "attack": self.base_attack,
            "defense": self.base_defense,
            "speed": self.base_speed,
            "mana": self.base_mana,
        }

        # Apply modifiers
        for stat, modifier in modifiers.items():
            if stat in stats:
                stats[stat] += modifier
                # Ensure stats don't go below 0
                stats[stat] = max(0, stats[stat])

        return stats

    def calculate_flee_chance(self, current_health: int, max_health: int) -> float:
        """
        Calculate flee chance based on current health and entity properties.

        Args:
            current_health: Current health value
            max_health: Maximum health value

        Returns:
            Flee chance as float between 0.0 and 1.0
        """
        # Bosses never flee
        if self.is_boss:
            return 0.0

        # Calculate health percentage
        health_percent = current_health / max_health if max_health > 0 else 0.0

        # If health is above 50%, use base flee chance
        if health_percent > 0.5:
            return self.flee_chance

        # Below 50% health, increase flee chance based on how low health is
        low_health_modifier = (0.5 - health_percent) * 2.0  # 0.0 to 1.0 range
        modified_chance = self.flee_chance + (
            low_health_modifier * 0.4
        )  # Up to 40% bonus

        # Cap at 100%
        return min(1.0, modified_chance)

    def is_immune_to(self, status_effect: str) -> bool:
        """
        Check if entity is immune to a specific status effect.

        Args:
            status_effect: Name of the status effect to check

        Returns:
            True if entity is immune, False otherwise
        """
        return status_effect in self.immunities


class EntityRegistry(BaseRegistry[Entity]):
    """
    Registry for managing entity data (player character, enemies, bosses).

    Loads entity definitions from JSON files and provides query methods
    for filtering by type, immunity, and other properties.
    """

    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialize EntityRegistry.

        Args:
            data_path: Path to directory containing entity JSON files (for testing)
        """
        super().__init__("Entity")
        self._data_path = data_path

        Log.p("EntityReg", ["Initialized EntityRegistry"])

    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> Entity:
        """
        Create an Entity instance from dictionary data.

        Args:
            item_data: Dictionary containing entity data

        Returns:
            Entity instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ["id", "name", "description", "entity_type"]
        for field in required_fields:
            if field not in item_data:
                raise ValueError(f"Missing required field: {field}")

        return Entity(**item_data)

    def _get_item_id(self, item: Entity) -> str:
        """Get the unique identifier for an entity."""
        return item.id

    def initialize(self) -> None:
        """Initialize the EntityRegistry by loading data."""
        Log.p("EntityReg", ["Initializing EntityRegistry"])

        if self._data_path is not None:
            # Use provided path (for testing)
            data_dir = self._data_path
        else:
            # Use default data directory
            data_dir = Path("data/entities")

        self.load_from_directory(data_dir)

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """
        Get all entities of a specific type.

        Args:
            entity_type: Type of entity ("player", "normal", "elite", "boss")

        Returns:
            List of entities matching the type
        """
        return [
            entity
            for entity in self.get_all_items().values()
            if entity.entity_type == entity_type
        ]

    def get_entities_with_immunity(self, status_effect: str) -> List[Entity]:
        """
        Get all entities that are immune to a specific status effect.

        Args:
            status_effect: Name of the status effect

        Returns:
            List of entities with immunity to the status effect
        """
        return [
            entity
            for entity in self.get_all_items().values()
            if entity.is_immune_to(status_effect)
        ]

    def get_bosses(self) -> List[Entity]:
        """
        Get all boss entities.

        Returns:
            List of all boss entities
        """
        return [entity for entity in self.get_all_items().values() if entity.is_boss]

    def get_elites(self) -> List[Entity]:
        """
        Get all elite entities.

        Returns:
            List of all elite entities
        """
        return [entity for entity in self.get_all_items().values() if entity.is_elite]

    def get_player_entities(self) -> List[Entity]:
        """
        Get all player character entities.

        Returns:
            List of all player entities
        """
        return self.get_entities_by_type("player")

    def get_enemies(self) -> List[Entity]:
        """
        Get all enemy entities (normal, elite, boss but not player).

        Returns:
            List of all enemy entities
        """
        return [
            entity
            for entity in self.get_all_items().values()
            if entity.entity_type != "player"
        ]
