"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Basic Item System                                                           ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Basic item data structures and examination                  ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.11                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Item:
    """Basic item data structure"""

    name: str
    description: str
    item_type: str
    properties: Dict[str, Any]


class ItemExaminer:
    """Provides detailed examination of items"""

    def examine(self, item: Item) -> str:
        """Examine an item and return detailed description"""
        examination = item.description

        # Add property-based details
        if item.item_type == "weapon":
            if "damage" in item.properties:
                examination += f"\nDamage: {item.properties['damage']}"
            if "damage_type" in item.properties:
                examination += f"\nDamage Type: {item.properties['damage_type']}"

        elif item.item_type == "armor":
            if "defense_bonus" in item.properties:
                examination += f"\nDefense Bonus: +{item.properties['defense_bonus']}"

        return examination


# EOF
