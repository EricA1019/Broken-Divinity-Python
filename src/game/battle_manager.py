"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Battle Manager                                                              ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Combat battle management and entity state tracking         ║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.9                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

from src.utils.logging import Log
from src.game.entity_registry import EntityRegistry
from src.core.signals import get_signal_bus, CoreSignal


class BattleResult(Enum):
    """Battle outcome results."""

    ONGOING = "ongoing"
    VICTORY = "victory"
    DEFEAT = "defeat"
    FLED = "fled"


@dataclass
class CombatEntity:
    """A combat participant with live state tracking."""

    name: str
    entity_type: str  # "player", "enemy", "ally"
    max_hp: int
    current_hp: int
    max_mana: int
    current_mana: int
    attack: int
    defense: int
    speed: int
    status_effects: List[str] = field(default_factory=list)

    def is_alive(self) -> bool:
        """Check if entity is alive."""
        return self.current_hp > 0

    def is_dead(self) -> bool:
        """Check if entity is dead."""
        return self.current_hp <= 0

    def take_damage(self, damage: int) -> int:
        """Apply damage and return actual damage taken."""
        if damage < 0:
            damage = 0

        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage

        if self.current_hp < 0:
            self.current_hp = 0

        Log.p(
            "BattleMgr",
            [
                f"{self.name} takes {actual_damage} damage ({self.current_hp}/{self.max_hp} HP)"
            ],
        )
        return actual_damage

    def heal(self, amount: int) -> int:
        """Heal entity and return actual healing done."""
        if amount < 0:
            amount = 0

        old_hp = self.current_hp
        self.current_hp = min(self.current_hp + amount, self.max_hp)
        actual_healing = self.current_hp - old_hp

        Log.p(
            "BattleMgr",
            [
                f"{self.name} heals {actual_healing} HP ({self.current_hp}/{self.max_hp} HP)"
            ],
        )
        return actual_healing

    def can_spend_mana(self, cost: int) -> bool:
        """Check if entity has enough mana."""
        return self.current_mana >= cost

    def spend_mana(self, cost: int) -> bool:
        """Spend mana if available."""
        if not self.can_spend_mana(cost):
            return False

        self.current_mana -= cost
        Log.p(
            "BattleMgr",
            [
                f"{self.name} spends {cost} mana ({self.current_mana}/{self.max_mana} MP)"
            ],
        )
        return True

    def restore_mana(self, amount: int) -> int:
        """Restore mana and return actual amount restored."""
        if amount < 0:
            amount = 0

        old_mana = self.current_mana
        self.current_mana = min(self.current_mana + amount, self.max_mana)
        actual_restore = self.current_mana - old_mana

        Log.p(
            "BattleMgr",
            [
                f"{self.name} restores {actual_restore} mana ({self.current_mana}/{self.max_mana} MP)"
            ],
        )
        return actual_restore


class BattleManager:
    """Manages combat encounters and entity states."""

    def __init__(self):
        """Initialize battle manager."""
        self.player: Optional[CombatEntity] = None
        self.enemies: List[CombatEntity] = []
        self.allies: List[CombatEntity] = []
        self.battle_active = False
        self.battle_result = BattleResult.ONGOING

        self.entity_registry = EntityRegistry()
        self.entity_registry.initialize()  # Load entity data
        self.signal_bus = get_signal_bus()

        Log.p("BattleMgr", ["Battle manager initialized"])

    def is_battle_active(self) -> bool:
        """Check if battle is currently active."""
        return self.battle_active

    def start_battle(
        self,
        player: CombatEntity,
        enemies: List[CombatEntity],
        allies: Optional[List[CombatEntity]] = None,
    ) -> None:
        """Start battle with given entities."""
        self.player = player
        self.enemies = enemies.copy()
        self.allies = allies.copy() if allies else []
        self.battle_active = True
        self.battle_result = BattleResult.ONGOING

        enemy_names = [e.name for e in enemies]
        Log.p(
            "BattleMgr", [f"Battle started: {player.name} vs {', '.join(enemy_names)}"]
        )

        # Emit battle started signal
        self.signal_bus.emit(
            CoreSignal.COMBAT_STARTED,
            "BattleManager",
            {
                "player": player.name,
                "enemies": enemy_names,
                "allies": [a.name for a in self.allies],
            },
        )

    def start_battle_from_registry(
        self,
        player_name: str,
        enemy_names: List[str],
        ally_names: Optional[List[str]] = None,
    ) -> bool:
        """Start battle using entity registry data."""
        try:
            # Load player entity
            player_data = self.entity_registry.get_item(player_name)
            if not player_data:
                Log.p(
                    "BattleMgr",
                    [f"ERROR: Player entity '{player_name}' not found in registry"],
                )
                return False

            player = self._create_combat_entity_from_data(player_data)

            # Load enemy entities
            enemies = []
            for enemy_name in enemy_names:
                enemy_data = self.entity_registry.get_item(enemy_name)
                if not enemy_data:
                    Log.p(
                        "BattleMgr",
                        [f"ERROR: Enemy entity '{enemy_name}' not found in registry"],
                    )
                    return False

                enemy = self._create_combat_entity_from_data(enemy_data)
                enemies.append(enemy)

            # Load ally entities if specified
            allies = []
            if ally_names:
                for ally_name in ally_names:
                    ally_data = self.entity_registry.get_item(ally_name)
                    if not ally_data:
                        Log.p(
                            "BattleMgr",
                            [f"ERROR: Ally entity '{ally_name}' not found in registry"],
                        )
                        return False

                    ally = self._create_combat_entity_from_data(ally_data)
                    allies.append(ally)

            self.start_battle(player, enemies, allies)
            return True

        except Exception as e:
            Log.p("BattleMgr", [f"ERROR starting battle from registry: {e}"])
            return False

    def _create_combat_entity_from_data(self, entity_data) -> CombatEntity:
        """Create CombatEntity from registry data."""
        return CombatEntity(
            name=entity_data.name,
            entity_type=entity_data.entity_type,
            max_hp=entity_data.base_health,
            current_hp=entity_data.base_health,
            max_mana=entity_data.base_mana,
            current_mana=entity_data.base_mana,
            attack=entity_data.base_attack,
            defense=entity_data.base_defense,
            speed=entity_data.base_speed,
        )

    def get_living_enemies(self) -> List[CombatEntity]:
        """Get all living enemies."""
        return [enemy for enemy in self.enemies if enemy.is_alive()]

    def get_living_allies(self) -> List[CombatEntity]:
        """Get all living allies."""
        return [ally for ally in self.allies if ally.is_alive()]

    def get_all_living_entities(self) -> List[CombatEntity]:
        """Get all living entities in battle."""
        entities = []
        if self.player and self.player.is_alive():
            entities.append(self.player)
        entities.extend(self.get_living_enemies())
        entities.extend(self.get_living_allies())
        return entities

    def check_battle_end(self) -> BattleResult:
        """Check if battle should end and return result."""
        if not self.battle_active:
            return self.battle_result

        # Check if player is dead
        if not self.player or self.player.is_dead():
            self._end_battle(BattleResult.DEFEAT)
            return BattleResult.DEFEAT

        # Check if all enemies are dead
        living_enemies = self.get_living_enemies()
        if len(living_enemies) == 0:
            self._end_battle(BattleResult.VICTORY)
            return BattleResult.VICTORY

        return BattleResult.ONGOING

    def flee_battle(self) -> bool:
        """Attempt to flee from battle."""
        if not self.battle_active:
            return False

        # TODO: Add flee chance calculation based on speed, enemy types, etc.
        # For now, always allow fleeing
        self._end_battle(BattleResult.FLED)
        Log.p("BattleMgr", ["Player fled from battle"])
        return True

    def _end_battle(self, result: BattleResult) -> None:
        """End the battle with given result."""
        self.battle_active = False
        self.battle_result = result

        Log.p("BattleMgr", [f"Battle ended: {result.value}"])

        # Emit battle ended signal
        self.signal_bus.emit(
            CoreSignal.COMBAT_ENDED,
            "BattleManager",
            {
                "result": result.value,
                "player_alive": self.player.is_alive() if self.player else False,
                "enemies_defeated": len([e for e in self.enemies if e.is_dead()]),
            },
        )

    def get_battle_summary(self) -> dict:
        """Get current battle status summary."""
        if not self.battle_active:
            return {"active": False, "result": self.battle_result.value}

        return {
            "active": True,
            "player": {
                "name": self.player.name if self.player else "None",
                "hp": (
                    f"{self.player.current_hp}/{self.player.max_hp}"
                    if self.player
                    else "0/0"
                ),
                "mana": (
                    f"{self.player.current_mana}/{self.player.max_mana}"
                    if self.player
                    else "0/0"
                ),
            },
            "enemies": [
                {
                    "name": enemy.name,
                    "hp": f"{enemy.current_hp}/{enemy.max_hp}",
                    "alive": enemy.is_alive(),
                }
                for enemy in self.enemies
            ],
            "living_enemies": len(self.get_living_enemies()),
        }


# EOF
