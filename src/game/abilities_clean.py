"""
Core ability system for Broken Divinity.

Provides Ability dataclasses and AbilityRegistry for managing combat abilities.
Integrates with the registry foundation and signal bus architecture.

Author: GitHub Copilot
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from src.core.registry import BaseRegistry
from src.core.signals import get_signal_bus, CoreSignal
from src.utils.logging import Log


@dataclass
class AbilityCost:
    """Resource costs for using an ability."""

    ammo: int = 0
    mana: int = 0
    health: int = 0  # Some abilities might cost health

    def can_afford(
        self, current_ammo: int, current_mana: int, current_health: int
    ) -> bool:
        """Check if entity has sufficient resources to use this ability."""
        return (
            current_ammo >= self.ammo
            and current_mana >= self.mana
            and current_health > self.health  # Must have more health than cost
        )

    def apply_cost(
        self, current_ammo: int, current_mana: int, current_health: int
    ) -> tuple[int, int, int]:
        """Apply ability costs and return new resource values."""
        return (
            current_ammo - self.ammo,
            current_mana - self.mana,
            current_health - self.health,
        )


@dataclass
class AbilityEffects:
    """Effects and parameters for an ability."""

    base_damage: Optional[List[int]] = None  # [min, max] damage range
    heal_amount: Optional[List[int]] = None  # [min, max] healing range
    accuracy_modifier: int = 0  # Bonus/penalty to hit chance
    defense_bonus: int = 0  # Temporary defense increase
    critical_chance: float = 0.0  # Additional crit chance (0.0-1.0)
    duration: int = 0  # How many turns effect lasts
    removes_bleeding: bool = False
    blocks_movement: bool = False

    def get_damage_range(self) -> tuple[int, int]:
        """Get min/max damage values."""
        if self.base_damage and len(self.base_damage) >= 2:
            return (self.base_damage[0], self.base_damage[1])
        return (0, 0)

    def get_heal_range(self) -> tuple[int, int]:
        """Get min/max healing values."""
        if self.heal_amount and len(self.heal_amount) >= 2:
            return (self.heal_amount[0], self.heal_amount[1])
        return (0, 0)


@dataclass
class Ability:
    """Core ability data structure."""

    id: str
    name: str
    description: str
    type: str  # "attack", "heal", "defense", "utility"
    damage_type: str  # "ballistic", "infernal", "none"
    cost: AbilityCost
    cooldown: int  # Turns before ability can be used again
    range: int  # Maximum range in grid squares
    targeting: str  # "single", "self", "self_or_ally", "area", "line", "cone"
    effects: AbilityEffects
    animation: str = "default"
    sound: str = "default"

    def is_attack_ability(self) -> bool:
        """Check if this is an attack ability."""
        return self.type == "attack"

    def is_heal_ability(self) -> bool:
        """Check if this is a healing ability."""
        return self.type == "heal"

    def is_self_targeting(self) -> bool:
        """Check if this ability only targets self."""
        return self.targeting in ["self"]

    def can_target_allies(self) -> bool:
        """Check if this ability can target friendly units."""
        return self.targeting in ["self_or_ally", "ally"]

    def get_damage_range(self) -> tuple[int, int]:
        """Get the damage range for this ability."""
        return self.effects.get_damage_range()

    def get_heal_range(self) -> tuple[int, int]:
        """Get the healing range for this ability."""
        return self.effects.get_heal_range()


class AbilityRegistry(BaseRegistry[Ability]):
    """Registry for managing combat abilities."""

    def __init__(self, data_path: Optional[Path] = None):
        default_path = Path("data/abilities")
        config = RegistryConfig(
            data_path=str(data_path or default_path),
            file_pattern="*.json",
            recursive_scan=True,
            auto_load=False,  # Don't auto-load in constructor
            validate_on_load=True,
        )
        super().__init__(config)

        Log.p(
            "ABILITY",
            [f"AbilityRegistry initialized with path: {self.config.data_path}"],
        )

    def _get_item_id(self, item: Ability) -> str:
        """Get the unique identifier for an ability."""
        return item.id

    def _load_item_from_dict(self, data: Dict[str, Any], file_path: Path) -> Ability:
        """Load an ability from dictionary data."""
        return self._parse_ability_data(data)

    def _validate_item(self, item: Ability) -> bool:
        """Validate an ability object."""
        if not item.id or not item.name:
            Log.p("ABILITY", [f"Ability missing id or name: {item}"])
            return False

        if item.type not in ["attack", "heal", "defense", "utility"]:
            Log.p("ABILITY", [f"Unknown ability type '{item.type}' for {item.id}"])

        if item.damage_type not in ["ballistic", "infernal", "none"]:
            Log.p(
                "ABILITY", [f"Unknown damage type '{item.damage_type}' for {item.id}"]
            )

        if item.cooldown < 0:
            Log.p("ABILITY", [f"Invalid cooldown {item.cooldown} for {item.id}"])
            return False

        if item.range < 0:
            Log.p("ABILITY", [f"Invalid range {item.range} for {item.id}"])
            return False

        return True

    def _load_item_from_file(self, file_path: Path) -> List[Ability]:
        """Load abilities from a JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            abilities = []

            # Handle different JSON structures
            if isinstance(data, dict):
                if "detective_abilities" in data:
                    # Detective abilities format
                    ability_list = data["detective_abilities"]
                elif "abilities" in data:
                    # Generic abilities format
                    ability_list = data["abilities"]
                else:
                    # Assume the dict is a single ability
                    ability_list = [data]
            elif isinstance(data, list):
                ability_list = data
            else:
                Log.p("ABILITY", [f"Invalid JSON structure in {file_path}"])
                return []

            for ability_data in ability_list:
                ability = self._parse_ability_data(ability_data)
                abilities.append(ability)

            Log.p("ABILITY", [f"Loaded {len(abilities)} abilities from {file_path}"])
            return abilities

        except Exception as e:
            Log.p("ABILITY", [f"Failed to load abilities from {file_path}: {e}"])
            return []

    def _parse_ability_data(self, data: Dict[str, Any]) -> Ability:
        """Parse ability data from JSON into Ability object."""
        # Parse cost data
        cost_data = data.get("cost", {})
        cost = AbilityCost(
            ammo=cost_data.get("ammo", 0),
            mana=cost_data.get("mana", 0),
            health=cost_data.get("health", 0),
        )

        # Parse effects data
        effects_data = data.get("effects", {})
        effects = AbilityEffects(
            base_damage=effects_data.get("base_damage"),
            heal_amount=effects_data.get("heal_amount"),
            accuracy_modifier=effects_data.get("accuracy_modifier", 0),
            defense_bonus=effects_data.get("defense_bonus", 0),
            critical_chance=effects_data.get("critical_chance", 0.0),
            duration=effects_data.get("duration", 0),
            removes_bleeding=effects_data.get("removes_bleeding", False),
            blocks_movement=effects_data.get("blocks_movement", False),
        )

        # Create ability
        ability = Ability(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            type=data["type"],
            damage_type=data["damage_type"],
            cost=cost,
            cooldown=data["cooldown"],
            range=data["range"],
            targeting=data["targeting"],
            effects=effects,
            animation=data.get("animation", "default"),
            sound=data.get("sound", "default"),
        )

        Log.p("ABILITY", [f"Parsed ability: {ability.name} ({ability.id})"])
        return ability

    def get_abilities_by_type(self, ability_type: str) -> List[Ability]:
        """Get all abilities of a specific type."""
        return [
            ability for ability in self._data.values() if ability.type == ability_type
        ]

    def get_attack_abilities(self) -> List[Ability]:
        """Get all attack abilities."""
        return self.get_abilities_by_type("attack")

    def get_heal_abilities(self) -> List[Ability]:
        """Get all healing abilities."""
        return self.get_abilities_by_type("heal")

    def get_defense_abilities(self) -> List[Ability]:
        """Get all defensive abilities."""
        return self.get_abilities_by_type("defense")

    def get_abilities_for_entity(self, entity_id: str) -> List[Ability]:
        """Get abilities available to a specific entity."""
        # For now, return all abilities
        # Later this can be filtered by entity class, level, etc.
        return list(self._data.values())


# Global registry instance
_ability_registry: Optional[AbilityRegistry] = None


def get_ability_registry() -> AbilityRegistry:
    """Get the global ability registry instance."""
    global _ability_registry
    if _ability_registry is None:
        _ability_registry = AbilityRegistry()
        _ability_registry.load_data()
        emit_signal(
            CoreSignal.REGISTRY_INITIALIZED,
            "AbilityRegistry",
            {
                "registry_name": "abilities",
                "item_count": _ability_registry.get_item_count(),
            },
        )
    return _ability_registry


def setup_ability_registry(data_path: Optional[Path] = None) -> AbilityRegistry:
    """Setup the ability registry with a specific path."""
    global _ability_registry
    _ability_registry = AbilityRegistry(data_path)
    _ability_registry.load_data()
    emit_signal(
        CoreSignal.REGISTRY_INITIALIZED,
        "AbilityRegistry",
        {
            "registry_name": "abilities",
            "item_count": _ability_registry.get_item_count(),
        },
    )
    return _ability_registry
