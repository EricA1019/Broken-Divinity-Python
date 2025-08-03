# Broken Divinity - Development Roadmap

This roadmap outlines the development progression for the ASCII roguelike version of Broken Divinity, organized into discrete "hops" following the Close-to-Shore methodology.

## 🎯 Development Philosophy

Each hop represents a complete, testable feature that:
- ✅ Has green tests
- ✅ Produces a bootable prototype
- ✅ Includes verbose logging with system tags
- ✅ Follows data-driven principles
- ✅ Ends with a clean commit

## 📋 Phase 1: Foundation

### Core Infrastructure
- [x] **Hop 1**: Project Scaffold - VS Code workspace, dependencies, folder structure
- [ ] **Hop 2**: Minimal tcod Window - Black console with ESC handling
- [ ] **Hop 3**: Screen Layout Framework - 4-region console layout with borders
- [ ] **Hop 4**: Basic Entity Data Model - JSON entity loader with registry
- [ ] **Hop 5**: Prefix/Suffix Variant System - Entity modifiers with merge algorithm
- [ ] **Hop 6**: Action State Machine - Root menu with F/D/I/A key handling
- [ ] **Hop 7**: Combat Log System - Scrollable message history

### World Generation
- [ ] **Hop 8**: Simple Room Generator - Single rectangular room with walls/floor
- [ ] **Hop 9**: Multi-Room Dungeon - Connected rooms with corridors
- [ ] **Hop 10**: Player Movement - @ character movement with collision
- [ ] **Hop 11**: Enemy Placement - Random enemy spawning in rooms
- [ ] **Hop 12**: Field of View - tcod FOV with explored/visible states
- [ ] **Hop 13**: Room Event System - Combat/treasure/empty room triggers
- [ ] **Hop 14**: Turn-Based Time - Speed-based priority queue scheduler

### Combat System
- [ ] **Hop 15**: Basic Combat Initiation - Enemy collision starts combat mode
- [ ] **Hop 16**: Attack Resolution - Damage calculation and HP tracking
- [ ] **Hop 17**: Ability System Core - JSON abilities with effects and costs
- [ ] **Hop 18**: Buff/Debuff Framework - Temporary stat modifications
- [ ] **Hop 19**: Enemy AI Basic - Pathfinding and ability usage
- [ ] **Hop 20**: Death and Respawn - Permadeath with detective immunity
- [ ] **Hop 21**: Victory Conditions - Room/floor completion tracking

### Polish & Integration
- [ ] **Hop 22**: Inventory System - Item collection and usage
- [ ] **Hop 23**: Ability Menu - Asciimatics ability selection interface
- [ ] **Hop 24**: Save/Load Framework - JSON state persistence
- [ ] **Hop 25**: Settings System - YAML/TOML configuration
- [ ] **Hop 26**: Advanced Variants - Complex modifier combinations
- [ ] **Hop 27**: Polish Pass - Visual improvements and feedback
- [ ] **Hop 28**: Full Integration Test - End-to-end testing and validation

## 🔧 Technical Milestones

### Core Systems
- **Entity Registry**: JSON-driven entity loading with variant support
- **Combat Engine**: Turn-based resolution with abilities and effects
- **Dungeon Generator**: Procedural room-based layouts
- **UI Framework**: tcod rendering with asciimatics modal menus

### Data-Driven Content
- **Entity Variants**: Prefix/suffix modifiers for dynamic encounters
- **Ability System**: JSON-defined spells and skills
- **Item Generation**: Equipment with procedural properties
- **Alignment Restrictions**: Faction-based ability limitations

### Quality Assurance
- **Test Coverage**: Comprehensive pytest suite for all systems
- **Performance**: Efficient rendering for large dungeons
- **Compatibility**: Unicode support with fallback handling
- **Documentation**: Clear API documentation and usage examples

## 🎮 Feature Progression

### Early Prototype (Hops 1-7)
**Goal**: Basic playable framework
- Window rendering and input handling
- Entity loading and display
- Action menu navigation
- Combat log functionality

### Core Gameplay (Hops 8-14)
**Goal**: Dungeon exploration mechanics
- Procedural map generation
- Player movement and collision
- Basic enemy encounters
- Turn-based timing system

### Combat Depth (Hops 15-21)
**Goal**: Tactical combat system
- Damage calculation and effects
- Ability casting and resource management
- Enemy AI and pathfinding
- Victory/defeat conditions

### Polish Phase (Hops 22-28)
**Goal**: Complete gaming experience
- Inventory management
- User interface refinement
- Save/load functionality
- Performance optimization

## 📈 Success Metrics

### Technical Quality
- [ ] 100% test coverage for core systems
- [ ] Zero memory leaks in extended sessions
- [ ] Consistent frame rate on target hardware
- [ ] Clean separation of data and logic

### User Experience
- [ ] Intuitive keyboard and mouse controls
- [ ] Clear visual feedback for all actions
- [ ] Responsive interface with smooth transitions
- [ ] Comprehensive help and tutorial systems

### Content Depth
- [ ] Rich variety in procedural encounters
- [ ] Meaningful choice in character builds
- [ ] Balanced risk/reward progression
- [ ] Engaging tactical combat scenarios

## 🚀 Future Enhancements

### Phase 2 Considerations
- **Extended Content**: Additional enemy types, abilities, and items
- **Advanced Dungeons**: Multi-floor complexes with themed areas
- **Character Progression**: Experience and skill development
- **Narrative Elements**: Quest system and story integration

### Community Features
- **Modding Support**: Enhanced JSON schema for community content
- **Replay System**: Action recording and playback
- **Analytics**: Gameplay metrics and balance analysis
- **Documentation**: Comprehensive modding guides

## 📝 Development Notes

### Current Focus
Working on foundational systems with emphasis on:
- Robust entity management
- Clean state machine architecture
- Comprehensive testing framework
- Data-driven content pipeline

### Key Dependencies
- **python-tcod**: Core rendering and algorithms
- **asciimatics**: UI widget framework
- **pytest**: Testing infrastructure
- **PyYAML**: Configuration management

### Risk Mitigation
- Font compatibility testing across platforms
- Performance profiling for large dungeons
- State management complexity monitoring
- UI framework integration validation

---

*This roadmap is living document, updated as development progresses and priorities evolve.*
