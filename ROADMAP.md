# Broken Divinity - Development Roadmap

## Project Overview
An ASCII-based settlement builder with procedural suffix-driven content and tactical combat, inspired by Warsim's numbered menu system, Dwarf Fortress colony management, and Detective investigation mechanics.

## Development Philosophy
- **Hop-Based Development**: Each hop represents a complete, testable feature with green tests
- **Signal-Driven Architecture**: All components communicate via a central signal bus
- **Registry-First Approach**: Five core registries built from the beginning with full integration
- **Warsim-Style UI**: Numbered options (1-9) for all menus, clean ASCII borders
- **Test-Driven**: Add registries one at a time, test until green, then integration testing

## Current Status: v0.0.9 - Basic Combat Engine Complete ✅
**Combat System Foundations Operational**
- ✅ Signal Bus Foundation (17 tests passing)
- ✅ StateRegistry (13 tests passing) 
- ✅ BuffRegistry (14 tests passing)
- ✅ EntityRegistry (14 tests passing)
- ✅ AbilityRegistry (17 tests passing)
- ✅ SuffixRegistry (12/13 tests passing, 1 flaky)
- ✅ MainUI Framework (22 tests passing)
- ✅ Basic Combat Engine (34 tests passing)
- ✅ **174/174 tests passing, game boots with professional UI**
- 🎯 **NEXT**: Hop 10 - Combat Screen Development

---

## PHASE 1: CORE COMBAT SYSTEM (Hops 2-15)

### Hop 2: Signal Bus Foundation ✅ **COMPLETE**
**Central Communication System**
- ✅ SignalBus class with pub/sub pattern
- ✅ Event registration and emission
- ✅ Registry communication protocol
- ✅ Hot-reload signal definitions

**Success Criteria**
- ✅ SignalBus can register/emit events
- ✅ Multiple subscribers per event type
- ✅ Event payload validation
- ✅ Unit tests pass for all signal operations

### Hop 3: StateRegistry (Status Effects) ✅ **COMPLETE**
**First Registry Implementation**
- ✅ Stun, Bleed, Poison, Slow, Haste tracking
- ✅ Duration-based effects system
- ✅ Stack/conflict resolution rules
- ✅ Signal integration for status changes
- ✅ Enhanced BaseRegistry for single-object JSON loading
- ✅ Virtual environment setup with pytest
- ✅ Comprehensive test suite (13 StateRegistry tests)

**Success Criteria**
- ✅ StateRegistry loads/applies all status types
- ✅ Duration countdown works correctly
- ✅ Status conflicts resolve properly
- ✅ SignalBus integration functional
- ✅ All tests green before proceeding
- ✅ systemupkeep.md updated with StateRegistry APIs

**Workflow Improvements Identified:**
- ✅ JSON loading enhancement needed for BaseRegistry
- ✅ VSCode task configuration for virtual environment
- ✅ Single-object JSON file support critical for data organization
- ✅ Test-first development caught integration issues early
- ✅ Systematic debugging approach resolved complex data loading bug

### Hop 4: BuffRegistry (Positive Effects) ✅ **COMPLETE**
**Beneficial Status System**
- ✅ Defense bonus, Attack bonus, Speed bonus
- ✅ Temporary vs permanent buffs
- ✅ Stacking rules and cap limits
- ✅ Integration with StateRegistry via signals
- ✅ 5 buff types: rage, shield_wall, combat_focus, combat_training, blessing
- ✅ Comprehensive test suite (14 BuffRegistry tests)
- ✅ Enhanced game launcher with BuffRegistry testing

**Success Criteria**
- ✅ BuffRegistry manages all positive effects
- ✅ Stacking calculations accurate
- ✅ Signal communication working (separate from StateRegistry)
- ✅ Integration tests with StateRegistry pass
- ✅ Full test suite passing (84/84 tests)

**Workflow Improvements Identified:**
- ✅ Test-first development approach proved highly effective
- ✅ Signal bus real testing approach better than mocking
- ✅ Enhanced game launcher validates registries automatically  
- ✅ BaseRegistry pattern enables rapid registry development
- ✅ JSON individual file approach scales well for content

### Hop 5: EntityRegistry (Creatures & Stats) ✅ **COMPLETE**
**Character and Enemy Data**
- ✅ Detective base stats and growth
- ✅ Enemy archetypes and stat blocks
- ✅ Flee chance calculations
- ✅ Boss immunity flags
- ✅ Entity type classification (player, normal, elite, boss)
- ✅ Stat calculation system with modifiers
- ✅ Comprehensive test suite (14 EntityRegistry tests)
- ✅ Enhanced game launcher with EntityRegistry testing

**Success Criteria**
- ✅ EntityRegistry loads creature definitions
- ✅ Stat calculations work correctly
- ✅ Boss/elite/normal classifications
- ✅ SignalBus integration complete
- ✅ Tests cover all entity types
- ✅ Full test suite passing (98/98 tests)

**Workflow Improvements Identified:**
- ✅ Real signal bus testing continues to be more effective than mocking
- ✅ BaseRegistry pattern enabled rapid EntityRegistry development
- ✅ JSON individual file approach scales excellently for entity content
- ✅ Test-first development caught data loading pattern issues early
- ✅ Enhanced game launcher now validates all three registries automatically

### Hop 6: AbilityRegistry (JSON-Driven Abilities) ✅ **COMPLETE**
**Detective Abilities System**
- ✅ Load DetectiveAbilities.json with comprehensive schema
- ✅ Mana/ammo cost validation and tracking
- ✅ Cooldown tracking per ability
- ✅ Damage type classification (physical, magic, ranged)
- ✅ Comprehensive test suite (17 AbilityRegistry tests)
- ✅ Entity-ability association system

**Success Criteria**
- ✅ AbilityRegistry reads JSON correctly
- ✅ All Detective abilities accessible
- ✅ Cost validation working
- ✅ Cooldown system functional
- ✅ JSON schema strictly enforced

**Workflow Improvements Identified:**
- ✅ Complex JSON schema validation proves BaseRegistry flexibility
- ✅ Entity-ability linking enables dynamic ability assignment
- ✅ Cost tracking system enables resource management
- ✅ Test coverage for all ability types ensures combat readiness

### Hop 7: SuffixRegistry (Procedural Generation) ✅ **COMPLETE**
**Affix System Foundation**
- ✅ Enemy suffix combinations with proper weighting
- ✅ Weapon part generation support
- ✅ Rarity weighting system (common, rare, epic, legendary)
- ✅ Procedural name generation for variants
- ✅ Comprehensive test suite (12/13 tests passing, 1 flaky)
- ✅ Entity variant generation with stat modifications

**Success Criteria**
- ✅ SuffixRegistry generates valid combinations
- ✅ Rarity weights working correctly
- ✅ Name generation functional
- ✅ All registries integrate cleanly
- ✅ Full registry suite tests pass (132/133)

### Hop 8: Warsim-Style UI Framework ✅ **COMPLETE**
**Numbered Menu System**
- ✅ Consistent 1-9 numbered options
- ✅ ASCII borders and clean layout  
- ✅ Input validation and error handling
- ✅ Screen state management
- ✅ tcod rendering backend integration
- ✅ MainUI class with comprehensive features
- ✅ MenuScreen, MenuOption, StatusData dataclasses
- ✅ Screen stacking (push/pop) support
- ✅ Signal bus integration for UI actions
- ✅ Test-friendly rendering fallback
- ✅ Complete test suite (133/133 tests passing)
- ✅ Integrated into main game launcher

**MainUI Layout Design (Current Implementation)**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ Broken Divinity v0.0.8    Detective Status: Healthy    Resources: Available ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Welcome to Broken Divinity - ASCII Detective Investigation Game             ║
║                                                                               ║
║  [Main content area - dynamic based on current screen]                      ║
║  - Location descriptions and ASCII art                                       ║
║  - Combat grids and action results                                           ║
║  - Investigation scenes and dialogue                                         ║
║  - Character sheets and inventory                                            ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Investigate     4. Character      7. Settings                            ║
║ 2. Combat          5. Inventory      8. Save Game                           ║
║ 3. Explore         6. Abilities      9. Exit                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- ✅ Status header displays correctly
- ✅ Numbered menus respond to 1-9 keys  
- ✅ Screen transitions work smoothly
- ✅ ASCII borders render properly
- ✅ State management functional
- ✅ All tests green before proceeding
- ✅ Game launches with UI interface

**Workflow Improvements Identified:**
- ✅ tcod integration successful for ASCII rendering
- ✅ Flexible MenuScreen constructor enables multiple calling patterns
- ✅ Test-first development caught API compatibility issues early
- ✅ Signal bus integration provides clean UI event handling
- ✅ Fallback rendering enables headless testing
- ✅ Main game launcher now displays professional UI interface

### Hop 9: Basic Combat Engine ✅ **COMPLETE**
**Menu-Driven Combat System**
- ✅ Battle manager with entity state tracking
- ✅ Turn manager with initiative system 
- ✅ Game state machine for screen transitions
- ✅ MainUI integration for combat screens
- ✅ Combat entity management with HP/mana tracking
- ✅ Battle result system (victory/defeat/flee)

**Combat Flow Architecture**
1. ✅ GameStateMachine manages state transitions
2. ✅ BattleManager handles combat entities and battle state
3. ✅ TurnManager calculates initiative and manages turn order
4. ✅ CombatEntity dataclass tracks HP, mana, alive status
5. ✅ Action recording system for combat history
6. ✅ Signal bus integration for combat events
7. ✅ Screen stubs created for all game states

**Success Criteria**
- ✅ Combat screen renders in MainUI framework
- ✅ Turn order calculation functional (initiative + randomization)
- ✅ Entity lifecycle management (create, damage, heal, death)
- ✅ Battle state tracking (active/victory/defeat/flee)
- ✅ State machine enables proper screen transitions
- ✅ All combat tests passing (34 new tests)
- ✅ Integration with existing registry systems

**Workflow Improvements Identified:**
- ✅ Test-first approach ensured comprehensive coverage
- ✅ Dataclass pattern effective for combat entities
- ✅ Signal bus enables loose coupling between systems
- ✅ Screen stub approach allows incremental UI development
- ✅ Game state machine provides clear navigation structure

### Hop 10: Combat Screen Development 🎯 **NEXT**
**MainUI Combat Interface**
- Combat-specific screen layouts
- Entity positioning display (ASCII grid or list)
- Action feedback and damage numbers
- Status effect visual indicators
- Combat log integration

**Visual Combat Design**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ COMBAT: Downtown Alley     Turn: 3     Initiative: Detective > Thug         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Detective [HP: 18/20] [MP: 8/10]     Thug [HP: 12/15] [Bleeding]            ║
║                                                                               ║
║ > Detective fires aimed shot at Thug for 6 damage!                          ║
║ > Thug takes 2 bleeding damage                                              ║
║ > Thug swings club at Detective for 4 damage!                              ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Attack          4. Use Ability      7. Check Status                      ║
║ 2. Defend          5. Use Item         8. Attempt Flee                      ║
║ 3. Take Cover      6. Examine Enemy    9. Combat Options                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Combat screen renders properly in MainUI
- [ ] Entity health/mana displays update
- [ ] Action feedback shows clearly
- [ ] Status effect indicators visible
- [ ] Combat controls respond to 1-9 keys

### Hop 11: Investigation Screen System
**Detective Work Interface**
- Investigation scene rendering
- Evidence collection mechanics
- Clue analysis and deduction
- Interview and interrogation screens
- Case file management

**Investigation Layout**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ INVESTIGATION: Crime Scene Alpha     Evidence: 3/7     Suspects: 2          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ You examine the abandoned warehouse. Blood stains lead toward the basement.   ║
║                                                                               ║
║ Evidence Found:                                                               ║
║ • Bloody footprint (Size 11, distinctive tread)                             ║
║ • Torn fabric (High-quality wool, navy blue)                                ║
║ • Cigarette butt (Brand: Lucky Strike, fresh)                               ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Examine Area      4. Interview Witness   7. Review Case File             ║
║ 2. Collect Evidence  5. Check for Prints    8. Contact Backup              ║
║ 3. Follow Trail      6. Analyze Clues       9. Leave Scene                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Investigation screens render in MainUI
- [ ] Evidence collection system functional
- [ ] Clue tracking and analysis working
- [ ] Interview mechanics integrated
- [ ] Case progression properly tracked

### Hop 12: Character Management Screen
**Player Progression Interface**
- Character sheet display
- Stat allocation and upgrades
- Equipment and inventory management
- Ability point distribution
- Experience and level tracking

**Character Sheet Layout**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ CHARACTER: Detective Morrison     Level: 3     XP: 1,250/2,000              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ STATS                    EQUIPMENT                  ABILITIES                ║
║ Health: 20/20           Weapon: .38 Revolver       Snap Shot      [Ready]   ║
║ Mana:   10/10           Armor:  Leather Coat       Aimed Shot     [Ready]   ║
║ Attack: 12              Badge:  Detective Shield    Patch Up       [Ready]   ║
║ Defense: 8                                          Take Cover     [Ready]   ║
║ Speed:  14              RESOURCES                                            ║
║                         Ammo: 18/24                                          ║
║ Ability Points: 2       Evidence: 12 pieces                                 ║
║                         Cash: $347                                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Allocate Points   4. Manage Equipment   7. Abilities Overview            ║
║ 2. Review Stats      5. Inventory          8. Case History                  ║
║ 3. Equipment Detail  6. Save Character     9. Return                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Character screen displays all stats correctly
- [ ] Stat allocation system functional
- [ ] Equipment management working
- [ ] Ability tracking accurate
- [ ] Experience and leveling system operational

### Hop 13: World Exploration System
**Location-Based Navigation**
- Multiple investigation locations
- Location discovery and unlocking
- Travel between areas
- Random encounter triggers
- Environmental storytelling

**Exploration Interface**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ EXPLORE: Central District     Time: 14:30     Day: 5     Weather: Overcast  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ The rain-slicked streets of the Central District stretch before you.        ║
║ Steam rises from manholes, and the distant sound of police sirens           ║
║ echoes between the towering buildings. Several locations catch your eye.    ║
║                                                                               ║
║ Available Locations:                                                         ║
║ • Police Station (HQ) - Always available                                    ║
║ • Downtown Alley - Crime scene reported                                     ║
║ • Harbor District - Suspicious activity                                     ║
║ • ? ? ? - Requires investigation                                            ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Police Station    4. Harbor District     7. Check Map                    ║
║ 2. Downtown Alley    5. Follow Lead         8. Review Notes                 ║
║ 3. ? ? ?             6. Random Patrol       9. Return to HQ                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Multiple locations accessible
- [ ] Location unlocking system working
- [ ] Travel mechanics functional
- [ ] Random encounters trigger properly
- [ ] Environmental descriptions engaging

### Hop 14: Save/Load System
**Game State Persistence**
- Complete game state serialization
- Multiple save slot management
- Auto-save functionality
- Game session restoration
- Data integrity validation

**Save System Features**
- Character progression preservation
- Investigation case state tracking
- Location unlock status
- Equipment and inventory persistence
- Settings and preferences storage

**Success Criteria**
- [ ] Game state saves completely
- [ ] Multiple save slots functional
- [ ] Auto-save triggers appropriately
- [ ] Load game restores all state
- [ ] Data corruption prevention working

### Hop 15: Core Game Loop Integration
**Complete System Validation**
- End-to-end gameplay scenarios
- All registries working together seamlessly
- Performance testing with complex states
- Edge case handling and error recovery
- Polish and user experience refinement

**Integration Testing Scope**
- Combat → Investigation → Exploration cycle
- Character progression across all systems
- Save/load functionality across game states
- UI transitions and state management
- Registry data consistency validation

**Success Criteria**
- [ ] Complete gameplay loop functional
- [ ] All systems integrate without conflicts
- [ ] Performance acceptable for extended play
- [ ] Error handling robust and user-friendly
- [ ] User experience polished and engaging

---

## PHASE 2: EXPLORATION & BACKGROUND SYSTEMS (Hops 16-25)

### Hop 16: File Template System
**JSON Schema Enforcement**
- Standardized templates for all JSON files
- Validation system for structure compliance
- Auto-generation tools for new content
- Version compatibility checks

### Hop 17: Exploration State Machine
**World Navigation System**
- Location discovery and travel
- Random encounter triggers
- Detective movement between areas
- Map unlocking progression

### Hop 18: Investigation Mechanics
**Detective Skills System**
- Evidence gathering abilities
- Clue analysis mini-games
- Interview and interrogation
- Case file management

### Hop 19: Enhanced Procedural Generation
**Advanced Suffix System**
- Multi-tier rarity weights
- Settlement research integration
- Weapon part combinations
- NPC personality generation

### Hop 20: Game Clock & Time
**World Time System**
- 3-minute ticks per combat round
- Day/night cycles
- Timed events and deadlines
- Long-cast ability integration

### Hop 21: Save/Load Infrastructure
**Persistence System**
- Game state serialization
- Registry data preservation
- Player progression tracking
- Multiple save slot support

### Hop 22: Enhanced AI Systems
**Smart Enemy Behavior**
- Tactical positioning AI
- Ability usage decision trees
- Group coordination tactics
- Dynamic difficulty scaling

### Hop 23: Equipment & Inventory
**Gear Management System**
- Equipment durability tracking
- Weapon customization
- Inventory grid management
- Crafting material storage

### Hop 24: Faction Reputation
**Diplomacy Framework**
- Holy/Infernal/Secular standings
- Reputation consequences
- Faction-specific benefits
- Political intrigue events

### Hop 25: Background Systems Integration
**Phase 2 Completion Testing**
- All exploration systems functional
- Investigation mechanics complete
- Save/load working properly
- Performance optimization complete

---

## PHASE 3: SETTLEMENT & OVERWORLD (Hops 26-35)

### Hop 26-30: Settlement Building Core
**ASCII Colony Management**
- Top-down settlement grid
- Building placement and upgrades
- Resource production chains
- Population management

### Hop 31-35: Overworld Integration
**World Map System**
- Multiple settlement locations
- Travel between regions
- Global events and consequences
- Endgame progression paths

---

## PHASE 4: ADVANCED FEATURES (Hops 36-45)

### Mystery Investigation Campaign
**Yahweh Death Investigation**
- Procedural case generation
- Multiple suspect mechanics
- Evidence-based conclusions
- Branching story outcomes

### Advanced Combat Features
**Tactical Depth Expansion**
- Area-of-effect ability templates
- Environmental hazards
- Team-based combat tactics
- Epic boss encounters

---

## EPOCH MILESTONES

### Epoch 1: Core Game Foundation (Hops 1-15)
**Complete detective investigation system with menu-driven UI**
- All 5 registries operational and tested
- MainUI framework with professional interface
- Combat system integrated with investigation
- Character progression and exploration systems
- Save/load functionality and core game loop

### Epoch 2: World Exploration (Hops 16-25)
**Investigation and exploration systems**
- Detective can explore world
- Investigation mechanics active
- Advanced procedural generation
- Background systems complete

### Epoch 3: Settlement Building (Hops 26-35)
**Colony management integration**
- Settlement construction working
- Resource management active
- Overworld travel functional
- Multiple locations accessible

### Epoch 4: Complete Game (Hops 36-45)
**Full feature integration**
- Mystery campaign playable
- Advanced combat features
- Endgame content available
- Polish and optimization complete

---

## Success Metrics & Quality Gates

### Per-Hop Requirements
- All unit tests pass (green status)
- Integration tests with existing hops pass
- Performance benchmarks met
- Code review completed
- Documentation updated
- **systemupkeep.md updated with new signals/APIs**

### Epoch Gate Requirements
- Complete feature demonstration
- End-to-end testing scenarios pass
- Performance stress testing complete
- User experience validation
- Regression testing suite passes

### Risk Mitigation
- Single registry implementation at a time
- Comprehensive testing before integration
- Rollback procedures for failed hops
- Feature flags for experimental systems
- Regular architecture review sessions
