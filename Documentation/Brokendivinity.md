A sprawling ASCII settlement-builder, a procedural loot factory, and an investigation into the hardest whodunit imaginable—Broken Divinity weaves colony-sim depth with menu-driven exploration and turn-based duels inspired by SanctuaryRPG and Warsim.¹ The Detective roams a world where Heaven, Hell, and Earth have fused, growing a refuge cell-by-cell while suffix-driven enemies, weapons, and NPCs explode into billions of variants. Below is the consolidated, player-facing README (systems + lore) with every redundant “hop” reference removed and four starter abilities stored in DetectiveAbilities.json.
1. Game Pillars
1.1 Detective Narrative

Investigate Yahweh’s death in the vein of Disco Elysium’s razor-sharp questioning and branching revelations.
Financial Times
1.2 ASCII Settlement

A top-down map grows like a living blueprint—think Warsim’s kingdom screen, but every new farm, forge, or shrine swaps in richer glyph blocks.
Steam Store
Fires, celestial purges, and demon plagues can raze districts, echoing Dwarf Fortress’ “losing is FUN” ethos.
Polygon
1.3 Suffix System

    Enemies/NPCs : Base species + up to three suffixes (Imp of Blight, Militiaman of Zeal) draw from the Diablo-style affix table.
    Diablo Wiki
    Diablo Wiki

    Weapons/Relics : Parts × 1-6 suffixes mirror Borderlands’ billion-gun generator.
    Reddit

    Villagers : Personality suffixes (of Mercy, of Trade) change shop prices and morale. Path-of-Exile-like modifier depth ensures unique runs.
    Reddit

    Current generator already exceeds 4 trillion melee combinations.

1.4 Tactical Combat Snapshot

    Menu-based entry (“Enter the Fighting Pit”) triggers a dynamic ASCII grid sized to the room.

    Turn order: speed score + random tiebreak each round, a nod to classic JRPG initiatives.
    Steam Store

    F-D-I-A menu (Fight, Defend, Inventory, Ability).

    Morale, bleed, poison, and external hazards tick at round start (after every entity has acted).

2. Core Systems (tech-agnostic view)
2.1 Signal-Bus Architecture

All managers, registries, and UIs communicate via a central pub/sub bus—loose coupling for easy swaps.
2.2 Registries
Registry	Purpose	Hot-reload?
StateReg	Stun, Bleed, Poison logic	✔
BuffReg	Positive auras, stacking rules	✔
SuffixReg	Affix tables, rarity weights	✔
AbilityReg	Reads data/abilities/*.json, exposes by name	✔
EntityReg	Species, stat blocks, flee chance	✔

File-watcher service reloads JSON and emits “registry-updated” bus events.
2.3 Combat Timeline

    Round start – roll initiative; apply timed effects (bleed, poison).

    Entity turn – one action (move grid, ability, defend). Movement costs the action.

    Morale check – entities at low HP may attempt to flee (50 % base, bosses immune). Failure burns their action unless alone on the field.

    Turn end – after every entity acts, clock advances three in-world minutes; global hazards trigger.

2.4 Damage & Defense

damage_taken = max(0, attack – defense); no hard minimum. DoT effects ignore defense.
2.5 Ability & Initiative Modifiers

Speed can be buffed by haste spells or gear. Equipment and suffixes may grant +speed or –speed.
2.6 Experience & Level-Up

    Credit : killer gets full XP; surviving allies share a pooled bonus; heals or support actions award small XP ticks.

    Level-up : automatic—stat bumps + 1 ability point (choose from a curated list).

2.7 Research & Faction Diplomacy

    Three trees—Holy, Infernal, Secular—unlock buildings, suffix tiers, and edicts (inspired by Civilization’s “one-more-turn” pull).

    Goodwill drifts daily like RimWorld factions; speeches or hero actions can spike it.
    RimWorld Wiki

    Hero auras borrow the passive influence model seen in Age of Empires II expansions.
    ageofempires.fandom.com

3. Detective’s Starter Ability File

data/abilities/DetectiveAbilities.json

[
  {
    "name": "Snap Shot",
    "description": "Quick pistol shot before the enemy can react.",
    "damage_type": "Ballistic",
    "base_damage": 4,
    "ammo_cost": 1,
    "mana_cost": 0,
    "cooldown_rounds": 0,
    "tags": ["ranged", "quick"]
  },
  {
    "name": "Aimed Shot",
    "description": "Carefully line up a lethal shot for extra damage.",
    "damage_type": "Ballistic",
    "base_damage": 8,
    "ammo_cost": 1,
    "mana_cost": 1,
    "cooldown_rounds": 2,
    "tags": ["ranged", "focus", "crit_chance_up"]
  },
  {
    "name": "Patch Yourself Up",
    "description": "Field dressing to restore health over time.",
    "damage_type": "Heal",
    "heal_amount": 6,
    "ammo_cost": 0,
    "mana_cost": 2,
    "cooldown_rounds": 3,
    "tags": ["heal", "over_time"]
  },
  {
    "name": "Take Cover",
    "description": "Dive behind cover, raising defense for one round.",
    "damage_type": "Buff",
    "defense_bonus": 3,
    "ammo_cost": 0,
    "mana_cost": 0,
    "cooldown_rounds": 1,
    "tags": ["defensive", "buff"]
  }
]

All four abilities conform to the public schema read by AbilityReg and illustrate ammo, mana, and cooldown usage.
4. Outstanding Road-Map Items (later phases)

    Dynamic grid renderer – cones, circles, and line AoE templates.

    Game clock integration – tick three minutes per completed turn; long-cast abilities consume multiple ticks.

    Advanced flee AI – bosses immune, elites roll morale mod.

    Suffix rarity tiers – weighting by settlement research level.

    Hero recruitment UI – icons, faction tension tooltips.