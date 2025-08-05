# Broken Divinity - ASCII Detective Adventure

A menu-driven ASCII supernatural mystery game where Detective Morrison investigates divine murders in post-apocalyptic New Babylon. Built with Python 3.11+ using the "Close-to-Shore" development methodology for reliable, data-driven gameplay.

## 🎯 Core Features

- **Menu-Driven Exploration**: Navigate via numbered selections (1-9), no direct movement
- **Data-Driven Design**: All content in JSON files with automatic discovery systems
- **Detective Investigation**: Piece together clues to solve supernatural murders
- **Status Effect System**: Complex buff/debuff mechanics with duration tracking
- **Character Progression**: Skill development and equipment management
- **Tactical Combat**: Turn-based encounters with F/D/I/A controls
- **Rich ASCII Interface**: Professional UI with tcod rendering

## 🏗️ Enhanced Architecture

Built using the "Close-to-Shore" methodology with comprehensive testing:

```
broken_divinity_proto/
├── src/                    # Core game code
│   ├── game/              # Game logic (entities, state, locations)
│   ├── ui/                # User interface (menus, screens, layout)
│   ├── core/              # Core systems (registries, signals)
│   └── utils/             # Utilities (logging, helpers)
├── data/                  # Game content (JSON files)
│   ├── entities/          # Character and NPC definitions
│   ├── abilities/         # Detective skills and powers
│   ├── locations/         # Exploration areas and items
│   └── modifiers/         # Procedural generation data
├── tests/                 # Comprehensive test suite
│   ├── unit/              # Component isolation tests
│   ├── integration/       # System interaction tests
│   ├── smoke/             # End-to-end critical path tests
│   └── game_flow/         # Complete player journey tests
├── docs/                  # Documentation
│   └── playtests/         # Manual testing reports
└── schemas/               # JSON validation schemas
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- VS Code (recommended)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   make install
   # or manually:
   pip install -e .[dev]
   ```

4. Run the enhanced test suite:
   ```bash
   make test-all
   ```

5. Validate the installation:
   ```bash
   make validate-boot
   ```

6. Start the game:
   ```bash
   make run
   # or
   python -m src.main
   ```

## 🎮 Controls

- **Numbered Keys (1-9)**: Menu navigation and selection
- **0**: Next page (when available)
- **F**: Fight
- **D**: Defend  
- **I**: Inventory/Inspect
- **A**: Abilities
- **ESC**: Back/Exit

## 🧪 Enhanced Testing Strategy

The project uses a comprehensive multi-layered testing approach:

### Test Categories

```bash
# Individual test categories
make test-unit          # Component isolation tests
make test-integration   # System interaction tests  
make test-smoke         # End-to-end critical paths
make test-game-flow     # Complete player journeys

# Validation commands
make validate-schemas   # JSON schema validation
make validate-boot      # Game startup test
make validate-data      # All data file checks

# Workflow commands
make test-pre-commit    # Full automated suite
make test-hop-complete  # Everything + manual validation
make test-debug         # Run with verbose output
```

### VS Code Integration

Use `Ctrl+Shift+P` and search for:
- "Tasks: Test: All" - Run complete test suite
- "Tasks: Test: Unit" - Run unit tests only
- "Tasks: Validate: Boot Test" - Quick game validation
- "Tasks: Run Game" - Start the game

### Player-Driven Testing

Each development hop includes mandatory manual testing:
1. Feature functionality validation
2. User experience assessment  
3. Story progression verification
4. Performance and stability check

Results are documented in `docs/playtests/hop_X_playtest.md`

## 📖 Documentation

- [Roadmap](Documentation/ROADMAP.md) - Feature development progression
- [Personal Style Guide](Personal Style / Preferences.md) - Code conventions
- [Close-to-Shore Methodology](Personal Style /Close‑to‑Shore Coding.md) - Development process

## 🎨 Design Philosophy

**Data-Driven First**: Content lives in `.json` resources. Systems discover content by scanning folders, avoiding hard-coded content paths.

**Verbose Logging**: Every subsystem uses bracketed tags (`[EntityReg]`, `[CombatMgr]`) for clear tracing.

**Always Green**: Every change ends with passing tests and a bootable scene following the "Close-to-Shore" methodology.

**Auto-Populating UI**: Interface elements discover and display content automatically without manual configuration.

## 🤝 Contributing

1. Follow the Close-to-Shore methodology (see documentation)
2. Each feature requires tests before implementation
3. Use conventional commit messages: `feat(combat): add damage calculation`
4. Ensure all tests pass before committing
5. Add verbose logging with appropriate system tags

## 📄 License

This project is open source. See the LICENSE file for details.

## 🔗 Links

- [Python-TCOD Documentation](https://python-tcod.readthedocs.io/)
- [Asciimatics Documentation](https://asciimatics.readthedocs.io/)
- [Roguelike Development Community](https://www.reddit.com/r/roguelikedev/)

---

*Built with ❤️ following the Close-to-Shore development methodology*
