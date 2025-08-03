# Broken Divinity ASCII Roguelike - Project Plan

## Project Summary

Transform Broken Divinity from Godot to a classic ASCII roguelike using Python + tcod, maintaining the core data-driven philosophy while creating a terminal-based tactical combat experience.

**Core Goals:**
- Single-player, turn-based, permadeath (except detective)
- Procedural dungeons with room-based encounters
- Prefix/suffix entity variants (enemies, NPCs, loot)
- Data-driven registries (JSON + YAML/TOML for config)
- 100×35 console with unicode glyphs
- Full test coverage with pytest + CI

**Tech Stack:**
- `python-tcod` for rendering, FOV, pathfinding
- `asciimatics` for modal UI widgets
- `pytest` for testing
- JSON for game data, YAML/TOML for settings
- VS Code with Python tasks

---

## Phase 1: Foundation

Following "Close-to-Shore Coding" methodology - each hop must end with green tests and bootable prototype.

**Note**: See `Documentation/ROADMAP.md` for the complete feature tracking roadmap.

### Core Infrastructure (Hops 1-7)

#### Hop 1: Project Scaffold
**Outcome:** VS Code workspace with dependencies and basic project structure
- Create `pyproject.toml` with tcod, asciimatics, pytest
- Set up folder structure (`src/`, `data/`, `tests/`)
- Add VS Code `tasks.json` for test runner
- Basic `.gitignore` and `README.md`
- **DoD:** `pytest` runs (empty), dependencies install

#### Hop 2: Minimal tcod Window
**Outcome:** Black console window that responds to ESC key
- Basic tcod window initialization (100×35)
- Event loop stub that exits on ESC
- Font loading with unicode glyph support
- **DoD:** Window opens, displays, closes cleanly

#### Hop 3: Screen Layout Framework
**Outcome:** Console divided into 4 regions with borders
- Top status bar (world info)
- Center enemy/map pane 
- Side combat log panel
- Bottom action bar
- **DoD:** All regions visible with placeholder text

#### Hop 4: Basic Entity Data Model
**Outcome:** JSON entity loader with tests
- `Entity` class with stats, abilities, glyph
- JSON loader for `data/entities/`
- Simple registry pattern (dict lookup)
- **DoD:** Load imp.json, access via registry, tests green

#### Hop 5: Prefix/Suffix Variant System
**Outcome:** Entity variants spawn with modifiers applied
- Variant modifier loader (`data/variants/`)
- Merge algorithm (add/mul operations on stats)
- Spawn function that applies random prefix/suffix
- **DoD:** "Brave Imp" has +4 courage, tests verify merge

#### Hop 6: Action State Machine
**Outcome:** Root action menu responds to F/D/I/A keys
- GameState base class
- ActionMenuState with keyboard input
- State transitions (main → submenu)
- **DoD:** Press F shows "Fight selected", ESC returns to main

#### Hop 7: Combat Log System
**Outcome:** Scrollable message history
- CombatLog class with circular buffer
- Render messages in log panel
- Auto-scroll to bottom, manual scroll with arrows
- **DoD:** Messages appear, old ones scroll off, navigation works

### World Generation (Hops 8-14)

#### Hop 8: Simple Room Generator
**Outcome:** Single rectangular room with walls/floor
- Room class with bounds, wall/floor tiles
- Basic tile enum (Wall, Floor, Door)
- Render room in center pane with ascii chars
- **DoD:** See room outline, floor interior, door marked

#### Hop 9: Multi-Room Dungeon
**Outcome:** 3-5 connected rooms with corridors
- Dungeon class managing multiple rooms
- Corridor generation between rooms
- Collision detection (no overlapping rooms)
- **DoD:** Navigate connected rooms, all accessible

#### Hop 10: Player Movement
**Outcome:** @ character moves through dungeon with arrow keys
- Player entity with position
- Movement validation (wall collision)
- Camera following player
- **DoD:** Smooth movement, can't walk through walls

#### Hop 11: Enemy Placement
**Outcome:** Random enemies spawn in rooms
- Enemy spawning system
- Room occupation tracking
- Basic AI (stationary for now)
- **DoD:** See enemies in rooms, different glyphs per type

#### Hop 12: Field of View
**Outcome:** Only visible areas are rendered
- tcod FOV algorithm integration
- Light radius around player
- Explored/visible/hidden tile states
- **DoD:** Realistic vision, fog of war works

#### Hop 13: Room Event System
**Outcome:** Entering rooms triggers events
- Room event types (combat, treasure, empty)
- Event probability tables
- Trigger system on room entry
- **DoD:** "You enter a dusty chamber..." messages

#### Hop 14: Turn-Based Time
**Outcome:** Player and enemies take turns based on speed
- Turn scheduler with priority queue
- Speed-based turn order
- Turn counter and time tracking
- **DoD:** Fast enemies move more often, time advances properly

### Combat System (Hops 15-21)

#### Hop 15: Basic Combat Initiation
**Outcome:** Moving into enemy starts combat mode
- Combat state detection
- Initiative order calculation
- Combat UI mode (enemy stats visible)
- **DoD:** Combat starts, shows enemy HP/stats

#### Hop 16: Attack Resolution
**Outcome:** Fight command deals damage to target
- Damage calculation (atk range vs defense)
- HP reduction and death detection
- Combat log messages with details
- **DoD:** Attack deals damage, enemy dies when HP=0

#### Hop 17: Ability System Core
**Outcome:** Abilities loaded from JSON with effects
- Ability JSON format and loader
- Effect types (damage, buff, movement)
- Ability cost system (MP/cooldowns)
- **DoD:** Fire Bolt ability works, costs MP, deals damage

#### Hop 18: Buff/Debuff Framework
**Outcome:** Temporary effects that modify stats
- Buff class with duration, magnitude
- Stat modification system
- Turn-based expiration
- **DoD:** Shield buff gives +2 def for 3 turns

#### Hop 19: Enemy AI Basic
**Outcome:** Enemies use abilities and move toward player
- Basic AI decision tree
- Pathfinding to player
- Ability usage based on range/cost
- **DoD:** Enemies move intelligently, use abilities

#### Hop 20: Death and Respawn
**Outcome:** Player death handling (except detective immunity)
- Death detection and game over state
- Detective permadeath immunity
- Restart/continue flow
- **DoD:** Non-detective dies → game over, detective continues

#### Hop 21: Victory Conditions
**Outcome:** Clearing room/floor advances progress
- Room clear detection
- Floor completion rewards
- Progress tracking
- **DoD:** Clear all enemies → "Floor complete" message

### Polish & Integration (Hops 22-28)

#### Hop 22: Inventory System
**Outcome:** Items can be collected and used
- Item JSON format and variants
- Inventory UI (asciimatics modal)
- Use/equip/drop actions
- **DoD:** Pick up sword, equip it, stats change

#### Hop 23: Ability Menu
**Outcome:** Ability selection submenu
- Asciimatics ability selection frame
- Ability descriptions and costs
- Target selection for ranged abilities
- **DoD:** Select Fire Bolt, choose target, cast successfully

#### Hop 24: Save/Load Framework
**Outcome:** Game state persists between sessions
- JSON serialization of game state
- Load saved game on startup
- Multiple save slots
- **DoD:** Save game, restart, load continues from same state

#### Hop 25: Settings System
**Outcome:** YAML/TOML configuration for user preferences
- Key binding customization
- Display options (colors, font size)
- Audio cues (optional)
- **DoD:** Change keybinds in settings.yaml, game respects them

#### Hop 26: Advanced Variants
**Outcome:** Complex modifier combinations
- Multiple prefix/suffix stacking
- Rare/legendary tier modifiers
- Alignment restrictions (demon/divine/neutral)
- **DoD:** "Vile Brave Imp" has both modifiers, no divine abilities

#### Hop 27: Polish Pass
**Outcome:** UI feedback and visual improvements
- Animation hints (fade/highlight)
- Better unicode glyph choices
- Color coding for different entity types
- **DoD:** Game feels responsive, visually clear

#### Hop 28: Full Integration Test
**Outcome:** Complete playthrough works end-to-end
- Automated integration test suite
- Manual playtest from start to floor completion
- Performance verification
- **DoD:** Full game loop works, no crashes, tests green

---

## Definition of Done (DoD) Checklist

Each hop is complete when ALL of the following are true:

1. **✅ Tests Green:** pytest runs pass for all affected components
2. **✅ Bootable:** Main game starts and reaches the new functionality
3. **✅ Logged:** Clear `[SystemTag]` messages show the feature working
4. **✅ Data-Driven:** No hard-coded content, loads from JSON/YAML
5. **✅ Committed:** Clean commit with conventional message format
6. **✅ TODOs:** Future improvements marked inline with tags

## Development Environment Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Linux

# Install dependencies
pip install python-tcod asciimatics pytest pyyaml

# VS Code tasks (add to .vscode/tasks.json)
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "python",
      "args": ["-m", "pytest", "-v"],
      "group": "test"
    },
    {
      "label": "Run Game",
      "type": "shell", 
      "command": "python",
      "args": ["-m", "src.main"],
      "group": "build"
    }
  ]
}
```

## File Structure Template

```
broken_divinity_proto/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── game/
│   │   ├── __init__.py
│   │   ├── entities.py      # Entity, registry classes
│   │   ├── combat.py        # Combat system
│   │   ├── dungeon.py       # Map generation
│   │   └── states.py        # Game state machine
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── console.py       # tcod rendering
│   │   └── menus.py         # asciimatics widgets
│   └── utils/
│       ├── __init__.py
│       ├── logging.py       # Log helper
│       └── loaders.py       # JSON/YAML loaders
├── data/
│   ├── entities/
│   │   ├── imp.json
│   │   └── detective.json
│   ├── variants/
│   │   ├── prefixes.json
│   │   └── suffixes.json
│   ├── abilities/
│   │   └── basic_attacks.json
│   └── items/
│       └── weapons.json
├── tests/
│   ├── __init__.py
│   ├── test_entities.py
│   ├── test_combat.py
│   └── test_variants.py
├── config/
│   └── settings.yaml
├── pyproject.toml
└── README.md
```

---

## Risk Mitigation

**Major Risks:**
1. **Unicode rendering issues** → Test font compatibility early (Hop 2)
2. **Performance with large dungeons** → Profile during Week 2
3. **Complex state management** → Keep states simple, test transitions
4. **tcod/asciimatics integration** → Prototype modal overlap in Week 1

**Mitigation Strategy:**
- Each hop focuses on a single, complete feature
- Always have a working version to fall back to
- Test on multiple terminals/systems early
- Keep scope minimal, defer nice-to-haves

---

## Quick Start

Ready to begin? See the [ROADMAP](Documentation/ROADMAP.md) for progress tracking, then start with **Hop 1: Project Scaffold**.

---

*This plan follows Close-to-Shore methodology: short hops, always green tests, bootable at every step. Each hop delivers a complete, working feature.*
