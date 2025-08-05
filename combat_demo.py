#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Combat Demo Script                                                          ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Demonstrate live combat with imp vs detective              ║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.10                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from src.game.game_state_machine import GameStateMachine, GameState
from src.game.battle_manager import BattleManager
from src.game.turn_manager import TurnManager
from src.utils.logging import Log
from src.core.signals import reset_signal_bus


def run_combat_demo():
    """Run a live combat demonstration."""
    print("🎮 Starting Broken Divinity Combat Demo - Hop 10")
    print("=" * 60)

    # Reset signal bus for clean state
    reset_signal_bus()

    # Initialize game systems
    print("\n📋 Initializing game systems...")
    state_machine = GameStateMachine()
    battle_manager = BattleManager()
    turn_manager = TurnManager()

    # Start battle: Detective vs Imp
    print("\n⚔️ Starting battle: Detective vs Imp")
    success = battle_manager.start_battle_from_registry("detective", ["imp"])

    if not success:
        print("❌ Failed to start battle!")
        return False

    print("✅ Battle started successfully!")

    # Setup turn order
    all_entities = [
        e for e in [battle_manager.player] + battle_manager.enemies if e is not None
    ]
    turn_manager.setup_turn_order(all_entities)

    # Transition to exploration, then combat
    print("\n🗺️ Transitioning to exploration...")
    state_machine.transition_to(GameState.EXPLORATION)
    exploration_screen = state_machine.get_current_screen()
    if exploration_screen.status:
        print(f"📍 Current location: {exploration_screen.status.location}")

    print("\n⚔️ Entering combat mode...")
    state_machine.transition_to(GameState.COMBAT)
    combat_screen = state_machine.get_current_screen()

    # Display combat screen
    print("\n" + "=" * 60)
    print(f"🏆 {combat_screen.title}")
    print("=" * 60)
    print(combat_screen.description)
    print("=" * 60)

    # Display status
    status = combat_screen.status
    if status:
        print(f"📍 Location: {status.location}")
        print(f"⏰ Time: {status.time}")
        if hasattr(status, "hp") and status.hp:
            print(f"❤️ HP: {status.hp}/{status.max_hp}")
        if hasattr(status, "mana") and status.mana:
            print(f"🔮 MP: {status.mana}/{status.max_mana}")

    print("\n🎯 Available Actions:")
    for option in combat_screen.options:
        status_icon = "✅" if option.enabled else "❌"
        print(f"  {status_icon} [{option.key}] {option.text} - {option.description}")

    # Display turn order
    print("\n🔄 Turn Order:")
    for i, turn_entry in enumerate(turn_manager.turn_order):
        entity = turn_entry.entity
        current_marker = "👉" if i == turn_manager.current_turn_index else "  "
        print(f"  {current_marker} {entity.name} (Initiative: {turn_entry.initiative})")
        print(
            f"     ❤️ {entity.current_hp}/{entity.max_hp} HP | 🔮 {entity.current_mana}/{entity.max_mana} MP"
        )

    # Display battle status
    print(
        f"\n📊 Battle Status: {'Active' if battle_manager.is_battle_active() else 'Inactive'}"
    )

    # Show infernal abilities
    print("\n🔥 Infernal Abilities Available:")
    from src.game.abilities import AbilityRegistry
    from pathlib import Path

    ability_registry = AbilityRegistry()
    ability_registry.load_from_directory(Path("data/abilities"))

    infernal_abilities = ["infernal_bolt", "shadow_step", "minor_curse"]
    for ability_id in infernal_abilities:
        ability = ability_registry.get_item(ability_id)
        if ability:
            print(f"  🔥 {ability.name} - {ability.description}")
            print(f"     💫 Type: {ability.type} | 🎯 Target: {ability.targeting}")
        else:
            print(f"  ❌ {ability_id} - Not found")

    print("\n" + "=" * 60)
    print("🎉 Combat Demo Complete!")
    print("✅ All systems operational:")
    print("  - Entity loading from JSON")
    print("  - Battle manager integration")
    print("  - Turn order calculation")
    print("  - State machine transitions")
    print("  - Live combat screen display")
    print("  - Infernal damage type system")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = run_combat_demo()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
