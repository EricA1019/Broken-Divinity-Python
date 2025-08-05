"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Location System                                                             ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Location-based exploration for scene system                ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.11                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from src.utils.logging import Log


@dataclass
class LocationItem:
    """Represents an item that can be found in a location"""

    name: str
    display_name: str
    description: str
    item_type: str
    properties: Dict[str, Any]
    examinable: bool = True
    obtainable: bool = True


class ApartmentLocation:
    """Morrison's apartment - tutorial location"""

    def __init__(self):
        self.tag = "ApartLoc"
        self.name = "Morrison's Apartment"
        self.description = self._get_apartment_description()
        self._setup_items()
        Log.p(self.tag, ["Apartment location initialized"])

    def _get_apartment_description(self) -> str:
        """Get the atmospheric description of the apartment"""
        return """You wake in your cramped apartment. Sunlight filters through dirty windows.
The smell of stale whiskey hangs in the air. Your head pounds mercilessly.

The place is a mess - clothes scattered, empty bottles on the floor, and case files 
spread across the small table. This is what rock bottom looks like for a detective."""

    def _setup_items(self):
        """Initialize the items available in the apartment"""
        self.items = {
            "revolver": LocationItem(
                name="revolver",
                display_name="S&W Model 10 Revolver",
                description="Your old service weapon. A reliable .38 caliber revolver that's seen better days. The metal is worn but well-maintained. It feels heavy with both memories and potential.",
                item_type="weapon",
                properties={
                    "damage_type": "physical.ballistic.38",
                    "damage": 8,
                    "ammo_capacity": 6,
                    "current_ammo": 6,
                },
            ),
            "jacket": LocationItem(
                name="jacket",
                display_name="Old Leather Jacket",
                description="A worn but sturdy leather jacket. The brown leather has seen countless nights on the streets. Despite its age, it still provides decent protection. +2 defense when worn.",
                item_type="armor",
                properties={"defense_bonus": 2, "durability": 75, "weight": 3},
            ),
            "badge": LocationItem(
                name="badge",
                display_name="Detective Badge",
                description="Your detective shield - tarnished but authentic. The metal feels warm to the touch, almost pulsing with an energy you don't understand. This badge is more than just identification now.",
                item_type="special",
                properties={
                    "resurrection_anchor": True,
                    "authority_level": "detective",
                    "blessed": False,  # Will become True after Lucifer encounter
                },
            ),
            "bottle": LocationItem(
                name="bottle",
                display_name="Empty Whiskey Bottle",
                description="An empty bottle of cheap whiskey. The evidence of last night's poor decision-making. The smell alone makes your hangover worse.",
                item_type="junk",
                properties={"value": 0, "reminder_of_shame": True},
                obtainable=False,
            ),
        }

    def get_items(self) -> Dict[str, LocationItem]:
        """Get all items in the location"""
        return self.items

    def examine_item(self, item_name: str) -> Optional[str]:
        """Examine a specific item and return its description"""
        if item_name not in self.items:
            return None

        item = self.items[item_name]
        Log.p(self.tag, [f"Player examined {item.display_name}"])
        return item.description

    def get_item(self, item_name: str) -> Optional[LocationItem]:
        """Get a specific item if it exists"""
        return self.items.get(item_name)

    def apply_initial_status(self):
        """Apply the initial hungover status effect"""
        # This will be called when the player first enters the apartment
        Log.p(self.tag, ["Applying hungover status effect"])
        # The actual status application will be handled by the character state system
        pass


# EOF
