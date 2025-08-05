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

## Current Status: v0.0.10 - Combat System Foundation Complete ✅
**Solid Technical Foundation Built**
- ✅ Signal Bus Foundation (17 tests passing)
- ✅ StateRegistry - Status effects system (13 tests passing) 
- ✅ BuffRegistry - Positive effects system (14 tests passing)
- ✅ EntityRegistry - Creatures and stats (14 tests passing)
- ✅ AbilityRegistry - Detective abilities (17 tests passing)
- ✅ SuffixRegistry - Procedural generation (12/13 tests passing)
- ✅ MainUI Framework - Professional interface (22 tests passing)
- ✅ Basic Combat Engine - Turn-based tactical system (34 tests passing)
- ✅ Infernal Combat System - Imp enemy with infernal abilities
- ✅ **183/190 tests passing, game boots with professional UI**
- 🎯 **NEXT**: Hop 11 - Scene 1: Apartment Exploration

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

## PHASE 1: THE AWAKENING (Hops 11-16)
*"Detective Morrison's First Day in the New World"*

### Hop 11: Scene 1 - Apartment Exploration ⚙️ **IN PROGRESS**
**Tutorial Environment & Equipment System**
- Apartment location with item examination
- Equipment slot system (weapon, armor, badge)
- S&W Model 10 revolver acquisition (.357 damage type)
- Old leather jacket equipment (+2 defense)
- Detective badge (enables resurrection mechanic)
- Hungover status effect (-1 to all stats, 2 hour duration)

**New Systems Required:**
- Equipment Registry with slot management
- Item interaction system 
- Location-based exploration screens
- Status effect with duration tracking
- Damage type system (.357 revolver rounds)

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
- [ ] Equipment system functional (weapon/armor/badge slots)
- [ ] S&W Model 10 provides .357 damage type attacks
- [ ] Leather jacket gives +2 defense when equipped
- [ ] Hungover status affects stats temporarily
- [ ] All equipment tests passing

### Hop 12: Scene 2 - First Combat Encounter
**Alley Tactical Combat Introduction**
- Downtown alley location with thug encounter
- Enhanced combat screen showing equipped items
- .357 revolver attacks vs basic physical
- Defense calculations with armor
- Turn-based tactical positioning
- Victory/defeat/flee outcomes

**Combat Enhancement Requirements:**
- Damage type effectiveness system
- Equipment stat integration in combat
- Enhanced combat UI showing gear
- Tactical positioning basics
- Ammo tracking for revolver

**Alley Combat Layout**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ COMBAT: Downtown Alley     Turn: 2     Morrison vs Street Thug              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Morrison [HP: 18/20] [Ammo: 5/6]        Thug [HP: 8/15] [Bleeding]         ║
║ Equipment: S&W Model 10 + Leather Jacket                                    ║
║                                                                               ║
║ > Morrison fires .357 round for 8 damage! Critical hit!                     ║
║ > Thug takes 2 bleeding damage from wound                                   ║
║ > Thug swings knife wildly, blocked by leather jacket!                     ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 1. Fire Revolver       4. Reload Weapon     7. Check Equipment             ║
║ 2. Aimed Shot          5. Take Cover        8. Attempt Flee                ║
║ 3. Pistol Whip         6. Examine Enemy     9. Combat Options              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Success Criteria**
- [ ] Combat screen displays equipment effects
- [ ] .357 damage type properly calculated
- [ ] Armor provides actual damage reduction
- [ ] Ammo tracking functional during combat
- [ ] Combat AI responds to player equipment

### Hop 13: Scene 3 - Divine Revelation (Cutscene)
**Lucifer's Blessing System**
- Post-combat cutscene implementation
- Lucifer entity introduction (non-combat)
- Blessing buff system (.blessing damage type)
- Resurrection badge activation
- Divine power mechanics explanation
- Story exposition integration

**Divine Systems Required:**
- Cutscene system with non-interactive dialogue
- Blessing damage type and mechanics
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
- [ ] .blessing damage type available for detective abilities
- [ ] Story state progression tracking

### Hop 14: Scene 4 - New Babylon Foundation
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

### Hop 15: Tutorial Integration & Polish
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

### Hop 16: Phase 1 Completion Testing
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

## PHASE 2: THE INVESTIGATION (Hops 17-25)
*"Building the Case Against Divine Killers"*

### Hop 17-19: Evidence System & Case Building
**Systematic Investigation Mechanics**
- Evidence collection and analysis
- Witness interview system
- Clue correlation mechanics
- Case file management
- Investigation skill progression

### Hop 20-22: Multiple Crime Scenes  
**Expanding the Mystery**
- Additional location types
- Procedural evidence generation
- Advanced investigation techniques
- Suspect tracking system
- Red herring mechanics

### Hop 23-25: Advanced Investigation Features
**Professional Detective Work**
- Forensic analysis mini-games
- Interrogation dialogue trees
- Case conclusion system
- Multiple suspect management
- Investigation campaign structure

---

## PHASE 3: COLONY EXPANSION (Hops 26-35)
*"Building New Babylon into a Thriving Community"*

### Hop 26-30: Advanced Colony Management
**Complex Settlement Systems**
- Advanced building types and upgrades
- Resource production chains
- Population specialization
- Trade and diplomacy systems
- Threat management (raids, disasters)

### Hop 31-35: Regional Expansion
**Beyond New Babylon**
- Multiple settlement management
- Regional exploration and claiming
- Inter-settlement trade networks
- Large-scale threat response
- Endgame colony objectives

---

## PHASE 4: EPIC CONCLUSION (Hops 36-45)
*"The Truth Behind Yahweh's Murder"*

### Hop 36-40: Divine Conspiracy
**Uncovering the Truth**
- Divine entity encounters
- Cosmic-scale investigation
- Multiple ending paths
- Divine combat mechanics
- Reality-altering consequences

### Hop 41-45: Final Confrontations & Polish
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
