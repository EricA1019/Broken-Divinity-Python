Below is the **single, canonical "Close-to-Shore Bible"** for *Broken Divinity – Python / ASCII edition*.

This is a **framework for LLM-driven complex project development**, designed specifically for AI agents collaborating with human developers to build sophisticated, maintainable software systems.

---

# Broken Divinity — Close-to-Shore Bible

*Short hops, loud logs, data-driven JSON, always-green pytest*  
**LLM Agent Development Framework v2.0**e **single, canonical “Close-to-Shore Bible”** for *Broken Divinity – Python / ASCII edition*.
It merges everything discussed so far, re-orders the sections for a smoother read, and folds in:

* your **preferred file header** (Section 11)
* the **version-number flow + GitHub rule** (Section 15)

---

# Broken Divinity — Close-to-Shore Bible

*Short hops, loud logs, data-driven JSON, always-green pytest*

---

## 0) Core Principles (“Stay Close to Shore”)

|                       | Rule                                                               | Rationale                      |
| --------------------- | ------------------------------------------------------------------ | ------------------------------ |
| **Short hops**        | Each hop is a tiny, runnable vertical slice.                       | Always know where land is.     |
| **Always green**      | End every hop with green tests **and** a bootable ASCII game.      | No lingering debt.             |
| **Data-driven first** | Content lives in JSON/YAML; systems **discover** via folder scans. | Easy modding, no brittle glue. |
| **Avoid hard-coding** | Prefer tables & registries over `if/elif` ladders.                 | Fewer bugs, easier refactor.   |
| **Auto-populated UI** | Containers read data and spawn controls automatically.             | No hand-placed buttons.        |
| **Traceable logs**    | Verbose, tagged logs; never silently fail.                         | Debug in seconds, not hours.   |

**Definition of Done (per hop)**

1. `pytest` green (unit + integration + smoke + game_flow)
2. JSON schema validation passes for all data files
3. `Game.run()` boots without error and completes boot test
4. Player-driven testing completed with documented results
5. Logs clean (no warnings/errors unless expected)
6. New data discovered, not hard-wired
7. Commit + tag (see §15)
8. `TODO(tag):` notes for deferred work
9. Documentation updated (README.md, ROADMAP.md)

---

## 1) Project Layout

```
broken_divinity/
│
├─ src/                     # importable package
│   ├─ engine/              # loop, renderer, input, event bus
│   ├─ systems/             # registries + managers
│   ├─ components/          # lightweight ECS bits
│   └─ ui/                  # ASCII panels
│
├─ data/                    # JSON / YAML assets
│   ├─ abilities/
│   ├─ buffs/
│   ├─ statuses/
│   └─ entities/
│
├─ tests/                   # permanent pytest suites
│   ├─ unit/
│   ├─ integration/
│   └─ smoke/
│
└─ scratch_tests/           # temporary debug tests (git-ignored)
```

---

## 2) Dependencies

| Purpose         | Library                                |
| --------------- | -------------------------------------- |
| ASCII rendering | **rich** (fallback to `curses`)        |
| Input           | `blessed` or `readchar`                |
| Data parsing    | `json` + `pyyaml`                      |
| Tests           | `pytest`, `pytest-subtests`            |
| Logging         | `logging` + `rich.logging.RichHandler` |
| CLI helpers     | `typer` (optional)                     |

---

## 3) Logging & Observability

```python
# src/engine/logging_setup.py
import logging
from rich.logging import RichHandler

def configure(verbose: bool = True) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(markup=True)]
    )
```

* **Tag prefix** = logger name (`log = logging.getLogger("TurnMgr")`).
* `log.debug|info|warning|error(…)` as severity ladder.
* Never silently fail.

---

## 4) Data-Driven Conventions

* **Assets:** JSON/YAML; keys match `name`.
* **Registries:** scan `data/**` once, cache by `name`.
* **Tables over branches:** map types → effects in dicts, not control flow.

---

## 5) Architecture (Engine Loop Snapshot)

```python
class Game:
    def __init__(self):
        configure(verbose=True)
        self.renderer   = ASCIIRenderer()
        self.turn_mgr   = TurnManager(event_bus=EventBus.global_bus())

    def run(self) -> None:
        while not self.turn_mgr.game_over:
            self.turn_mgr.process_turn()
            self.renderer.render(self.turn_mgr)
            cmd = self.renderer.get_input()
            self.turn_mgr.handle_input(cmd)
```

* Managers live in `src/systems`.
* Global events via `EventBus`.
* IDs via `id(entity)` if needed.

---

## 6) UI Principles (ASCII Panels)

| Panel             | Public API               | Data Source                     |
| ----------------- | ------------------------ | ------------------------------- |
| **InitiativeBar** | `populate(units)`        | `TurnManager.order`             |
| **ActionBar**     | `show(actor)`            | `actor.ability_container.all()` |
| **EntityPanel**   | `bind(entity)`           | Signals: `hp_changed`, `died`   |
| **CombatLog**     | Subscribes to `EventBus` | Emits formatted lines           |

Zero hard-wired paths; icons loaded via registry meta.

---

## 7) Game Rules (Initial)

* **Damage types:** `Physical`, `Infernal`, `Holy` (mod table).
* **Rounds vs Turns:** buffs expire at **round end**.
* **Stacks:** magnitude + duration stack (exceptions noted in resource).

---

## 8) Comprehensive Testing Strategy (Multi-Layered Validation)

This testing framework ensures stability through automated testing and human validation at every hop.

### Test Architecture Overview

```
tests/
├── unit/                   # Component isolation tests
├── integration/            # System interaction tests  
├── smoke/                  # End-to-end critical path tests
├── game_flow/              # Player journey validation
└── scratch_tests/          # Temporary debug tests (git-ignored)
```

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Validate individual components in isolation
**Scope**: Single classes, functions, or modules
**Coverage**: All registries, managers, and UI components

**Examples**:
- `test_ability_registry.py` - Registry loading and lookup
- `test_state_machine.py` - Game state transitions  
- `test_entity_manager.py` - Entity creation and management
- `test_menu_screen.py` - UI component behavior

**Standards**:
- Mock external dependencies
- Test public API only (no private member access)
- Fast execution (<100ms per test)
- Deterministic results

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Validate system-to-system interactions
**Scope**: Multiple components working together
**Coverage**: Cross-system workflows and data flow

**Examples**:
- `test_game_flow.py` - Menu navigation and screen transitions
- `test_registry_integration.py` - Multiple registries working together
- `test_ui_data_binding.py` - UI components reading from data systems
- `test_signal_propagation.py` - Event bus message flow

**Key Test**: `test_continue_game_flow()` validates main menu → apartment screen transition

**Standards**:
- Test realistic component interactions
- Verify data flows between systems
- Test error handling and edge cases
- Medium execution time (100ms-1s per test)

### 3. Smoke Tests (`tests/smoke/`)

**Purpose**: Validate critical game paths work end-to-end
**Scope**: Complete user workflows from start to finish
**Coverage**: Core game loop and major features

**Examples**:
- `test_boot_sequence.py` - Game starts without errors
- `test_character_creation.py` - Full character creation flow
- `test_apartment_exploration.py` - Complete location exploration
- `test_menu_navigation.py` - All menu transitions work

**Standards**:
- Test real user scenarios
- No mocking of core systems
- Test with actual data files
- Slower execution acceptable (1-5s per test)

### 4. Game Flow Tests (`tests/game_flow/`)

**Purpose**: Validate complete player journeys and story progression
**Scope**: Multi-screen workflows and narrative coherence
**Coverage**: Player experience from tutorial to endgame

**Examples**:
- `test_new_player_onboarding.py` - Complete new game setup
- `test_investigation_workflow.py` - Detective work progression
- `test_location_discovery.py` - Exploration and world building
- `test_narrative_progression.py` - Story beats and character development

**Standards**:
- Test with production-like data
- Validate UI feedback and messaging
- Test error recovery scenarios
- Include timing and performance validation

### 5. JSON Schema Validation

**Purpose**: Prevent data corruption and ensure content consistency
**Implementation**: Automated validation before development begins

**Schema Files** (`schemas/`):
```
schemas/
├── abilities_schema.json       # Detective abilities structure
├── locations_schema.json       # Location and exploration data
├── characters_schema.json      # Character definitions
├── status_effects_schema.json  # Buffs and debuffs
└── items_schema.json          # Equipment and inventory
```

**Validation Commands**:
```bash
# Validate all data files
python -m tests.validate_schemas

# Validate specific data type
python -m tests.validate_schemas --type locations
```

### 6. Player-Driven Testing (Manual Validation)

**Purpose**: Ensure actual playability and fun factor
**Frequency**: Every hop completion
**Scope**: New features and affected systems

#### Player Test Protocol

**Phase A: Feature Validation**
1. **Access Test** - Can player reach new feature?
2. **Functionality Test** - Does feature work as designed?
3. **Integration Test** - How does it interact with existing systems?
4. **Feedback Test** - Are player actions clearly communicated?

**Phase B: Experience Validation**  
1. **Intuitive Controls** - Are interactions obvious?
2. **Clear Feedback** - Does player understand what happened?
3. **Narrative Coherence** - Does new content fit the story?
4. **Fun Factor** - Does feature enhance gameplay?

**Phase C: Edge Case Testing**
1. **Error Handling** - What happens with invalid input?
2. **Boundary Conditions** - Test limits and extremes
3. **Recovery Scenarios** - Can player recover from mistakes?
4. **Performance** - Any noticeable slowdowns or glitches?

#### Player Test Documentation

Create `docs/playtests/hop_X_playtest.md` for each test session:

```markdown
# Hop X Playtest Report

## Feature Tested: [Feature Name]
## Tester: [Name]
## Date: [Date]

### Functionality Check
- [ ] Feature accessible from expected location
- [ ] Core functionality works as designed  
- [ ] Integration with existing systems
- [ ] Error handling appropriate

### User Experience Check
- [ ] Controls intuitive
- [ ] Feedback clear and helpful
- [ ] Fits narrative context
- [ ] Enhances overall experience

### Issues Found
[List any bugs, confusing interactions, or improvement suggestions]

### Overall Assessment
[Pass/Fail with explanation]
```

### Testing Workflow Integration

#### Pre-Development (Step 1)
```bash
# Ensure clean starting state
python -m pytest tests/unit tests/integration tests/smoke -v
python -m tests.validate_schemas
python -m src.main --quick-boot-test
```

#### During Development (Step 3)
```bash
# Fast feedback loop (every 15-30 minutes)
python -m pytest tests/unit/test_[current_component].py -v
python -m pytest tests/integration/test_[current_feature].py -v

# Continuous JSON validation
python -m tests.validate_schemas --watch
```

#### Pre-Commit (Step 4)
```bash
# Full automated test suite
python -m pytest tests/ -v --tb=short

# JSON schema validation
python -m tests.validate_schemas

# Boot test
python -m src.main --boot-test
```

#### Hop Completion (Step 5)
```bash
# Full test suite + player validation
python -m pytest tests/ -v
python -m tests.validate_schemas
python -m src.main --full-boot-test

# Manual player test session
[Follow Player Test Protocol]
[Document results in docs/playtests/]
```

### Test Maintenance Guidelines

**Test Hygiene**:
- Remove obsolete tests when refactoring
- Update tests when changing APIs
- Keep test data minimal and focused
- Use fixtures for common setup

**Performance**:
- Unit tests: <100ms each
- Integration tests: <1s each  
- Smoke tests: <5s each
- Full suite: <30s total

**Reliability**:
- No flaky tests allowed
- Deterministic test data
- Proper cleanup after each test
- Clear failure messages

### CLI Testing Commands

```bash
# Individual test categories
make test-unit          # Fast component tests
make test-integration   # System interaction tests  
make test-smoke         # End-to-end critical paths
make test-game-flow     # Complete player journeys

# Validation commands
make validate-schemas   # JSON schema validation
make validate-boot      # Game startup test
make validate-data      # All data file checks

# Combined workflows
make test-pre-commit    # Full automated suite
make test-hop-complete  # Everything + manual validation
make test-debug         # Run with verbose output
```

---

## 9) CLI & Tasks

**Makefile**

```make
# Testing commands
test-unit:         ; python -m pytest tests/unit -v
test-integration:  ; python -m pytest tests/integration -v  
test-smoke:        ; python -m pytest tests/smoke -v
test-game-flow:    ; python -m pytest tests/game_flow -v
test-all:          ; python -m pytest tests/ -v
test-scratch:      ; python -m pytest scratch_tests -q

# Validation commands
validate-schemas:  ; python -m tests.validate_schemas
validate-boot:     ; python -m src.main --boot-test
validate-data:     ; python -m tests.validate_schemas && python -m src.main --boot-test

# Workflow commands
test-pre-commit:   ; make test-all && make validate-data
test-hop-complete: ; make test-pre-commit && echo "Run manual player test"
test-debug:        ; python -m pytest tests/ -v -s --tb=long

# Game commands
run:               ; python -m src.main
run-debug:         ; python -m src.main --debug --verbose
```

VS Code `tasks.json` mirrors these commands for one-key execution.

---

## 10) Code-Style Quick List

* **Black** + **PEP 8**.
* Guard clauses; ≤ 40 lines/function.
* Explicit `dataclass`es for data carriers.
* Severity: `assert` → `log.warning` → `log.error`.
* End every file with `#EOF`.

---

## 11) Preferred File Header

```python
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Ability Registry                                                            ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Discovers JSON ability definitions and serves them by name ║
║  Last-Updated  : 2025-08-03                                                 ║
║  Version       : v0.11.19                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
# imports…
#EOF
```

* 80-char box, symmetrical.
* Lives *inside* the top docstring.
* Update **Last-Updated** and **Version** each hop.

---

## 12) ASCII Artistry

* Icons in `icons/*.txt` (multi-line).
* Render via Rich panels; strip ANSI on fallback.
* Example `imp.txt`:

```
/\_/\
(ಠ_ಠ)
/ >🔥
```

---

## 13) Prompting LLMs

```
I'm building a terminal ASCII roguelike in Python 3.11.

Constraints:
- Data-driven JSON in data/*
- Registries discover content recursively
- Rich renderer, curses fallback
- Pytest tests first (test_*.py), no private pokes
- Provide a bootstrap script that writes files, skipping existing
- Verbose logging via logging.getLogger("[Tag]")
```

Checklist: deterministic tests, recursive scans, tagged logs, etc.

---

## 14) Enhanced Close-to-Shore Workflow (LLM Agent Framework)

### Framework Philosophy
This workflow is designed for **LLM agents working with human developers** on complex software projects. It emphasizes:
- **Predictable progress** through small, verifiable increments
- **Clear validation gates** at each step to prevent compound errors
- **Human feedback integration** at critical decision points
- **Maintainable quality** through automated validation

### Terminology Hierarchy
- **Steps** make up a **Hop** (PATCH version bump)
- **Hops** make up a **Phase** (MINOR version bump)  
- **Phases** make up an **Epoch** (MAJOR version bump)

### Standard Hop Workflow (6 Steps)

Each hop follows this **mandatory sequence**:

#### Step 1: Hop Planning & Setup
1. **Read ROADMAP.md** - Understand current hop requirements
2. **Run full test suite** - Ensure starting from green state (`make test-pre-commit`)
3. **Validate JSON schemas** - Ensure all data files conform (`make validate-schemas`)
4. **Boot test** - Verify game starts cleanly (`make validate-boot`)
5. **Configure environment** - Set up venv if needed
6. **Ask clarifying questions** - Use numbered format when unclear

#### Step 2: JSON Schema Validation & Templates
1. **Create/update schemas** - Schema validation for any new data types
2. **Validate existing JSON files** - Run schema validation before development
3. **Create data templates** - For any new data structures needed
4. **Fix validation errors** - Ensure all JSON conforms before coding begins
5. **Document schema changes** - Update schema documentation

#### Step 3: Test-First Implementation
1. **Write failing unit tests** - Cover all new components and functions
2. **Write failing integration tests** - Cover system interactions
3. **Write failing game flow tests** - Cover complete user workflows
4. **Implement minimal code** - Make tests pass incrementally
5. **Run tests frequently** - Keep feedback loop tight (every 15-30 minutes)
6. **Fix issues immediately** - Never continue with red tests

#### Step 4: Integration & System Validation
1. **Full unit test suite** - All component tests pass
2. **Full integration test suite** - All system interaction tests pass
3. **Smoke tests** - All critical path tests pass
4. **Game flow tests** - All user journey tests pass
5. **JSON validation suite** - All data files pass schema validation
6. **Boot game manually** - Verify `python -m src.main` works and shows new features
7. **Check error logs** - No unexpected warnings/errors

#### Step 5: Player Experience Testing (Manual Human Process)
1. **Human gameplay test** - Developer/tester plays through new features
2. **Follow Player Test Protocol** - Complete Phase A, B, and C validation
3. **Document player experience** - Create playtest report in `docs/playtests/`
4. **Note confusing or broken interactions** - Record UX issues
5. **Iterate on UX issues** - Fix gameplay flow problems
6. **Verify story progression** - New content fits narrative context
7. **Performance check** - No significant slowdowns or glitches

#### Step 6: Documentation & Commit
1. **Update README.md** - Reflect new features and current state
2. **Update ROADMAP.md** - Mark hop complete, set next target
3. **Update schema documentation** - Document any new JSON schemas added
4. **Write clear commit message** - Summarize what was accomplished
5. **Run final test suite** - One last verification everything works
6. **Tag version** - Follow semver (v0.phase.hop)
7. **Push to repository** - Share progress (mandatory for phase tags)

### JSON Validation System

**Purpose**: Prevent data file errors through automated schema validation

#### Schema Structure
- **Location**: `schemas/` directory
- **Format**: JSON Schema Draft 7
- **Naming**: `{data_type}_schema.json` (e.g., `abilities_schema.json`)

#### Required Schemas
1. **abilities_schema.json** - All ability JSON files
2. **status_effects_schema.json** - Status effect definitions
3. **locations_schema.json** - Location and item data
4. **characters_schema.json** - Character definitions
5. **items_schema.json** - Game items and equipment

#### Validation Process
1. **Pre-development** - Run validation before Step 3
2. **Automated** - Script validates all JSON files
3. **Blocking** - Development stops until validation passes
4. **Templates** - Provide example JSON for new data types

### Player Experience Requirements

**Mandatory for hop completion**: Human must actually play the game

#### Testing Scope
- **New features** - Every new system must be manually tested
- **Integration points** - How new features connect to existing systems
- **Story flow** - Narrative coherence and progression
- **UI/UX** - Intuitive controls and clear feedback

#### Success Criteria
- **Playable** - Player can access and use new features
- **Logical** - Actions make sense in context
- **Smooth** - No jarring transitions or broken flows
- **Fun** - Features enhance rather than detract from experience

### LLM Agent Collaboration Patterns

#### Communication Guidelines
1. **Ask before major changes** - Confirm direction when uncertain
2. **Report progress frequently** - Keep human informed of status
3. **Request clarification** - Use numbered questions for complex topics
4. **Document decisions** - Explain reasoning for technical choices

#### Error Recovery Protocol
1. **Stop at first failure** - Don't compound problems
2. **Analyze error systematically** - Use debugging tools
3. **Ask for help** - When stuck, explain what was tried
4. **Learn from mistakes** - Update process to prevent recurrence

### Version Management

#### Hop Versions (PATCH)
- **Format**: v0.0.X
- **Criteria**: Single feature complete with tests and player validation
- **Commit**: "Complete Hop X: [feature description]"

#### Phase Versions (MINOR)  
- **Format**: v0.X.0
- **Criteria**: Major system complete (e.g., entire combat system)
- **Milestone**: Significant gameplay capability added

#### Epoch Versions (MAJOR)
- **Format**: vX.0.0
- **Criteria**: Core game loop or architecture change
- **Scope**: Fundamental shifts in how the game works

### Workflow Quality Gates

**Before Starting Any Hop:**
- [ ] All existing tests passing (130+ unit, integration, smoke, game_flow)
- [ ] All JSON files pass schema validation
- [ ] Game boots successfully and completes boot test
- [ ] Clear understanding of hop scope
- [ ] Previous hop's player testing documented
- [ ] No unplanned technical debt

**During Hop Development:**
- [ ] JSON validation passing continuously
- [ ] Unit tests written before implementation
- [ ] Integration tests cover system interactions
- [ ] Regular test runs (every 15-30 minutes)
- [ ] Immediate issue resolution
- [ ] Clear progress tracking
- [ ] Incremental commits with green tests

**Before Completing Any Hop:**
- [ ] All unit tests pass (no red tests)
- [ ] All integration tests pass
- [ ] All smoke tests pass  
- [ ] All game flow tests pass
- [ ] All JSON validation passes
- [ ] Game boots cleanly and shows new features
- [ ] Player can access and experience new feature
- [ ] Player testing completed and documented
- [ ] Documentation updated (README.md, ROADMAP.md)
- [ ] Code follows style guide
- [ ] Performance acceptable (no significant slowdowns)

| Term             | Meaning                                        |
| ---------------- | ---------------------------------------------- |
| **Hop**          | One merge-ready vertical slice (`PATCH` bump). |
| **Phase**        | A cohesive feature block (`MINOR` bump).       |
| **Epoch**        | Breaking redesign (`MAJOR` bump).              |
| **Panel**        | Rectangular ASCII region.                      |
| **Scratch test** | Disposable debug file in `scratch_tests/`.     |

---

## 15) Version-Number Flow & GitHub Policy

| SemVer field | Represents      | Starts at       | Example    | Remote push?                              |
| ------------ | --------------- | --------------- | ---------- | ----------------------------------------- |
| **MAJOR**    | Epoch / rewrite | `0` → `1` later | `v1.00.00` | Yes                                       |
| **MINOR**    | **Phase**       | `0`             | `v0.11.00` | **Must** push at every phase close        |
| **PATCH**    | **Hop**         | `1`             | `v0.11.19` | Push optional (push if others/CI need it) |

> Hop 19 inside Phase 11 ⇒ **`v0.11.19`**

### Tag Recipes

```bash
# ----- Hop (PATCH) -----
git commit -m "feat(ui): initiative bar renders"
git tag -a v0.11.19 -m "Hop 19: initiative bar"
git push --tags origin main        # optional

# ----- Phase close (MINOR) -----
git commit -m "chore(phase): close phase 12 – action bar complete"
git tag -a v0.12.00 -m "Phase 12 complete: action bar"
git push --tags origin main        # **mandatory**
```

**Pre-tag checklist**

1. `pytest` green.
2. `Game.run --quick` boots.
3. Update headers’ `Last-Updated` + `Version`.
4. Append CHANGELOG entry.
5. If **phase tag**, push `main` & tags to GitHub immediately.

---

*Living document — refine as habits evolve. Keep hops short, logs loud, tests green, scenes bootable.*
