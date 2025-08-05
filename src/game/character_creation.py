"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Character Creation System                                                   ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019               ║
║  Purpose       : Character background selection and creation workflow       ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.12                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional

log = logging.getLogger("[CharCreate]")


@dataclass
class CharacterBackground:
    """Character background loaded from JSON data."""

    id: str
    name: str
    display_name: str
    description: str
    flavor_text: str
    stat_modifiers: Dict[str, int]
    starting_items: List[str]
    starting_abilities: List[str]
    starting_status_effects: List[str]
    background_skills: List[Dict[str, str]]
    personality_traits: List[str]
    dialogue_options: Dict[str, List[str]]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "CharacterBackground":
        """Create CharacterBackground from JSON data."""
        return cls(
            id=data["id"],
            name=data["name"],
            display_name=data["display_name"],
            description=data["description"],
            flavor_text=data["flavor_text"],
            stat_modifiers=data["stat_modifiers"],
            starting_items=data["starting_items"],
            starting_abilities=data["starting_abilities"],
            starting_status_effects=data["starting_status_effects"],
            background_skills=data["background_skills"],
            personality_traits=data["personality_traits"],
            dialogue_options=data["dialogue_options"],
        )


@dataclass
class Character:
    """Player character with background and stats."""

    background_id: str
    base_stats: Dict[str, int]
    starting_items: List[str]
    starting_abilities: List[str]
    starting_status_effects: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary for saving."""
        return asdict(self)


class CharacterCreator:
    """Handles character creation and background loading."""

    def __init__(self):
        """Initialize character creator and load backgrounds."""
        self.available_backgrounds: List[CharacterBackground] = []
        self._load_backgrounds()
        log.info(f"Loaded {len(self.available_backgrounds)} character backgrounds")

    def _load_backgrounds(self) -> None:
        """Load all character backgrounds from JSON files."""
        backgrounds_dir = Path("data/character_backgrounds")

        if not backgrounds_dir.exists():
            log.warning(f"Character backgrounds directory not found: {backgrounds_dir}")
            return

        for json_file in backgrounds_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                background = CharacterBackground.from_json(data)
                self.available_backgrounds.append(background)
                log.debug(f"Loaded background: {background.display_name}")

            except (json.JSONDecodeError, KeyError) as e:
                log.error(f"Error loading background from {json_file}: {e}")
            except Exception as e:
                log.error(f"Unexpected error loading {json_file}: {e}")

    def create_character(self, background: CharacterBackground) -> Character:
        """Create a character with the specified background."""
        log.info(f"Creating character with {background.display_name} background")

        # Base stats (all stats start at 10)
        base_stats = {
            "health": 10,
            "mana": 10,
            "stamina": 10,
            "strength": 10,
            "dexterity": 10,
            "intelligence": 10,
            "perception": 10,
            "charisma": 10,
        }

        # Apply background stat modifiers
        for stat, modifier in background.stat_modifiers.items():
            if stat in base_stats:
                base_stats[stat] += modifier
                log.debug(f"Applied {modifier:+d} to {stat} (now {base_stats[stat]})")

        character = Character(
            background_id=background.id,
            base_stats=base_stats,
            starting_items=background.starting_items.copy(),
            starting_abilities=background.starting_abilities.copy(),
            starting_status_effects=background.starting_status_effects.copy(),
        )

        log.info(f"Character created successfully: {background.display_name}")
        return character


# EOF
