"""
Suffix Registry System for Broken Divinity.

Provides procedural generation of prefix/suffix modifiers for entities, weapons,
and NPCs using Diablo/Borderlands-style affix systems with rarity weighting.

Author: GitHub Copilot
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
import random

from src.core.registry import BaseRegistry
from src.core.signals import get_signal_bus, CoreSignal
from src.utils.logging import Log


class SuffixType(Enum):
    """Types of suffixes that can be applied."""

    PREFIX = "prefix"
    SUFFIX = "suffix"


class SuffixRarity(Enum):
    """Rarity tiers for suffix generation."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"


@dataclass
class Suffix:
    """A single suffix/prefix modifier that can be applied to entities or items."""

    id: str
    name: str
    description: str = ""
    type: SuffixType = SuffixType.PREFIX
    rarity: SuffixRarity = SuffixRarity.COMMON
    stat_modifiers: Dict[str, int] = field(default_factory=dict)
    special_effects: List[str] = field(default_factory=list)
    restrictions: Optional[List[str]] = None
    weight: int = 50

    def can_apply_to(self, target_type: str) -> bool:
        """Check if this suffix can be applied to the given target type."""
        if not self.restrictions:
            return True  # Universal suffix
        return target_type in self.restrictions

    def apply_to_stats(self, base_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Apply this suffix's stat modifiers to base stats."""
        modified_stats = base_stats.copy()

        for stat, modifier in self.stat_modifiers.items():
            if stat in modified_stats:
                if isinstance(modified_stats[stat], (int, float)):
                    modified_stats[stat] += modifier
                else:
                    # For non-numeric stats, log warning
                    Log.p(
                        "SuffixReg",
                        [
                            f"Cannot modify non-numeric stat '{stat}' with value {modified_stats[stat]}"
                        ],
                    )
            else:
                # Add new stat if it doesn't exist
                modified_stats[stat] = modifier

        return modified_stats


class SuffixRegistry(BaseRegistry[Suffix]):
    """Registry for managing procedural suffix/prefix modifiers."""

    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the suffix registry."""
        super().__init__("Suffix")
        self._data_path = data_path

        Log.p("SuffixReg", ["Suffix registry initialized"])

        # Load data if path provided
        if data_path:
            self.load_from_directory(data_path)

    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> Suffix:
        """Load a Suffix from dictionary data."""
        # Validate required fields
        required_fields = ["id", "name", "type", "rarity"]
        for field in required_fields:
            if field not in item_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse enum fields
        try:
            suffix_type = SuffixType(item_data["type"])
        except ValueError:
            raise ValueError(f"Invalid suffix type: {item_data['type']}")

        try:
            suffix_rarity = SuffixRarity(item_data["rarity"])
        except ValueError:
            raise ValueError(f"Invalid suffix rarity: {item_data['rarity']}")

        # Validate stat_modifiers is a dictionary if present
        stat_modifiers = item_data.get("stat_modifiers", {})
        if not isinstance(stat_modifiers, dict):
            raise ValueError("stat_modifiers must be a dictionary")

        # Validate special_effects is a list if present
        special_effects = item_data.get("special_effects", [])
        if not isinstance(special_effects, list):
            raise ValueError("special_effects must be a list")

        # Validate restrictions is a list if present
        restrictions = item_data.get("restrictions")
        if restrictions is not None and not isinstance(restrictions, list):
            raise ValueError("restrictions must be a list")

        # Validate weight is a positive integer
        weight = item_data.get("weight", 50)
        if not isinstance(weight, int) or weight <= 0:
            raise ValueError("weight must be a positive integer")

        return Suffix(
            id=item_data["id"],
            name=item_data["name"],
            description=item_data.get("description", ""),
            type=suffix_type,
            rarity=suffix_rarity,
            stat_modifiers=stat_modifiers,
            special_effects=special_effects,
            restrictions=restrictions,
            weight=weight,
        )

    def _get_item_id(self, item: Suffix) -> str:
        """Get the ID of a Suffix."""
        return item.id

    def load_data(self) -> None:
        """Load or reload data from the configured path."""
        if self._data_path:
            self.load_from_directory(self._data_path)
        else:
            Log.p("SuffixReg", ["No data path configured for load_data()"])

    def get_prefixes(self) -> List[Suffix]:
        """Get all prefix suffixes."""
        return [
            suffix
            for suffix in self.get_all_items().values()
            if suffix.type == SuffixType.PREFIX
        ]

    def get_suffixes(self) -> List[Suffix]:
        """Get all suffix-type suffixes."""
        return [
            suffix
            for suffix in self.get_all_items().values()
            if suffix.type == SuffixType.SUFFIX
        ]

    def get_suffixes_by_rarity(self, rarity: SuffixRarity) -> List[Suffix]:
        """Get all suffixes of a specific rarity."""
        return [
            suffix
            for suffix in self.get_all_items().values()
            if suffix.rarity == rarity
        ]

    def get_applicable_suffixes(self, target_type: str) -> List[Suffix]:
        """Get all suffixes that can be applied to a specific target type."""
        return [
            suffix
            for suffix in self.get_all_items().values()
            if suffix.can_apply_to(target_type)
        ]

    def select_random_suffix(
        self,
        target_type: Optional[str] = None,
        suffix_type: Optional[SuffixType] = None,
        rarity_filter: Optional[SuffixRarity] = None,
    ) -> Optional[Suffix]:
        """Select a random suffix based on weights and filters."""
        # Get candidates based on filters
        candidates = list(self.get_all_items().values())

        if target_type:
            candidates = [s for s in candidates if s.can_apply_to(target_type)]

        if suffix_type:
            candidates = [s for s in candidates if s.type == suffix_type]

        if rarity_filter:
            candidates = [s for s in candidates if s.rarity == rarity_filter]

        if not candidates:
            return None

        # Weighted selection
        total_weight = sum(suffix.weight for suffix in candidates)
        if total_weight == 0:
            return None

        selection_point = random.randint(1, total_weight)
        current_weight = 0

        for suffix in candidates:
            current_weight += suffix.weight
            if current_weight >= selection_point:
                return suffix

        # Fallback (shouldn't happen)
        return candidates[-1] if candidates else None

    def generate_entity_variant(
        self,
        base_name: str,
        base_stats: Dict[str, Any],
        max_suffixes: int = 2,
        force_generation: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an entity variant with random suffixes applied.

        Args:
            base_name: The base entity name (e.g., "imp")
            base_stats: Base stats to modify
            max_suffixes: Maximum number of suffixes to apply
            force_generation: If True, always apply at least one suffix

        Returns:
            Dictionary with variant name, stats, and applied suffixes, or None if no variant
        """
        # Determine how many suffixes to apply
        if force_generation:
            num_suffixes = random.randint(1, max_suffixes)
        else:
            # 70% chance to apply suffixes
            if random.random() > 0.7:
                return None
            num_suffixes = random.randint(1, max_suffixes)

        applied_suffixes = []
        modified_stats = base_stats.copy()
        name_parts = [base_name]

        # Apply prefixes first
        prefixes_to_apply = min(num_suffixes, 1)  # Max 1 prefix for now
        for _ in range(prefixes_to_apply):
            prefix = self.select_random_suffix(
                target_type="entity", suffix_type=SuffixType.PREFIX
            )
            if prefix and prefix not in applied_suffixes:
                applied_suffixes.append(prefix)
                modified_stats = prefix.apply_to_stats(modified_stats)
                name_parts.insert(0, prefix.name)  # Prefixes go before base name

        # Apply suffixes if we have room
        remaining_slots = num_suffixes - len(applied_suffixes)
        for _ in range(remaining_slots):
            suffix = self.select_random_suffix(
                target_type="entity", suffix_type=SuffixType.SUFFIX
            )
            if suffix and suffix not in applied_suffixes:
                applied_suffixes.append(suffix)
                modified_stats = suffix.apply_to_stats(modified_stats)
                name_parts.append(suffix.name)  # Suffixes go after base name

        if not applied_suffixes:
            return None

        # Generate variant name
        variant_name = " ".join(name_parts)

        Log.p(
            "SuffixReg",
            [
                f"Generated variant: {variant_name} with {len(applied_suffixes)} suffix(es)"
            ],
        )

        return {
            "name": variant_name,
            "base_name": base_name,
            "stats": modified_stats,
            "applied_suffixes": applied_suffixes,
            "special_effects": [
                effect
                for suffix in applied_suffixes
                for effect in suffix.special_effects
            ],
        }

    def generate_weapon_variant(
        self, base_name: str, base_stats: Dict[str, Any], max_suffixes: int = 3
    ) -> Optional[Dict[str, Any]]:
        """Generate a weapon variant with suffix combinations (simplified for now)."""
        # Similar to entity variant but for weapons
        # Implementation would be expanded later for weapon-specific logic
        return self.generate_entity_variant(
            base_name, base_stats, max_suffixes, force_generation=True
        )

    def get_suffix_combinations_count(self) -> int:
        """Get the total number of possible suffix combinations."""
        prefixes = len(self.get_prefixes())
        suffixes = len(self.get_suffixes())

        # Simple calculation: prefixes * suffixes * (no suffix option)
        # More complex calculation would account for multi-suffix combinations
        return (prefixes + 1) * (suffixes + 1)


# Global registry instance
_suffix_registry: Optional[SuffixRegistry] = None


def get_suffix_registry() -> SuffixRegistry:
    """Get the global suffix registry instance."""
    global _suffix_registry
    if _suffix_registry is None:
        _suffix_registry = SuffixRegistry()
    return _suffix_registry


def setup_suffix_registry(data_path: Optional[Path] = None) -> SuffixRegistry:
    """Setup the suffix registry with a specific path."""
    global _suffix_registry
    _suffix_registry = SuffixRegistry(data_path)
    return _suffix_registry


# EOF
