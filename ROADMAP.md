# Broken Divinity - Development Roadmap

## Project Overview
An ASCII-based settlement builder with procedural suffix-driven content and tactical combat, inspired by Warsim's numbered menu system, Dwarf Fortress colony management, and Detective investigation mechanics.

## Development Philosophy
- **Hop-Based Development**: Each hop represents a complete, testable feature with green tests
- **Signal-Driven Architecture**: All components communicate via a central signal bus
- **Registry-First Approach**: Five core registries built from the beginning with full integration
- **Warsim-Style UI**: Numbered options (1-9) for all menus, clean ASCII borders
- **Test-Driven**: Add registries one at a time, test until green, then integration testing

## Current Status: Reset to Hop 1 - Clean Start ✅
**Project Scaffold with Enhanced Vision**
- ✅ Basic project structure (src/, tests/, config/, Documentation/)
- ✅ Comprehensive lore and systems document (Brokendivinity.md)
- ✅ Detective abilities JSON schema defined
- ✅ Warsim-inspired UI design specified
- 🎯 **NEXT**: Complete roadmap rewrite with new architecture

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

### Hop 3: StateRegistry (Status Effects) 🎯 **NEXT**
**First Registry Implementation**
- Stun, Bleed, Poison, Slow, Haste tracking
- Duration-based effects system
- Stack/conflict resolution rules
- Signal integration for status changes

**Success Criteria**
- [ ] StateRegistry loads/applies all status types
- [ ] Duration countdown works correctly
- [ ] Status conflicts resolve properly
- [ ] SignalBus integration functional
- [ ] All tests green before proceeding

### Hop 4: BuffRegistry (Positive Effects)
**Beneficial Status System**
- Defense bonus, Attack bonus, Speed bonus
- Temporary vs permanent buffs
- Stacking rules and cap limits
- Integration with StateRegistry

**Success Criteria**
- [ ] BuffRegistry manages all positive effects
- [ ] Stacking calculations accurate
- [ ] Conflicts with StateRegistry resolved
- [ ] Signal communication working
- [ ] Integration tests with StateRegistry pass

### Hop 5: EntityRegistry (Creatures & Stats)
**Character and Enemy Data**
- Detective base stats and growth
- Enemy archetypes and stat blocks
- Flee chance calculations
- Boss immunity flags

**Success Criteria**
- [ ] EntityRegistry loads creature definitions
- [ ] Stat calculations work correctly
- [ ] Boss/elite/normal classifications
- [ ] SignalBus integration complete
- [ ] Tests cover all entity types

### Hop 6: AbilityRegistry (JSON-Driven Abilities)
**Detective Abilities System**
- Load DetectiveAbilities.json
- Mana/ammo cost validation
- Cooldown tracking per ability
- Damage type classification

**Success Criteria**
- [ ] AbilityRegistry reads JSON correctly
- [ ] All Detective abilities accessible
- [ ] Cost validation working
- [ ] Cooldown system functional
- [ ] JSON schema strictly enforced

### Hop 7: SuffixRegistry (Procedural Generation)
**Affix System Foundation**
- Enemy suffix combinations
- Weapon part generation
- Rarity weighting system
- Procedural name generation

**Success Criteria**
- [ ] SuffixRegistry generates valid combinations
- [ ] Rarity weights working
- [ ] Name generation functional
- [ ] All registries integrate cleanly
- [ ] Full registry suite tests pass

### Hop 8: Warsim-Style UI Framework
**Numbered Menu System**
- Consistent 1-9 numbered options
- ASCII borders and clean layout
- Input validation and error handling
- Screen state management

**UI Layout Design**
```
╔═══════════════════════════════════════════════════════════════════╗
║ Location: Downtown Alley    Gold: 1,247    Time: 15:42 Day 23    ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  [Main text area for descriptions, combat, dialogue]             ║
║                                                                   ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║ 1. Fight          4. Use Ability      7. Inventory               ║
║ 2. Defend         5. Examine Area     8. Character Stats         ║
║ 3. Flee           6. Talk             9. Settings                ║
╚═══════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Status header displays correctly
- [ ] Numbered menus respond to 1-9 keys
- [ ] Screen transitions work smoothly
- [ ] ASCII borders render properly
- [ ] State management functional

### Hop 9: Basic Combat Engine
**F-D-I-A Combat System**
- Fight/Defend/Inventory/Ability menu structure
- Turn-based initiative system
- Basic damage calculations
- Status effect integration

**Combat Flow**
1. Enter combat → grid renders
2. Initiative roll (speed + random)
3. Player turn: 1-Fight, 2-Defend, 3-Inventory, 4-Ability
4. Enemy AI turn
5. Status effects tick
6. Check win/lose/flee conditions
7. Reward screen → back to exploration

**Success Criteria**
- [ ] Combat initiates from exploration
- [ ] F-D-I-A menu working with number keys
- [ ] Turn order calculated correctly
- [ ] Basic attacks resolve damage
- [ ] Status effects apply and tick
- [ ] Combat ends with proper rewards

### Hop 10: Dynamic ASCII Combat Grid
**Tactical Positioning System**
- Grid size adapts to encounter (3x3 to 7x7)
- Entity positioning and movement
- Line-of-sight calculations
- Visual combat representation

**Grid Examples**
```
Small Encounter (3x3):    Large Arena (5x5):
┌─────┐                   ┌─────────┐
│ E . │                   │ . . E . │
│ . . │                   │ . . . . │
│ . D │                   │ . . . . │
└─────┘                   │ . . . . │
                          │ . D . . │
                          └─────────┘
```

**Success Criteria**
- [ ] Grid renders with proper borders
- [ ] Entity symbols display correctly
- [ ] Movement validates position
- [ ] Grid size adapts to encounter type
- [ ] Visual updates during combat

### Hop 11: Ability System Integration
**JSON-Driven Combat Abilities**
- Detective abilities from JSON loaded
- Mana/ammo cost validation
- Cooldown tracking between rounds
- Damage type processing

**Detective Abilities Integration**
- Snap Shot: Quick pistol (4 damage, 1 ammo)
- Aimed Shot: Precise shot (8 damage, 1 ammo, 1 mana, 2 cooldown)
- Patch Yourself Up: Heal over time (6 heal, 2 mana, 3 cooldown)
- Take Cover: Defense buff (+3 defense, 1 cooldown)

**Success Criteria**
- [ ] All 4 Detective abilities usable in combat
- [ ] Costs deducted correctly
- [ ] Cooldowns prevent spamming
- [ ] Heal over time effects work
- [ ] Defense buffs apply properly

### Hop 12: Status Effect Expansion
**Advanced Status System**
- Damage over time effects (bleed, poison)
- Defensive buffs and resistance
- Speed modifiers affecting initiative
- Complex status interactions

**Success Criteria**
- [ ] DoT effects tick each round
- [ ] Multiple status effects stack correctly
- [ ] Speed changes affect turn order
- [ ] Status immunity rules work
- [ ] Visual indicators for all effects

### Hop 13: Morale & Flee System
**Combat Escape Mechanics**
- Low HP entities attempt flee (50% base)
- Boss immunity to fleeing
- Elite morale modifiers
- Failed flee burns action

**Success Criteria**
- [ ] Flee attempts at low HP trigger
- [ ] Success rates calculated correctly
- [ ] Boss immunity enforced
- [ ] Failed attempts consume turn
- [ ] Player can attempt to flee

### Hop 14: Reward & XP System
**Post-Combat Progression**
- XP distribution (killer full, allies share)
- Level-up stat increases
- Ability point allocation
- Loot generation integration

**Success Criteria**
- [ ] XP awarded correctly after combat
- [ ] Level-up triggers stat increases
- [ ] Ability points accumulated
- [ ] Loot appears in inventory
- [ ] Progression persists between fights

### Hop 15: Combat Integration Testing
**Full Combat System Validation**
- End-to-end combat scenarios
- All registries working together
- Performance testing with multiple entities
- Edge case handling

**Success Criteria**
- [ ] Complex multi-enemy fights work
- [ ] All abilities interact correctly
- [ ] Status effects combine properly
- [ ] Performance acceptable for 5v5 fights
- [ ] No crashes or data corruption

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

### Epoch 1: Combat Foundation (Hops 1-15)
**Complete tactical combat system with Warsim-style UI**
- All 5 registries operational
- F-D-I-A combat fully functional
- Detective abilities integrated
- Status effects and progression working

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
