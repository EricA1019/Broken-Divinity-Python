"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Broken Divinity - Main Entry Point                                         ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Game entry point with registry initialization and testing  ║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.9                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
from typing import NoReturn
from pathlib import Path

from src.utils.logging import Log
from src.game.state_registry import StateRegistry
from src.game.buff_registry import BuffRegistry
from src.game.entity_registry import EntityRegistry
from src.game.abilities import AbilityRegistry
from src.game.suffix_registry import SuffixRegistry
from src.ui.main_ui import MainUI, MenuScreen, MenuOption, StatusData


def test_registries() -> bool:
    """Test all registries to ensure they load correctly."""
    Log.p("Main", ["Testing registry systems..."])

    try:
        # Test StateRegistry
        state_registry = StateRegistry()
        state_registry.initialize()
        state_count = state_registry.get_item_count()
        Log.p("Main", [f"StateRegistry loaded {state_count} status effects"])

        if state_count == 0:
            Log.p("Main", ["ERROR: StateRegistry loaded no items"])
            return False

        # Verify some expected effects exist
        expected_effects = ["stun", "bleed", "poison", "slow", "haste"]
        for effect in expected_effects:
            if not state_registry.get_item(effect):
                Log.p("Main", [f"ERROR: Missing expected status effect: {effect}"])
                return False

        # Test BuffRegistry
        buff_registry = BuffRegistry()
        buff_registry.initialize()
        buff_count = buff_registry.get_item_count()
        Log.p("Main", [f"BuffRegistry loaded {buff_count} buff effects"])

        if buff_count == 0:
            Log.p("Main", ["ERROR: BuffRegistry loaded no items"])
            return False

        # Verify some expected buffs exist
        expected_buffs = [
            "rage",
            "shield_wall",
            "combat_focus",
            "combat_training",
            "blessing",
        ]
        for buff in expected_buffs:
            if not buff_registry.get_item(buff):
                Log.p("Main", [f"ERROR: Missing expected buff: {buff}"])
                return False

        Log.p("Main", ["✅ BuffRegistry validation successful"])

        # Test EntityRegistry
        Log.p("Main", ["Testing EntityRegistry..."])
        entity_registry = EntityRegistry()
        entity_registry.initialize()

        entity_count = entity_registry.get_item_count()
        Log.p("Main", [f"EntityRegistry loaded {entity_count} entities"])

        if entity_count == 0:
            Log.p("Main", ["ERROR: EntityRegistry loaded no items"])
            return False

        # Verify some expected entities exist
        expected_entities = [
            "detective",
            "street_thug",
            "gang_lieutenant",
            "crime_boss",
            "corrupt_officer",
        ]
        for entity in expected_entities:
            if not entity_registry.get_item(entity):
                Log.p("Main", [f"ERROR: Missing expected entity: {entity}"])
                return False

        # Test entity type filtering
        players = entity_registry.get_player_entities()
        enemies = entity_registry.get_enemies()
        bosses = entity_registry.get_bosses()
        elites = entity_registry.get_elites()

        Log.p(
            "Main",
            [
                f"Found {len(players)} player(s), {len(enemies)} enemies, {len(bosses)} boss(es), {len(elites)} elite(s)"
            ],
        )

        if len(players) == 0:
            Log.p("Main", ["ERROR: No player entities found"])
            return False

        Log.p("Main", ["✅ EntityRegistry validation successful"])

        # Test AbilityRegistry
        Log.p("Main", ["Testing AbilityRegistry..."])
        ability_registry = AbilityRegistry()
        ability_registry.load_from_directory(Path("data/abilities"))

        ability_count = ability_registry.get_item_count()
        Log.p("Main", [f"AbilityRegistry loaded {ability_count} abilities"])

        if ability_count == 0:
            Log.p("Main", ["ERROR: AbilityRegistry loaded no items"])
            return False

        # Verify some expected abilities exist
        expected_abilities = [
            "snap_shot",
            "aimed_shot",
            "patch_up",
            "take_cover",
        ]
        for ability in expected_abilities:
            if not ability_registry.get_item(ability):
                Log.p("Main", [f"ERROR: Missing expected ability: {ability}"])
                return False

        # Test detective ability filtering
        detective_abilities = ability_registry.get_abilities_for_entity("detective")
        Log.p("Main", [f"Found {len(detective_abilities)} abilities for detective"])

        if len(detective_abilities) == 0:
            Log.p("Main", ["ERROR: No detective abilities found"])
            return False

        # Test ability cost validation
        test_ability = ability_registry.get_item("snap_shot")
        if test_ability:
            can_afford = test_ability.cost.can_afford(
                5, 5, 100
            )  # 5 ammo, 5 mana, 100 health
            if not can_afford:
                Log.p("Main", ["ERROR: Cost validation failed for snap_shot"])
                return False

        Log.p("Main", ["✅ AbilityRegistry validation successful"])

        # Test SuffixRegistry
        Log.p("Main", ["Testing SuffixRegistry..."])
        suffix_registry = SuffixRegistry()
        suffix_registry.load_from_directory(Path("data/suffixes"))

        suffix_count = suffix_registry.get_item_count()
        Log.p("Main", [f"SuffixRegistry loaded {suffix_count} suffixes"])

        if suffix_count == 0:
            Log.p("Main", ["ERROR: SuffixRegistry loaded no items"])
            return False

        # Test suffix type filtering
        prefixes = suffix_registry.get_prefixes()
        suffixes = suffix_registry.get_suffixes()
        Log.p("Main", [f"Found {len(prefixes)} prefixes, {len(suffixes)} suffixes"])

        if len(prefixes) == 0:
            Log.p("Main", ["ERROR: No prefixes found"])
            return False

        # Test procedural generation
        test_stats = {"hp": 20, "attack": 8, "defense": 5, "speed": 10}
        variant = suffix_registry.generate_entity_variant(
            "imp", test_stats, force_generation=True
        )

        if variant:
            Log.p(
                "Main",
                [
                    f"Generated variant: {variant['name']} with {len(variant['applied_suffixes'])} suffix(es)"
                ],
            )
        else:
            Log.p("Main", ["ERROR: Failed to generate entity variant"])
            return False

        # Test suffix combination count
        combinations = suffix_registry.get_suffix_combinations_count()
        Log.p("Main", [f"Total possible combinations: {combinations}"])

        Log.p("Main", ["✅ SuffixRegistry validation successful"])

        Log.p("Main", ["✅ All registries loaded successfully"])
        return True

    except Exception as e:
        Log.p("Main", [f"ERROR: Registry test failed: {str(e)}"])
        return False


def main() -> NoReturn:
    """Main entry point for Broken Divinity."""
    Log.p("Main", ["Starting Broken Divinity ASCII Roguelike v0.0.9"])

    try:
        # Test registry systems
        if not test_registries():
            Log.p("Main", ["FATAL: Registry systems failed to initialize"])
            sys.exit(1)

        Log.p("Main", ["Game systems initialized successfully"])

        # Initialize Main UI Framework with new main menu
        Log.p("Main", ["Initializing Main UI Framework..."])
        ui = MainUI()
        ui.initialize()

        # Main menu is already set as the entry point in MainUI
        Log.p("Main", ["Main menu loaded as entry point"])

        # Set up sample status data
        status = StatusData(
            location="Detective Bureau",
            gold=250,
            time="14:30",
            day=1,
            hp=85,
            max_hp=100,
            mana=40,
            max_mana=50,
            ammo=18,
        )

        ui.update_status(status)

        Log.p("Main", ["UI Framework ready - launching main UI loop"])

        # Launch the UI main loop
        ui.run_main_loop()

        Log.p("Main", ["UI loop completed"])

    except KeyboardInterrupt:
        Log.p("Main", ["Game interrupted by user"])
    except Exception as e:
        Log.p("Main", ["Fatal error:", str(e)])
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

# EOF
