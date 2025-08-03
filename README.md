# Broken Divinity - ASCII Roguelike

A classic turn-based ASCII roguelike implementation of Broken Divinity, built with Python and tcod. Experience tactical combat in a procedurally generated world where only the detective has immunity from permadeath.

## 🎯 Core Features

- **Turn-Based Combat**: Strategic, speed-based initiative system
- **Procedural Dungeons**: Room-based encounters with varied challenges
- **Entity Variants**: Dynamic prefix/suffix modifiers for enemies, NPCs, and loot
- **Data-Driven Design**: JSON-based content with YAML/TOML configuration
- **Detective Immunity**: Unique permadeath mechanics
- **Unicode Display**: Rich terminal graphics with fallback compatibility

## 🔧 Tech Stack

- **python-tcod**: Rendering, field-of-view, pathfinding
- **asciimatics**: Modal UI widgets and menus
- **pytest**: Comprehensive testing framework
- **JSON**: Game data (entities, abilities, items)
- **YAML/TOML**: Configuration and settings

## 🏗️ Project Structure

```
broken_divinity_proto/
├── src/                    # Core game code
│   ├── game/              # Game logic (entities, combat, dungeons)
│   ├── ui/                # User interface (console, menus)
│   └── utils/             # Utilities (logging, loaders)
├── data/                  # Game content (JSON files)
│   ├── entities/          # Character definitions
│   ├── variants/          # Prefix/suffix modifiers
│   ├── abilities/         # Spell and skill definitions
│   └── items/             # Equipment and consumables
├── tests/                 # Test suite
├── config/                # Settings and configuration
├── Documentation/         # Project documentation
└── .vscode/              # VS Code workspace configuration
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
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
   pip install python-tcod asciimatics pytest pyyaml
   ```

4. Run tests:
   ```bash
   python -m pytest -v
   ```

5. Start the game:
   ```bash
   python -m src.main
   ```

## 🎮 Controls

- **Arrow Keys**: Movement
- **F**: Fight
- **D**: Defend  
- **I**: Inventory
- **A**: Abilities
- **ESC**: Back/Exit

## 🧪 Testing

The project follows Test-Driven Development with comprehensive coverage:

```bash
# Run all tests
python -m pytest -v

# Run specific test file
python -m pytest tests/test_entities.py -v

# Run with coverage
python -m pytest --cov=src tests/
```

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
