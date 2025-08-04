"""
Core ability system for Broken Divinity.

Provides Ability dataclasses and AbilityRegistry for managing combat abilities.
Integrates with the registry foundation and signal bus architecture.

Author: GitHub Copilot
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from pathlib import Path

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
    status_effects: Optional[List[str]] = None  # Status effects to apply
    removes_bleeding: bool = False  # Can remove bleeding status
    duration: int = 0  # Duration for effects that have a time component

    def get_damage_range(self) -> tuple[int, int]:
        """Get damage range as a tuple."""
        if self.base_damage and len(self.base_damage) >= 2:
            return (self.base_damage[0], self.base_damage[1])
        return (0, 0)

    def get_heal_range(self) -> tuple[int, int]:
        """Get healing range as a tuple."""
        if self.heal_amount and len(self.heal_amount) >= 2:
            return (self.heal_amount[0], self.heal_amount[1])
        return (0, 0)


@dataclass
class Ability:
    """Core ability data structure."""

    id: str
    name: str
    description: str
    type: str  # "attack", "defense", "utility", "heal"
    damage_type: str  # "ballistic", "energy", "explosive", "holy"
    cost: AbilityCost
    cooldown: int
    range: int
    targeting: str  # "single", "area", "self"
    effects: AbilityEffects
    restrictions: Optional[List[str]] = None  # Alignment or other restrictions

    def can_use(
        self, current_ammo: int, current_mana: int, current_health: int
    ) -> bool:
        """Check if ability can be used with current resources."""
        return self.cost.can_afford(current_ammo, current_mana, current_health)

    def is_attack_ability(self) -> bool:
        """Check if this is an attack ability."""
        return self.type == "attack"

    def is_heal_ability(self) -> bool:
        """Check if this is a healing ability."""
        return self.type == "heal"

    def is_self_targeting(self) -> bool:
        """Check if this ability targets self."""
        return self.targeting == "self"

    def get_damage_range(self) -> tuple[int, int]:
        """Get damage range from effects."""
        return self.effects.get_damage_range()

    def get_heal_range(self) -> tuple[int, int]:
        """Get heal range from effects."""
        return self.effects.get_heal_range()

    def can_target_allies(self) -> bool:
        """Check if this ability can target allies."""
        # Healing abilities can target allies
        # Self-targeting abilities cannot target allies (they target self only)
        # Attack abilities generally cannot target allies
        return self.type in ("heal", "utility") and self.targeting != "self"


class AbilityRegistry(BaseRegistry[Ability]):
    """Registry for managing game abilities loaded from JSON data."""

    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the ability registry."""
        super().__init__("Ability")
        self._entities_abilities: Dict[str, List[str]] = {}
        self._data_path = data_path

        Log.p("AbilityReg", ["Ability registry initialized"])

        # Load data if path provided
        if data_path:
            self.load_from_directory(data_path)

    def load_data(self) -> None:
        """Load or reload data from the configured path."""
        if self._data_path:
            self.load_from_directory(self._data_path)
        else:
            Log.p("AbilityReg", ["No data path configured for load_data()"])

    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> Ability:
        """Load an Ability from dictionary data."""
        # Parse cost data
        cost_data = item_data.get("cost", {})
        cost = AbilityCost(
            ammo=cost_data.get("ammo", 0),
            mana=cost_data.get("mana", 0),
            health=cost_data.get("health", 0),
        )

        # Parse effects data
        effects_data = item_data.get("effects", {})
        effects = AbilityEffects(
            base_damage=effects_data.get("base_damage"),
            heal_amount=effects_data.get("heal_amount"),
            accuracy_modifier=effects_data.get("accuracy_modifier", 0),
            defense_bonus=effects_data.get("defense_bonus", 0),
            status_effects=effects_data.get("status_effects"),
            removes_bleeding=effects_data.get("removes_bleeding", False),
            duration=effects_data.get("duration", 0),
        )

        return Ability(
            id=item_data["id"],
            name=item_data["name"],
            description=item_data["description"],
            type=item_data["type"],
            damage_type=item_data["damage_type"],
            cost=cost,
            cooldown=item_data.get("cooldown", 0),
            range=item_data.get("range", 1),
            targeting=item_data.get("targeting", "single"),
            effects=effects,
            restrictions=item_data.get("restrictions"),
        )

    def _get_item_id(self, item: Ability) -> str:
        """Get the ID of an Ability."""
        return item.id

    def load_from_directory(self, data_path: Path) -> None:
        """Override to also process entity-ability mappings."""
        super().load_from_directory(data_path)

        # Process entity-ability mappings after loading
        self._process_entity_abilities()

    def _process_entity_abilities(self) -> None:
        """Process detective_abilities and other entity mappings."""
        # This would be expanded to handle the JSON structure like:
        # {"detective_abilities": [list of ability IDs]}
        # For now, we'll implement basic functionality
        self._entities_abilities.clear()

        # Look for detective abilities in our loaded data
        detective_abilities = []
        for ability_id, ability in self.get_all_items().items():
            # For now, assume all abilities can be used by detective
            # This can be refined based on restrictions
            if not ability.restrictions or "detective" not in ability.restrictions:
                detective_abilities.append(ability_id)

        if detective_abilities:
            self._entities_abilities["detective"] = detective_abilities

        Log.p(
            "AbilityReg",
            ["Processed entity abilities:", len(self._entities_abilities), "entities"],
        )

    def get_abilities_for_entity(self, entity_type: str) -> List[Ability]:
        """Get all abilities available to a specific entity type."""
        ability_ids = self._entities_abilities.get(entity_type, [])
        abilities = []

        for ability_id in ability_ids:
            ability = self.get_item(ability_id)
            if ability:
                abilities.append(ability)

        return abilities

    def get_ability_by_name(self, name: str) -> Optional[Ability]:
        """Get an ability by its display name."""
        for ability in self.get_all_items().values():
            if ability.name == name:
                return ability
        return None

    def has_item(self, item_id: str) -> bool:
        """Check if an item exists in the registry."""
        return self.get_item(item_id) is not None

    def get_attack_abilities(self) -> List[Ability]:
        """Get all attack abilities."""
        return [
            ability
            for ability in self.get_all_items().values()
            if ability.is_attack_ability()
        ]

    def get_heal_abilities(self) -> List[Ability]:
        """Get all healing abilities."""
        return [
            ability
            for ability in self.get_all_items().values()
            if ability.is_heal_ability()
        ]


# Global registry instance
_ability_registry: Optional[AbilityRegistry] = None


def get_ability_registry() -> AbilityRegistry:
    """Get the global ability registry instance."""
    global _ability_registry

    if _ability_registry is None:
        _ability_registry = AbilityRegistry()

    return _ability_registry


def setup_ability_registry(data_path: Path) -> AbilityRegistry:
    """Set up the global ability registry with data from the specified path."""
    global _ability_registry

    _ability_registry = AbilityRegistry()
    _ability_registry.load_from_directory(data_path)

    # Emit completion signal
    signal_bus = get_signal_bus()
    signal_bus.emit(
        CoreSignal.REGISTRY_INITIALIZED,
        "AbilityRegistry",
        {
            "registry_name": "abilities",  # Use plural form as expected by tests
            "item_count": _ability_registry.get_item_count(),
        },
    )

    return _ability_registry


# EOF
