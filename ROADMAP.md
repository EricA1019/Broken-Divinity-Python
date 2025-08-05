# Broken Divinity - Development Roadmap

## Project Overview
**"New Babylon" Detective Investigation Game**  
Scene-driven ASCII supernatural mystery with tactical combat, set in a post-apocalyptic city where Detective Morrison investigates divine murders while managing a survivor colony.

## Development Philosophy: "Close-to-Shore"
- **Scene-Driven Development**: Each hop represents a complete story scene with green tests
- **Signal-Driven Architecture**: All components communicate via a central signal bus  
- **Registry-First Foundation**: Five core registries providing solid data-driven foundation
- **Warsim-Style UI**: Numbered options (1-9) for all menus, clean ASCII borders
- **Test-First Development**: Implement features incrementally, always maintaining green tests

## Current Status: v0.0.12 - SQLite Data Layer Foundation Complete ✅  
**SQLite-First Development Workflow Established**
- ✅ Complete SQLite database schema with 6 core tables + relationships
- ✅ JSON to SQLite migration system with comprehensive validation
- ✅ Data backend abstraction layer supporting both JSON and SQLite
- ✅ Database manager with backup, validation, and error handling
- ✅ Enhanced VS Code tasks for database management workflow
- ✅ **37/38 tests passing, SQLite foundation 99% complete**
- 🎯 **NEXT**: Hop 13 - Registry SQLite Integration

**New Development Methodology:**
- **SQLite Database** (`data/game.db`) - Primary data store for production
- **JSON Test Data** (`data/test_data/`) - Development and testing files  
- **Migration Tools** - Promote tested JSON content to database
- **Backend Abstraction** - Unified Registry API for both data sources

---

## NEW BABYLON STORY SEQUENCE
**"The Divine Murder Case"**

Detective Morrison awakens in his apartment 3 days after Yahweh's assassination. The world has changed - divine power has shattered, leaving survivors to rebuild in the ruins. As the only detective blessed with resurrection abilities, Morrison must investigate the murder while establishing New Babylon, a haven for survivors.

### Story Arc Overview
1. **Apartment Wake-Up** - Equipment tutorial, first status (hungover)
2. **First Combat** - Alley encounter, basic tactical system
3. **Divine Revelation** - Lucifer appears, bestows resurrection blessing  
4. **Colony Foundation** - Establish New Babylon, basic management
5. **Investigation Campaign** - Systematic case-building with evidence
6. **Epic Confrontation** - Final boss encounters with divine consequences

---

## SCENE-DRIVEN DEVELOPMENT PHASES

## PHASE 1: THE AWAKENING (Hops 11-18)
*"Detective Morrison's First Day in the New World"*

### Hop 11: Scene 1 - Apartment Exploration ✅ **COMPLETE**
**Player wakes up hungover in their apartment with basic items to examine.**

### Hop 12: SQLite Data Layer Foundation ✅ **COMPLETE**
**Establish SQLite database as primary data store with JSON compatibility.**
- ✅ SQLite database schema with 6 core tables (entities, abilities, etc.)
- ✅ JSON to SQLite migration system with validation
- ✅ Data backend abstraction (unified API for JSON/SQLite)
- ✅ Database manager with backup and error handling
- ✅ VS Code tasks for database workflow management
- ✅ Comprehensive test suite (37/38 tests passing)

### Hop 13: Registry SQLite Integration 🎯 **CURRENT TARGET**
**Update existing registries to use SQLite backend with JSON fallback.**

**Development Status**: 14/14 apartment tests passing, fully functional
- ✅ ApartmentLocation class with 4 examinable items (revolver, jacket, badge, bottle)
- ✅ CharacterState with status effect persistence outside combat  
- ✅ Enhanced StateRegistry with stat_changes and duration tracking
- ✅ ApartmentScreen UI with 9 menu options integrated with MainUI
- ✅ Item examination system with detailed descriptions
- ✅ Status effects persist outside combat (hungover: -1 all stats, 2 hours)
- ✅ Game boots successfully, apartment exploration fully playable

**Technical Implementation**:
- ✅ src/game/locations.py - LocationItem dataclass, ApartmentLocation
- ✅ src/game/character_state.py - CharacterState with StateRegistry integration
- ✅ src/ui/apartment_screen.py - ApartmentScreen with menu actions
- ✅ Enhanced status effect JSON standardization
- ✅ JSON schema validation system implemented

**Story Elements**: Morrison wakes up 3 days after divine assassination, discovers personal items, feels effects of drinking. Sets up character's detective background and current state.

**Player Experience**: Examine 4 items, experience persistent status effects, navigate apartment with intuitive numbered menu options.

### Hop 12: Main Menu System with Character Creation ⚙️ **NEXT UP**
**Professional main menu as game entry point with character creation workflow.**

**Development Focus**:
- 🎯 Main menu system as game entry point (not apartment)
- 🎯 Character creation with background flavor options (Detective, Survivor, etc.)
- 🎯 Integration with existing MainUI framework and MenuScreen
- 🎯 Character background affects starting stats/items/abilities
- 🎯 Save/load system for character persistence
- 🎯 Settings menu with game options

**Enhanced Workflow Requirements**:
- ⚙️ JSON validation passes before development (Step 2)
- ⚙️ Character creation schema and templates created
- ⚙️ Test-first implementation with 100% green tests
- ⚙️ Manual player experience testing required
- ⚙️ Documentation updated with character system

**Technical Implementation**:
- 🎯 src/game/character_creation.py - Character creation system
- 🎯 src/ui/main_menu_screen.py - Main menu as entry point
- 🎯 data/character_backgrounds/ - Background definitions
- 🎯 Enhanced save/load for character persistence
- 🎯 Integration with existing MainUI MenuScreen framework

**Story Elements**: Player creates Detective Morrison's background, personalizing their approach to the investigation. Background choices affect starting equipment, abilities, and relationships.

**Player Experience**: Smooth main menu → character creation → apartment entry flow. Players feel ownership over their character's background and capabilities.

### Hop 13: First Combat Encounter
- Persistent status effects (outside combat duration)
- Basic item description system
- Story progression state tracking

**Apartment Layout**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ LOCATION: Morrison's Apartment     Time: 08:30     Status: Hungover         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ You wake in your cramped apartment. Sunlight filters through dirty windows.  ║
║ The smell of stale whiskey hangs in the air. Your head pounds mercilessly.   ║
║                                                                               ║
║ Items Visible:                                                               ║
║ • S&W Model 10 Revolver (on nightstand) - Your old service weapon           ║
║ • Leather Jacket (on chair) - Worn but protective                           ║
║ • Detective Badge (on dresser) - Symbol of your authority                   ║
║ • Empty Whiskey Bottle (floor) - Last night's poor choice                   ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Examine Revolver   4. Check Badge       7. Search Room                   ║
║ 2. Get Jacket         5. Drink Water       8. Look Outside                  ║
║ 3. Read Notes         6. Check Mirror      9. Leave Apartment               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Apartment location renders with examination options
- [ ] Basic item examination functional (descriptions only)
- [ ] S&W Model 10 discovered (.38 caliber physical damage concept)
- [ ] Leather jacket examined (+2 defense concept)
- [ ] Hungover status persists outside combat
- [ ] MainUI exploration system working

### Hop 12: Scene 2 - Multi-Enemy Combat Encounter
**Enhanced Tactical Combat with Multiple Foes**
- Downtown alley location with complex encounter
- 2x Imp enemies + 1x Dona Margarita (mini-boss)
- Turn order with multiple enemies
- Group tactics and targeting
- Enhanced combat UI for multi-enemy battles
- Victory/defeat/flee outcomes

**Combat Enhancement Requirements:**
- Multi-enemy battle system
- Enhanced targeting mechanics
- Group initiative calculations
- Dona Margarita boss entity
- Complex battle UI layouts

**Alley Combat Layout**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ COMBAT: Downtown Alley     Turn: 3     Morrison vs Demonic Forces           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Morrison [HP: 18/20] [MP: 10/10]        Imp1 [HP: 12/12] [Ready]            ║
║ Status: Hungover (-1 all stats)         Imp2 [HP: 10/12] [Bleeding]         ║
║                                         Dona Margarita [HP: 25/25] [Boss]   ║
║ > Morrison fires .38 round at Imp2 for 6 damage!                           ║
║ > Imp1 casts Infernal Bolt at Morrison for 4 damage!                       ║
║ > Dona Margarita prepares devastating attack...                             ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Target Imp1         4. Use Ability       7. Check Enemies               ║
║ 2. Target Imp2         5. Take Cover        8. Attempt Flee                ║
║ 3. Target Margarita    6. Defend            9. Combat Options              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Multi-enemy combat system functional
- [ ] Turn order handles 4 entities correctly
- [ ] Targeting system works for multiple enemies
- [ ] Dona Margarita boss mechanics working
- [ ] Complex combat UI displays clearly

### Hop 13: Scene 3 - The Unwinnable Angel Battle
**Maddened Angel Encounter (Story Beat)**
- Post-victory, overwhelming enemy appears
- Maddened Angel entity (unbeatable boss)
- Scripted defeat after limited turns
- Introduces resurrection mechanic naturally
- Sets up divine power system
- Story exposition through combat

**Angel Encounter Systems:**
- Unbeatable enemy mechanics
- Scripted battle progression
- Death/resurrection trigger
- Divine power introduction
- Story-driven combat pacing

**Angel Battle Layout**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ DIVINE COMBAT: Maddened Angel     Turn: 2     Morrison vs Divine Wrath      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Morrison [HP: 5/20] [MP: 2/10]          Maddened Angel [HP: ???/???]       ║
║ Status: Terrified, Bleeding             Status: Divine Fury, Untouchable    ║
║                                                                               ║
║ The angel's presence burns your soul. Its six wings blaze with holy fire.   ║
║ Your .38 rounds bounce harmlessly off its divine form.                      ║
║ "MORTAL. YOUR TIME HAS ENDED."                                              ║
║                                                                               ║
║ > Morrison fires desperately - no effect!                                   ║
║ > Angel raises sword of pure light...                                       ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Fire Again          4. Pray             7. Last Words                    ║
║ 2. Run (Impossible)     5. Cower           8. Face Death                    ║
║ 3. Take Cover          6. Look for Exit    9. Accept Fate                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Angel encounter triggers after demon victory
- [ ] Unbeatable combat mechanics functional
- [ ] Scripted defeat after 2-3 turns
- [ ] Death triggers resurrection system
- [ ] Story progression advances correctly

### Hop 14: Scene 4 - Divine Revelation (Cutscene)
**Lucifer's Blessing System**
- Post-resurrection cutscene implementation
- Lucifer entity introduction (non-combat)
- Blessing buff system (.blessing damage subcategory)
- Resurrection badge activation
- Divine power mechanics explanation
- Story exposition integration

**Divine Systems Required:**
- Cutscene system with non-interactive dialogue
- Blessing damage subcategory
- Badge-triggered resurrection system
- Divine entity templates
- Story progression tracking

**Lucifer Encounter Layout**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ DIVINE ENCOUNTER: Mysterious Figure     Time: 09:15     Power: Awakening    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ A tall figure in an expensive suit materializes from shadows.                ║
║ His smile is perfect, his eyes ancient. Power radiates from him like heat.   ║
║                                                                               ║
║ "Detective Morrison. I am... call me Lucy. We need to talk."                 ║
║ "Yahweh's death has consequences. You're now blessed with resurrection."     ║
║ "Your badge is the anchor. Die, and you'll return here, in this alley."     ║
║ "Use this power. Investigate. Build. Survive the coming chaos."             ║
║                                                                               ║
║ Your badge grows warm. Power flows through you. [Blessing: +2 to all stats] ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                        [PRESS ANY KEY TO CONTINUE]                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Cutscene system displays non-interactive dialogue
- [ ] Blessing buff automatically applied (+2 to all stats)
- [ ] Badge becomes resurrection anchor (functional system)
- [ ] .blessing damage subcategory available for detective abilities
- [ ] Story state progression tracking

### Hop 15: Scene 5 - New Babylon Foundation
**Basic Colony Management Introduction**
- Settlement screen with basic buildings
- Resource tracking (survivors, materials, food)
- Population management basics
- Building placement system
- Simple economy foundation

**Colony Systems Required:**
- Settlement grid system (ASCII-based)
- Resource registry and tracking
- Building placement mechanics
- Population simulation basics
- Economic foundation

**New Babylon Layout**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ NEW BABYLON SETTLEMENT     Population: 12     Resources: Basic              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║    [HQ] [ ? ] [ ? ]     Buildings Available:                                ║
║    [ ? ] [ ? ] [ ? ]     • Headquarters (built)                             ║
║    [ ? ] [ ? ] [ ? ]     • Shelter (houses 4 survivors)                     ║
║                          • Workshop (produces materials)                     ║
║ Current Status:          • Clinic (heals injured survivors)                  ║
║ Survivors: 12/16         • Garden (produces food)                            ║
║ Materials: 15 units                                                          ║
║ Food: 8 days supply      "A small but growing community of survivors who    ║
║ Morale: Hopeful          look to you for leadership and protection."         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Build Shelter      4. Manage People      7. Settlement Overview          ║
║ 2. Build Workshop     5. Assign Tasks       8. Colony Status                ║
║ 3. Build Clinic       6. Check Resources    9. Leave Settlement             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Settlement screen displays building grid
- [ ] Basic building placement functional
- [ ] Resource tracking accurate (survivors, materials, food)
- [ ] Population management working
- [ ] Economic basics operational

### Hop 16: Equipment Registry & Advanced Systems
**Complex Equipment and Damage Type Systems**
- Equipment Registry implementation (6th registry)
- Damage Type Registry for ballistic subcategories
- Full inventory system with equipment slots
- Advanced weapon variations using suffix system
- Ammo tracking and reload mechanics
- Equipment stat integration in all systems

**Advanced Systems Required:**
- Equipment Registry with slot management
- Damage Type Registry (.38, .357, .45, etc.)
- Full inventory UI and management
- Equipment-combat integration
- Suffix-based weapon generation
- Advanced item mechanics

**Success Criteria**
- [ ] Equipment Registry operational
- [ ] Damage Type Registry with ballistic subcategories
- [ ] Full equipment slot system functional
- [ ] Weapon variations generated via suffix system
- [ ] Advanced combat-equipment integration

### Hop 17: Tutorial Integration & Polish
**Seamless Scene Transitions**
- Smooth progression between all tutorial scenes
- Tutorial hints and guidance system
- Save/load functionality for scene progress
- Performance optimization for scene systems
- Bug fixes and user experience polish

**Integration Requirements:**
- Scene transition system
- Tutorial guidance framework
- Progress saving system
- Performance profiling
- User experience testing

**Success Criteria**
- [ ] All four tutorial scenes flow smoothly together
- [ ] Tutorial guidance helps new players
- [ ] Save/load preserves scene progress correctly
- [ ] Performance acceptable across all scenes
- [ ] No major bugs in tutorial sequence

### Hop 18: Phase 1 Completion Testing
**Full Tutorial Validation**
- End-to-end testing of complete tutorial sequence
- Performance benchmarking with all systems active
- Regression testing to ensure no broken existing features
- Documentation updates for new systems
- Preparation for Phase 2 development

**Quality Assurance Focus:**
- Complete tutorial playthrough testing
- All registry systems working together
- UI/UX consistency across scenes
- Performance profiling
- Documentation completeness

**Success Criteria**
- [ ] Complete tutorial sequence functional
- [ ] All existing tests still passing (190+)
- [ ] Performance meets quality standards
- [ ] Documentation updated and complete
- [ ] Ready for investigation campaign development

---

## PHASE 2: THE INVESTIGATION (Hops 19-27)
*"Building the Case Against Divine Killers"*

### Hop 19-21: Evidence System & Case Building
**Systematic Investigation Mechanics**
- Evidence collection and analysis
- Witness interview system
- Clue correlation mechanics
- Case file management
- Investigation skill progression

### Hop 22-24: Multiple Crime Scenes  
**Expanding the Mystery**
- Additional location types
- Procedural evidence generation
- Advanced investigation techniques
- Suspect tracking system
- Red herring mechanics

### Hop 25-27: Advanced Investigation Features
**Professional Detective Work**
- Forensic analysis mini-games
- Interrogation dialogue trees
- Case conclusion system
- Multiple suspect management
- Investigation campaign structure

---

## PHASE 3: COLONY EXPANSION (Hops 28-37)
*"Building New Babylon into a Thriving Community"*

### Hop 28-32: Advanced Colony Management
**Complex Settlement Systems**
- Advanced building types and upgrades
- Resource production chains
- Population specialization
- Trade and diplomacy systems
- Threat management (raids, disasters)

### Hop 33-37: Regional Expansion
**Beyond New Babylon**
- Multiple settlement management
- Regional exploration and claiming
- Inter-settlement trade networks
- Large-scale threat response
- Endgame colony objectives

---

## PHASE 4: EPIC CONCLUSION (Hops 38-47)
*"The Truth Behind Yahweh's Murder"*

### Hop 38-42: Divine Conspiracy
**Uncovering the Truth**
- Divine entity encounters
- Cosmic-scale investigation
- Multiple ending paths
- Divine combat mechanics
- Reality-altering consequences

### Hop 43-47: Final Confrontations & Polish
**Epic Climax & Game Completion**
- Final boss encounters
- Multiple victory conditions
- Ending cinematics
- Achievement system
- Performance optimization and final polish

---

## TECHNICAL FOUNDATION PRESERVATION
**Completed Systems to Build Upon**

### Registry Systems ✅ **All Operational**
- **StateRegistry**: Status effects with duration tracking
- **BuffRegistry**: Positive effects and stacking rules
- **EntityRegistry**: Creatures, stats, and classification
- **AbilityRegistry**: Detective abilities with costs/cooldowns  
- **SuffixRegistry**: Procedural generation foundation

### Combat Engine ✅ **Battle-Ready**
- **BattleManager**: Entity state tracking and battle logic
- **TurnManager**: Initiative system and turn order
- **GameStateMachine**: Screen transitions and state management
- **CombatEntity**: HP/mana tracking and lifecycle management
- **Signal Integration**: Event-driven combat communication

### UI Framework ✅ **Professional Interface**
- **MainUI**: tcod-based rendering with numbered menus
- **MenuScreen**: Flexible screen system with option handling
- **StatusData**: Header information display
- **Screen Stacking**: Push/pop navigation system
- **Signal Integration**: UI event handling

### Infrastructure ✅ **Rock-Solid Foundation**
- **SignalBus**: Central communication system
- **BaseRegistry**: Data-driven content loading
- **Test Suite**: 183/190 tests passing (96% success rate)
- **Virtual Environment**: Python 3.12 with all dependencies
- **Git Repository**: Version control with clean history

---

## SUCCESS METRICS & QUALITY GATES

### Per-Hop Requirements
- All unit tests pass (green status)
- Integration tests with existing systems pass
- Performance benchmarks met
- Scene progression functional
- User experience validated

### Phase Gate Requirements
- Complete scene sequence functional
- End-to-end testing passes
- Performance stress testing complete
- Story progression working correctly
- Regression testing suite passes

### Scene-Driven Quality Assurance
- Each scene tells part of the complete story
- Player progression feels natural and engaging
- Systems integrate seamlessly with narrative
- Technical foundation supports story requirements
- Polish level appropriate for story beats

---

## DEVELOPMENT WORKFLOW NOTES

### Scene-First Approach Benefits
- **Clear Milestones**: Each hop represents a playable story beat
- **User-Focused**: Features driven by player experience, not technical requirements
- **Natural Testing**: Story progression provides comprehensive testing scenarios
- **Motivation**: Completing scenes feels like real progress on the game
- **Scope Control**: Story beats naturally limit feature scope

### Technical Foundation Utilization
- **Registry Systems**: All five registries provide data-driven content
- **Signal Bus**: Enables loose coupling between story and technical systems
- **MainUI Framework**: Professional interface for all story scenes
- **Combat Engine**: Powers all tactical encounters throughout the story
- **Test Suite**: Ensures reliable foundation for story development

### Close-to-Shore Methodology
- **Short Hops**: Each scene increment is small and testable
- **Always Green**: Never break existing story progression
- **Data-Driven**: Story content lives in JSON files
- **Signal Integration**: Story events trigger appropriate system responses
- **Incremental Polish**: Each hop improves overall experience

#EOF
