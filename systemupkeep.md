# System Upkeep - Active Signals & APIs

## Overview
This document tracks all active signals, APIs, and component interfaces currently implemented in Broken Divinity. Updated after each hop completion during final validation.

**Last Updated**: Hop 8 (MainUI Framework) - v0.0.8  
**Next Update**: Hop 9 (Basic Combat Engine) completion

---

## Signal Bus System

### Core Signal Types (CoreSignal Enum)
All signals use the `CoreSignal` enum for type safety and consistency.

#### Registry Signals
- `REGISTRY_INITIALIZED` - Emitted when a registry completes initialization
- `REGISTRY_RELOADED` - Emitted when a registry reloads its data (hot-reload)
- `REGISTRY_ERROR` - Emitted when a registry encounters an error

#### Combat Signals
- `COMBAT_STARTED` - Emitted when combat begins
- `COMBAT_ENDED` - Emitted when combat concludes
- `TURN_STARTED` - Emitted at the beginning of each combat turn
- `TURN_ENDED` - Emitted at the end of each combat turn

#### Entity Signals
- `ENTITY_CREATED` - Emitted when a new entity is created
- `ENTITY_DESTROYED` - Emitted when an entity is destroyed
- `ENTITY_HP_CHANGED` - Emitted when entity health changes
- `ENTITY_DIED` - Emitted when an entity's health reaches 0

#### Ability Signals
- `ABILITY_USED` - Emitted when an ability is activated
- `ABILITY_COOLDOWN_STARTED` - Emitted when an ability goes on cooldown
- `ABILITY_COOLDOWN_ENDED` - Emitted when an ability cooldown expires

#### Status Effect Signals
- `STATUS_APPLIED` - Emitted when a status effect is applied to an entity
- `STATUS_REMOVED` - Emitted when a status effect is removed
- `STATUS_TICK` - Emitted when status effects update (each turn)

#### UI Signals
- `UI_UPDATE_REQUESTED` - Emitted when UI needs to refresh
- `UI_ERROR` - Emitted when UI encounters an error
- `UI_ACTION` - Emitted when UI action is triggered (Hop 8)
- `UI_ACTION_SELECTED` - Emitted when specific UI action is selected (Hop 8)
- `SCREEN_CHANGED` - Emitted when UI screen transitions occur (Hop 8)

### SignalBus API
**Location**: `src/core/signals.py`

#### Core Methods
```python
# Subscription Management
listen(signal_type: CoreSignal, callback: Callable[[SignalData], None]) -> None
unlisten(signal_type: CoreSignal, callback: Callable[[SignalData], None]) -> bool

# Signal Emission
emit(signal_type: CoreSignal, source: str, data: Optional[Dict[str, Any]] = None) -> None

# Debugging & Monitoring
get_subscriber_count(signal_type: CoreSignal) -> int
get_signal_history(count: Optional[int] = None) -> List[SignalData]
clear_subscribers() -> None
clear_history() -> None
```

#### Global Access
```python
# Thread-safe singleton access
get_signal_bus() -> SignalBus
reset_signal_bus() -> None  # Testing only
```

#### SignalData Container
```python
@dataclass
class SignalData:
    signal_type: CoreSignal
    source: str               # Component that emitted signal
    data: Dict[str, Any]      # Payload data
    timestamp: float          # Emission timestamp
```

---

## Registry System

### BaseRegistry API
**Location**: `src/core/registry.py`

#### Abstract Base Class
All registries inherit from `BaseRegistry[T]` providing:

#### Core Methods
```python
# Data Access
get(item_id: str) -> Optional[T]
get_all() -> Dict[str, T]
exists(item_id: str) -> bool
get_all_ids() -> List[str]

# Lifecycle Management
initialize() -> None
reload() -> None
is_initialized() -> bool

# Signal Integration
_emit_signal(signal_type: CoreSignal, data: Dict[str, Any]) -> None
_handle_reload_signal(signal_data: SignalData) -> None
```

#### Abstract Methods (Must Implement)
```python
_load_item_from_dict(item_data: Dict[str, Any]) -> T
_get_data_directory() -> Path
_validate_item_data(item_data: Dict[str, Any]) -> bool  # Optional
```

### AbilityRegistry Implementation
**Location**: `src/game/abilities.py`

#### Data Classes
```python
@dataclass
class AbilityCost:
    ammo: int = 0
    mana: int = 0
    health: int = 0
    
    # Resource validation methods
    can_afford(current_ammo: int, current_mana: int, current_health: int) -> bool
    apply_cost(current_ammo: int, current_mana: int, current_health: int) -> tuple[int, int, int]

@dataclass
class AbilityEffects:
    damage: int = 0
    healing: int = 0
    defense_bonus: int = 0
    status_effects: List[str] = field(default_factory=list)

@dataclass
class Ability:
    name: str
    description: str
    cost: AbilityCost
    effects: AbilityEffects
    cooldown: int = 0
    damage_type: str = "physical"
```

#### Registry API
```python
class AbilityRegistry(BaseRegistry[Ability]):
    # Inherits all BaseRegistry methods
    # Data directory: data/abilities/
    # File format: JSON with ability definitions
```

### StateRegistry Implementation ✅ **NEW - Hop 3**
**Location**: `src/game/state_registry.py`

#### Data Classes
```python
@dataclass
class StatusEffect:
    id: str
    name: str
    description: str
    default_duration: int = 1
    max_stacks: int = 1
    conflicts: List[str] = field(default_factory=list)
    
    # Status effect validation and utility methods built-in
```

#### Registry API
```python
class StateRegistry(BaseRegistry[StatusEffect]):
    # Inherits all BaseRegistry methods
    # Data directory: data/status_effects/
    # File format: Individual JSON files per status effect
    
    def registry_name(self) -> str:
        return "State"
    
    def _get_data_directory(self) -> Path:
        return Path("data/status_effects")
    
    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> StatusEffect:
        # Creates StatusEffect dataclass from JSON data
        return StatusEffect(**item_data)
    
    def _get_item_id(self, item: StatusEffect) -> str:
        return item.id
```

#### Available Status Effects
Current status effects loaded from `data/status_effects/`:
- **stun.json**: Prevents actions (2 turns, conflicts with haste)
- **bleed.json**: Damage over time (3 turns, stacks to 5)
- **poison.json**: Damage over time (4 turns, stacks to 3)
- **slow.json**: Reduced speed (3 turns, conflicts with haste)
- **haste.json**: Increased speed (3 turns, conflicts with stun and slow)

#### Conflict Resolution
Status effects can define conflicts in their JSON:
```json
{
    "id": "haste",
    "name": "Hastened", 
    "description": "Increased movement and action speed",
    "default_duration": 3,
    "max_stacks": 1,
    "conflicts": ["stun", "slow"]
}
```

### BuffRegistry Implementation ✅ **NEW - Hop 4**
**Location**: `src/game/buff_registry.py`

#### Data Classes
```python
@dataclass
class Buff:
    id: str
    name: str
    description: str
    stat_modifiers: Dict[str, int] = field(default_factory=dict)
    default_duration: int = 1
    max_stacks: int = 1
    buff_type: str = "temporary"  # "temporary" or "permanent"
    is_permanent: bool = False
    
    # Built-in calculation methods
    def calculate_total_modifiers(self, stack_count: int) -> Dict[str, int]
    def can_stack_to(self, target_stacks: int) -> bool
```

#### Registry API
```python
class BuffRegistry(BaseRegistry[Buff]):
    # Inherits all BaseRegistry methods
    # Data directory: data/buffs/
    # File format: Individual JSON files per buff
    
    def _get_data_directory(self) -> Path:
        return Path("data/buffs")
    
    def _load_item_from_dict(self, item_data: Dict[str, Any]) -> Buff:
        # Creates Buff dataclass from JSON data
        return Buff(**item_data)
    
    def _get_item_id(self, item: Buff) -> str:
        return item.id
    
    # Specialized query methods
    def get_buffs_by_type(self, buff_type: str) -> List[Buff]
    def get_stat_modifying_buffs(self, stat_name: str) -> List[Buff]
    def get_temporary_buffs() -> List[Buff]
    def get_permanent_buffs() -> List[Buff]
```

#### Available Buffs
Current buffs loaded from `data/buffs/`:
- **rage.json**: +5 attack, -2 defense (3 turns, stacks to 2)
- **shield_wall.json**: +8 defense, -3 speed (5 turns, single stack)
- **combat_focus.json**: +3 speed, +2 accuracy (4 turns, stacks to 3)
- **combat_training.json**: +2 attack, +1 defense (permanent)
- **blessing.json**: +1 all stats, +5 health (10 turns, single stack)

#### Stat Modification System
Buffs modify stats via stat_modifiers dictionary:
```json
{
    "id": "rage",
    "name": "Rage",
    "description": "Increases attack power but reduces defense",
    "stat_modifiers": {
        "attack": 5,
        "defense": -2
    },
    "default_duration": 3,
    "max_stacks": 2
}
```

### EntityRegistry Implementation ✅ **NEW - Hop 5**

**Registry Name**: `"Entity"`  
**Signal Source**: `"EntityRegistry"`  
**Data Directory**: `data/entities/`  
**Item Type**: `Entity` dataclass

#### Entity Dataclass Structure
```python
@dataclass
class Entity:
    id: str
    name: str
    description: str
    entity_type: str  # "player", "normal", "elite", "boss"
    
    # Base stats
    base_health: int = 100
    base_attack: int = 10
    base_defense: int = 10
    base_speed: int = 10
    base_mana: int = 50
    
    # Behavioral properties
    flee_chance: float = 0.0
    is_boss: bool = False
    is_elite: bool = False
    immunities: List[str] = field(default_factory=list)
```

#### Registry API
- `get_entities_by_type(entity_type: str) -> List[Entity]` - Filter by type
- `get_entities_with_immunity(status_effect: str) -> List[Entity]` - Filter by immunity
- `get_bosses() -> List[Entity]` - Get all boss entities
- `get_elites() -> List[Entity]` - Get all elite entities  
- `get_player_entities() -> List[Entity]` - Get all player entities
- `get_enemies() -> List[Entity]` - Get all non-player entities

#### Available Entities
- **detective** (player) - Balanced stats, 60 mana, no immunities
- **street_thug** (normal) - Low health, basic combat, 30% flee chance
- **gang_lieutenant** (elite) - Enhanced stats, stun immunity, low flee chance
- **crime_boss** (boss) - High health/attack, never flees, stun/poison immune
- **corrupt_officer** (elite) - Balanced combat-trained stats, 20% flee chance

#### Stat Calculation System
Entities can calculate modified stats with buffs/debuffs:
```python
entity.calculate_stats({"attack": 5, "defense": -2})
# Returns: {"health": 100, "attack": 15, "defense": 8, "speed": 10, "mana": 50}
```

#### Flee Chance Mechanics
- Base flee chance when health > 50%
- Increased flee chance when health < 50% (up to +40% bonus)
- Bosses never flee regardless of health
- Formula: `flee_chance + (low_health_modifier * 0.4)`

---

## Component Integration

### Signal Flow Patterns

#### Registry Lifecycle
1. Registry created → `REGISTRY_INITIALIZED` emitted
2. Data loaded → Additional `REGISTRY_INITIALIZED` if successful
3. Hot-reload triggered → `REGISTRY_RELOADED` emitted
4. Error encountered → `REGISTRY_ERROR` emitted

#### Combat Flow (Planned)
1. Combat starts → `COMBAT_STARTED`
2. Each turn → `TURN_STARTED` → actions → `TURN_ENDED`
3. Abilities used → `ABILITY_USED` → cooldowns → `ABILITY_COOLDOWN_STARTED`
4. Status effects → `STATUS_APPLIED` → `STATUS_TICK` → `STATUS_REMOVED`
5. Combat ends → `COMBAT_ENDED`

### Thread Safety
- All signal operations are thread-safe with internal locking
- All registry operations are thread-safe with per-instance locking
- Global signal bus uses double-checked locking pattern

---

## Testing Infrastructure

### Signal Bus Tests
**Location**: `tests/test_signal_bus.py`
- 20 comprehensive tests covering all signal operations
- Thread safety validation
- Error handling verification
- Signal history functionality

### Registry Tests
**Location**: `tests/test_base_registry.py`
- 14 tests covering abstract registry functionality
- JSON loading validation
- Signal integration testing
- Error handling scenarios

### Integration Tests
- Cross-component signal communication
- Registry-to-registry communication via signals
- Full lifecycle testing from initialization to hot-reload

---

## Validation Checklist

### Pre-Release Validation
- [ ] All signals documented with purpose and data format
- [ ] All APIs have complete method signatures
- [ ] Thread safety documented for all components
- [ ] Integration patterns documented
- [ ] Test coverage confirmed for all new signals/APIs

### Post-Release Updates
- [ ] New signals added to CoreSignal enum
- [ ] New registry APIs documented
- [ ] Signal flow patterns updated
- [ ] Integration examples provided
- [ ] Version number updated

---

## Version History

### v0.0.2 (Hop 2: Signal Bus Foundation)
**Added:**
- Complete SignalBus system with 15 predefined signals
- BaseRegistry abstract class with signal integration
- AbilityRegistry implementation inheriting from BaseRegistry
- Thread-safe signal emission and subscription
- Signal history tracking for debugging
- Global signal bus singleton pattern

**APIs Implemented:**
- SignalBus: listen, unlisten, emit, get_subscriber_count, get_signal_history
- BaseRegistry: get, get_all, exists, get_all_ids, initialize, reload
- AbilityRegistry: full implementation with JSON loading

### v0.0.3 (Hop 3: StateRegistry) ✅ **NEW**
**Added:**
- StateRegistry system for status effects management
- StatusEffect dataclass with conflict resolution
- Enhanced BaseRegistry to support single-object JSON files
- 5 status effects: stun, bleed, poison, slow, haste
- Comprehensive test suite (13 StateRegistry tests)
- Virtual environment setup with pytest integration
- VSCode tasks configuration for venv

**APIs Implemented:**
- StateRegistry: inherits BaseRegistry, adds status effect management
- StatusEffect: dataclass for status effect definitions
- Enhanced BaseRegistry: supports individual JSON files (not just arrays)
- JSON conflict resolution: status effects can define conflicting effects

**Workflow Improvements:**
- JSON loading bug identified and fixed in BaseRegistry
- VSCode task configuration automated for virtual environment
- Test-first development caught integration issues early
- Systematic debugging approach for complex data loading issues

### v0.0.4 (Hop 4: BuffRegistry) ✅ **NEW**
**Added:**
- BuffRegistry system for stat modification effects
- Buff dataclass with stacking and calculation methods  
- 5 buff types: rage, shield_wall, combat_focus, combat_training, blessing
- Temporary vs permanent buff support
- Enhanced game launcher with multi-registry testing
- Comprehensive test suite (14 BuffRegistry tests)
- Signal integration with real signal bus testing

**APIs Implemented:**
- BuffRegistry: inherits BaseRegistry, adds buff-specific query methods
- Buff: dataclass with stat modification calculations and stacking validation
- Specialized queries: get_buffs_by_type, get_stat_modifying_buffs
- Stat modification system: flexible JSON-based stat changes

**Workflow Improvements:**
- Test-first development approach proved highly effective
- Real signal bus testing approach better than mocking for integration
- Enhanced game launcher validates all registries automatically
- BaseRegistry pattern enables rapid new registry development
- Individual JSON file approach scales well for diverse content types

### v0.0.5 (Hop 5: EntityRegistry) ✅ **NEW**
**Added:**
- EntityRegistry system for character and enemy data management
- Entity dataclass with stat calculations and flee chance mechanics
- 5 entity types: detective, street_thug, gang_lieutenant, crime_boss, corrupt_officer
- Entity classification system (player, normal, elite, boss)
- Immunity system for status effects
- Stat modification support with buff/debuff calculations
- Comprehensive test suite (14 EntityRegistry tests)
- Enhanced game launcher now validates all three registries

**APIs Implemented:**
- EntityRegistry: inherits BaseRegistry, adds entity-specific query methods
- Entity: dataclass with stat calculations, flee chance mechanics, immunity checks
- Specialized queries: get_entities_by_type, get_entities_with_immunity, get_bosses, get_elites
- Stat calculation system: supports modifiers from buffs/debuffs
- Flee chance mechanics: health-based calculations with boss immunity

**Workflow Improvements:**
- Enhanced workflow with 5-phase approach continues to be highly effective
- Real signal bus testing proved valuable again for entity registry
- BaseRegistry pattern enabled EntityRegistry development in ~3 hours
- JSON individual file approach scales perfectly for entity variety
- Game launcher auto-validation catches integration issues immediately
- Test coverage now at 98/98 tests (expanded from 84/84)

---

## Workflow Improvement Log

### Hop 3 Lessons Learned
**What Worked Well:**
- Test-first development caught JSON loading issues immediately
- BaseRegistry pattern made StateRegistry implementation straightforward
- Virtual environment setup prevented dependency conflicts
- Systematic debugging with targeted testing isolated issues quickly

**Bottlenecks Identified:**
- BaseRegistry only supported array/nested JSON, not single objects
- VSCode tasks needed manual configuration for virtual environment
- JSON loading failure was silent until tests revealed the issue
- Manual test execution required due to task configuration

**Tool Gaps:**
- Need automated venv detection in VSCode tasks
- JSON schema validation would catch data issues earlier
- Better error messages for registry loading failures
- Hot-reload testing during development would speed iteration

**Process Improvements Made:**
- Enhanced BaseRegistry._load_json_file to handle single objects
- Updated all VSCode tasks to use virtual environment Python
- Added comprehensive JSON loading tests to BaseRegistry
- Documented workflow improvement process in agent prompt

### Hop 4 Lessons Learned
**What Worked Well:**
- Test-first development caught JSON structure issues immediately
- BaseRegistry pattern made BuffRegistry implementation straightforward in ~2 hours
- Real signal bus testing revealed actual integration patterns vs mocking
- Enhanced game launcher provides instant validation of new registries
- Individual JSON file approach enables easy content expansion

**Bottlenecks Identified:**
- Manual signal test conversion from mocking to real testing took extra time
- Registry constructor parameter differences caused initial test failures
- Game launcher needed manual updates for each new registry
- JSON data structure documentation could be more comprehensive

**Tool Gaps:**
- Need automated signal test generation for new registries
- Registry constructor patterns should be more consistent
- Game launcher should auto-discover and test all registries
- JSON schema documentation generation would help content creators

**Process Improvements Made:**
- Established real signal bus testing as standard practice
- Enhanced game launcher now validates all registries automatically
- Updated BaseRegistry pattern documentation for consistency
- Added comprehensive buff stat calculation system with validation

**Future Enhancements:**
- Add JSON schema validation for all data files
- Implement hot-reload testing during development
- Create development task automation scripts
- Add automated venv setup in project initialization
- Auto-discovery system for registries in game launcher
- Automated signal test template generation for new registries

**Test Coverage:**
- 98/98 tests passing
- Signal bus: 20 tests
- Base registry: 14 tests  
- Ability registry: 15 tests
- State registry: 13 tests
- Buff registry: 14 tests
- Entity registry: 14 tests
- Integration testing: 8 tests

---

## Future Updates

### Hop 3: StateRegistry (Status Effects)
**Planned Signals:**
- Enhanced STATUS_* signals with duration data
- New STATE_EXPIRED signal for duration-based effects
- STACK_CONFLICT signal for status effect conflicts

**Planned APIs:**
- StateRegistry class implementing BaseRegistry[StatusEffect]
- Duration tracking methods
- Stack/conflict resolution APIs
- Integration with combat turn system

### Hop 4: BuffRegistry (Positive Effects)
**Planned Signals:**
- BUFF_APPLIED, BUFF_REMOVED, BUFF_STACKED
- BUFF_CAP_REACHED for stacking limits

**Planned APIs:**
- BuffRegistry class with stacking calculations
- Integration methods with StateRegistry
- Conflict resolution between buffs and debuffs

---

## Main UI Framework (Hop 8)

### MainUI System
**Location**: `src/ui/main_ui.py`

#### Core Components
- **MainUI**: Primary UI framework class with tcod rendering
- **MenuScreen**: Screen container with title, options, status, and content
- **MenuOption**: Individual menu option with key, text, action, and state
- **StatusData**: Game status information (location, gold, time, health, etc.)
- **InputHandler**: Keyboard input processing and action mapping
- **UIConfig**: UI configuration (dimensions, colors, border styles)

#### MainUI API
```python
# Initialization
__init__(config: Optional[UIConfig] = None) -> None
initialize() -> None

# Screen Management  
set_screen(screen: MenuScreen) -> None
push_screen(screen: MenuScreen) -> None
pop_screen() -> Optional[MenuScreen]

# Status Management
update_status(status_data: StatusData) -> None

# Main Loop
run_main_loop() -> None
render() -> None
handle_input() -> Optional[str]

# Input Processing
process_input(key: str) -> Optional[str]
process_action(action: str) -> bool
```

#### MenuScreen API
```python
# Constructor (flexible)
__init__(title: str, arg2=None, arg3=None, status=None, description="", options=None)

# Content Management
add_option(option: MenuOption) -> None
add_content_line(line: str) -> None
clear_content() -> None

# Option Access
get_option(key: str) -> Optional[MenuOption]
get_option_by_key(key: str) -> Optional[MenuOption]
get_enabled_options() -> List[MenuOption]
```

#### UI Integration Features
- **Signal Bus Integration**: Emits UI_ACTION, UI_ACTION_SELECTED, SCREEN_CHANGED
- **tcod Rendering**: Professional ASCII borders, multi-section layout
- **Test-Friendly**: Fallback print rendering for headless testing
- **Screen Stacking**: Push/pop screen management for navigation
- **Flexible Constructors**: Support multiple calling patterns for compatibility

### UI Layout Structure
```
╔═══════════════════════════════════════════════════════════════════╗
║ Status Header: Location, Gold, Time, Day, HP, Mana, Ammo         ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  Main Content Area: Screen description and content lines         ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║ Menu Options: 1-9 numbered selections with actions               ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## Maintenance Notes

### Signal Bus Maintenance
- Monitor signal_history size (current max: 1000)
- Watch for subscriber memory leaks
- Validate signal payloads match expected formats

### Registry Maintenance  
- Ensure JSON schema validation remains strict
- Monitor hot-reload performance
- Watch for thread contention in high-frequency registries

### Integration Maintenance
- Test signal emission under high load
- Validate cross-registry communication patterns
- Monitor for circular signal dependencies

---

**Document Maintainer**: GitHub Copilot  
**Update Frequency**: After each hop completion during final validation  
**Next Scheduled Update**: Hop 3 completion
