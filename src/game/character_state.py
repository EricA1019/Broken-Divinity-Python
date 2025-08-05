"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Character State System                                                      ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Track character status effects outside combat              ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.11                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from src.game.state_registry import StateRegistry
from src.utils.logging import Log


@dataclass
class ActiveStatus:
    """Represents an active status effect on the character"""

    effect_name: str
    remaining_minutes: int
    stacks: int = 1


class CharacterState:
    """Manages character status effects outside of combat"""

    def __init__(self):
        self.tag = "CharState"
        self.state_registry = StateRegistry()
        self.state_registry.initialize()
        self.active_statuses: Dict[str, ActiveStatus] = {}
        self.time_minutes = 0  # Game time tracking
        Log.p(self.tag, ["Character state initialized"])

    def apply_status_effect(
        self, effect_name: str, duration_minutes: Optional[int] = None
    ):
        """Apply a status effect to the character"""
        effect = self.state_registry.get_item(effect_name)
        if not effect:
            Log.p(self.tag, [f"Unknown status effect: {effect_name}"])
            return

        # Calculate duration
        if duration_minutes is None:
            duration_minutes = (effect.duration_hours * 60) + effect.duration_minutes

        # Apply or stack the effect
        if effect_name in self.active_statuses:
            current = self.active_statuses[effect_name]
            if current.stacks < effect.max_stacks:
                current.stacks += 1
                Log.p(
                    self.tag, [f"Stacked {effect_name} (now {current.stacks} stacks)"]
                )
        else:
            self.active_statuses[effect_name] = ActiveStatus(
                effect_name=effect_name, remaining_minutes=duration_minutes, stacks=1
            )
            Log.p(self.tag, [f"Applied {effect_name} for {duration_minutes} minutes"])

    def has_status(self, effect_name: str) -> bool:
        """Check if character has a specific status effect"""
        return effect_name in self.active_statuses

    def get_stat_modifier(self, stat_name: str) -> int:
        """Get the total modifier for a stat from all active effects"""
        total_modifier = 0

        for status_name, active_status in self.active_statuses.items():
            effect = self.state_registry.get_item(status_name)
            if effect and effect.stat_changes and stat_name in effect.stat_changes:
                modifier = effect.stat_changes[stat_name] * active_status.stacks
                total_modifier += modifier

        return total_modifier

    def advance_time_minutes(self, minutes: int):
        """Advance game time and update status effect durations"""
        self.time_minutes += minutes
        expired_effects = []

        for status_name, active_status in self.active_statuses.items():
            active_status.remaining_minutes -= minutes
            if active_status.remaining_minutes <= 0:
                expired_effects.append(status_name)

        # Remove expired effects
        for effect_name in expired_effects:
            del self.active_statuses[effect_name]
            Log.p(self.tag, [f"Status effect {effect_name} expired"])

    def advance_time_hours(self, hours: int):
        """Advance game time by hours"""
        self.advance_time_minutes(hours * 60)

    def get_active_statuses(self) -> List[str]:
        """Get list of currently active status effect names"""
        return list(self.active_statuses.keys())


# EOF
