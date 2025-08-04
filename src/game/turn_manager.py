"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Turn Manager                                                                ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Turn-based combat initiative and action management         ║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.9                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from src.utils.logging import Log
from src.game.battle_manager import CombatEntity
from src.core.signals import get_signal_bus, CoreSignal


@dataclass
class TurnOrder:
    """Turn order entry with entity and initiative."""

    entity: CombatEntity
    initiative: int

    def __lt__(self, other) -> bool:
        """Compare for sorting - higher initiative goes first."""
        return self.initiative < other.initiative

    def __gt__(self, other) -> bool:
        """Compare for sorting - higher initiative goes first."""
        return self.initiative > other.initiative


@dataclass
class CombatAction:
    """Record of a combat action taken."""

    action_type: str  # "attack", "defend", "ability", "item", "flee"
    actor_name: str
    target_name: Optional[str] = None
    damage: Optional[int] = None
    healing: Optional[int] = None
    mana_cost: Optional[int] = None
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class TurnManager:
    """Manages turn-based combat initiative and actions."""

    def __init__(self):
        """Initialize turn manager."""
        self.turn_order: List[TurnOrder] = []
        self.current_turn_index = 0
        self.turn_number = 0
        self.action_history: List[CombatAction] = []

        self.signal_bus = get_signal_bus()

        Log.p("TurnMgr", ["Turn manager initialized"])

    def calculate_initiative(self, entity: CombatEntity) -> int:
        """Calculate initiative for an entity (speed + random roll)."""
        base_speed = entity.speed
        roll = random.randint(1, 10)  # 1d10 roll
        initiative = base_speed + roll

        Log.p(
            "TurnMgr",
            [f"{entity.name} initiative: {base_speed} + {roll} = {initiative}"],
        )
        return initiative

    def setup_turn_order(self, entities: List[CombatEntity]) -> None:
        """Setup initial turn order for all combat participants."""
        self.turn_order.clear()
        self.current_turn_index = 0
        self.turn_number = 0

        # Calculate initiative for all living entities
        for entity in entities:
            if entity.is_alive():
                initiative = self.calculate_initiative(entity)
                turn_entry = TurnOrder(entity=entity, initiative=initiative)
                self.turn_order.append(turn_entry)

        # Sort by initiative (highest first)
        self.turn_order.sort(reverse=True)

        # Log the turn order
        order_names = [
            f"{entry.entity.name}({entry.initiative})" for entry in self.turn_order
        ]
        Log.p("TurnMgr", [f"Turn order: {' > '.join(order_names)}"])

        # Emit turn started signal for first entity
        if self.turn_order:
            self._emit_turn_started()

    def get_current_actor(self) -> Optional[CombatEntity]:
        """Get the entity whose turn it is."""
        if not self.turn_order or self.current_turn_index >= len(self.turn_order):
            return None

        # Skip dead entities
        while self.current_turn_index < len(self.turn_order):
            current_entry = self.turn_order[self.current_turn_index]
            if current_entry.entity.is_alive():
                return current_entry.entity

            # Skip dead entity
            Log.p("TurnMgr", [f"Skipping dead entity: {current_entry.entity.name}"])
            self.current_turn_index += 1

        # All entities at or after current index are dead, wrap around
        self.current_turn_index = 0
        self.turn_number += 1
        return self.get_current_actor()

    def advance_turn(self) -> Optional[CombatEntity]:
        """Advance to the next turn and return the new current actor."""
        if not self.turn_order:
            return None

        # Emit turn ended signal for current entity
        current_entity = self.get_current_actor()
        if current_entity:
            self.signal_bus.emit(
                CoreSignal.TURN_ENDED,
                "TurnManager",
                {"entity": current_entity.name, "turn_number": self.turn_number},
            )

        # Move to next turn
        self.current_turn_index += 1

        # Check if we've completed a full round
        if self.current_turn_index >= len(self.turn_order):
            self.current_turn_index = 0
            self.turn_number += 1
            Log.p("TurnMgr", [f"Starting turn round {self.turn_number}"])

        # Get next actor and emit turn started signal
        next_actor = self.get_current_actor()
        if next_actor:
            self._emit_turn_started()

        return next_actor

    def is_player_turn(self) -> bool:
        """Check if it's currently the player's turn."""
        current_actor = self.get_current_actor()
        return current_actor is not None and current_actor.entity_type == "player"

    def record_action(self, action: CombatAction) -> None:
        """Record a combat action in the history."""
        self.action_history.append(action)
        Log.p("TurnMgr", [f"Action recorded: {action.description}"])

    def get_recent_actions(self, count: int = 5) -> List[CombatAction]:
        """Get the most recent combat actions."""
        recent = self.action_history[-count:] if self.action_history else []
        return list(reversed(recent))  # Most recent first

    def get_turn_summary(self) -> dict:
        """Get current turn status summary."""
        current_actor = self.get_current_actor()

        return {
            "turn_number": self.turn_number,
            "current_actor": current_actor.name if current_actor else "None",
            "current_index": self.current_turn_index,
            "total_entities": len(self.turn_order),
            "is_player_turn": self.is_player_turn(),
            "turn_order": [
                {
                    "name": entry.entity.name,
                    "initiative": entry.initiative,
                    "alive": entry.entity.is_alive(),
                }
                for entry in self.turn_order
            ],
        }

    def clear_history(self) -> None:
        """Clear action history."""
        self.action_history.clear()
        Log.p("TurnMgr", ["Action history cleared"])

    def reset(self) -> None:
        """Reset turn manager for new battle."""
        self.turn_order.clear()
        self.current_turn_index = 0
        self.turn_number = 0
        self.action_history.clear()
        Log.p("TurnMgr", ["Turn manager reset"])

    def _emit_turn_started(self) -> None:
        """Emit turn started signal for current entity."""
        current_entity = self.get_current_actor()
        if current_entity:
            self.signal_bus.emit(
                CoreSignal.TURN_STARTED,
                "TurnManager",
                {
                    "entity": current_entity.name,
                    "entity_type": current_entity.entity_type,
                    "turn_number": self.turn_number,
                    "is_player_turn": self.is_player_turn(),
                },
            )

    def get_entity_turn_position(self, entity_name: str) -> Optional[int]:
        """Get the turn position of a specific entity."""
        for i, entry in enumerate(self.turn_order):
            if entry.entity.name == entity_name:
                return i
        return None

    def is_entity_turn(self, entity_name: str) -> bool:
        """Check if it's a specific entity's turn."""
        current_actor = self.get_current_actor()
        return current_actor is not None and current_actor.name == entity_name


# EOF
