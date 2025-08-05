# Broken Divinity - Database Schema Documentation

**Version:** v0.0.12  
**Date:** 2025-08-05  
**Author:** Eric Acosta  

## Schema Overview

Broken Divinity uses SQLite as the primary data store with JSON compatibility for testing and development. The database provides relational data capabilities while maintaining the flexibility of JSON content within each record.

## Core Tables

### 1. Entities Table
**Purpose:** All game entities (players, NPCs, enemies, items)

```sql
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,                -- JSON blob with entity details
    entity_type TEXT NOT NULL,         -- 'player', 'enemy', 'npc', 'item'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_entities_name` ON entities(name)
- `idx_entities_type` ON entities(entity_type)

### 2. Abilities Table
**Purpose:** All player and entity abilities

```sql
CREATE TABLE IF NOT EXISTS abilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,                -- JSON blob with ability details
    ability_type TEXT NOT NULL,        -- 'offensive', 'defensive', 'supportive'
    mana_cost INTEGER DEFAULT 0,       -- Extracted for efficient queries
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_abilities_name` ON abilities(name)
- `idx_abilities_type` ON abilities(ability_type)
- `idx_abilities_mana` ON abilities(mana_cost)

### 3. Status Effects Table
**Purpose:** Temporary effects applied to entities

```sql
CREATE TABLE IF NOT EXISTS status_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,                -- JSON blob with effect details
    effect_type TEXT NOT NULL,         -- 'damage', 'heal', 'buff', 'debuff'
    duration INTEGER DEFAULT -1,       -- -1 for permanent, 0+ for turns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_status_effects_name` ON status_effects(name)
- `idx_status_effects_type` ON status_effects(effect_type)
- `idx_status_effects_duration` ON status_effects(duration)

### 4. Buffs Table
**Purpose:** Positive temporary effects

```sql
CREATE TABLE IF NOT EXISTS buffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,                -- JSON blob with buff details
    buff_type TEXT NOT NULL,           -- 'stat', 'ability', 'special'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_buffs_name` ON buffs(name)
- `idx_buffs_type` ON buffs(buff_type)

### 5. Suffixes Table
**Purpose:** Procedural generation modifiers

```sql
CREATE TABLE IF NOT EXISTS suffixes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,                -- JSON blob with suffix details
    applies_to TEXT NOT NULL,          -- 'weapon', 'armor', 'consumable', 'entity'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_suffixes_name` ON suffixes(name)
- `idx_suffixes_applies_to` ON suffixes(applies_to)

### 6. Locations Table
**Purpose:** Game world locations and areas

```sql
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,                -- JSON blob with location details
    location_type TEXT NOT NULL,       -- 'room', 'area', 'dungeon', 'world'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_locations_name` ON locations(name)
- `idx_locations_type` ON locations(location_type)

## Relationship Tables

### 7. Entity Abilities Table
**Purpose:** Many-to-many relationship between entities and their abilities

```sql
CREATE TABLE IF NOT EXISTS entity_abilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_name TEXT NOT NULL,
    ability_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_name) REFERENCES entities(name) ON DELETE CASCADE,
    FOREIGN KEY (ability_name) REFERENCES abilities(name) ON DELETE CASCADE,
    UNIQUE(entity_name, ability_name)
);
```

**Indexes:**
- `idx_entity_abilities_entity` ON entity_abilities(entity_name)
- `idx_entity_abilities_ability` ON entity_abilities(ability_name)

## Schema Management

### Version Tracking
```sql
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR REPLACE INTO schema_version (version, description) 
VALUES (1, 'Initial schema with core game tables');
```

### Database Triggers
**Update Timestamps:**
```sql
-- Auto-update timestamps on record changes
CREATE TRIGGER IF NOT EXISTS update_entities_timestamp 
    AFTER UPDATE ON entities
BEGIN
    UPDATE entities SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Similar triggers for all other tables...
```

## JSON Data Structure Examples

### Entity JSON Structure
```json
{
    "name": "PlayerCharacter",
    "entity_type": "player",
    "health": 100,
    "max_health": 100,
    "mana": 50,
    "max_mana": 50,
    "stats": {
        "strength": 15,
        "dexterity": 12,
        "intelligence": 18,
        "constitution": 14
    },
    "abilities": ["BasicAttack", "Heal", "Investigate"],
    "inventory": [],
    "location": "PlayerApartment",
    "description": "A determined detective seeking truth in a broken world."
}
```

### Ability JSON Structure
```json
{
    "name": "Investigate",
    "ability_type": "detective",
    "mana_cost": 10,
    "description": "Examine the environment for clues and hidden details.",
    "effects": {
        "type": "skill_check",
        "difficulty": "medium",
        "success_text": "You notice something important...",
        "failure_text": "Nothing seems out of the ordinary."
    },
    "cooldown": 0,
    "requirements": {
        "min_level": 1,
        "required_stats": {"intelligence": 10}
    }
}
```

### Location JSON Structure
```json
{
    "name": "PlayerApartment",
    "location_type": "room",
    "title": "Your Apartment",
    "description": "A modest one-bedroom apartment...",
    "ascii_art": "apartment_layout.txt",
    "connections": {
        "1": {"destination": "ApartmentHallway", "text": "Leave apartment"},
        "2": {"destination": "ApartmentBedroom", "text": "Go to bedroom"}
    },
    "items": [],
    "npcs": [],
    "events": []
}
```

## Query Patterns

### Common Queries
```sql
-- Get all offensive abilities with mana cost <= 20
SELECT name, data FROM abilities 
WHERE ability_type = 'offensive' AND mana_cost <= 20;

-- Get entity with all their abilities
SELECT e.name, e.data, GROUP_CONCAT(a.name) as abilities
FROM entities e
LEFT JOIN entity_abilities ea ON e.name = ea.entity_name
LEFT JOIN abilities a ON ea.ability_name = a.name
WHERE e.name = 'PlayerCharacter'
GROUP BY e.name;

-- Find all locations of a specific type
SELECT name, data FROM locations 
WHERE location_type = 'dungeon'
ORDER BY name;
```

### Performance Optimizations
- All primary lookup fields (name) are indexed
- Type fields are indexed for filtering
- Numeric fields (mana_cost, duration) are indexed for range queries
- Foreign key relationships use appropriate indexes

## Migration Strategy

### JSON to SQLite Migration
1. **Scan existing JSON files** in `data/` directory structure
2. **Parse and validate** JSON content against schemas
3. **Extract key fields** for database columns (type, mana_cost, etc.)
4. **Store full JSON** in data column for flexibility
5. **Create relationships** from JSON array fields (entity abilities)
6. **Validate integrity** after migration

### Backup and Export
- **Automatic backups** before schema changes
- **JSON export capability** for development and testing
- **Migration rollback** support for schema versioning

## Development Workflow Integration

### Testing Strategy
- **JSON files** used for test data development
- **In-memory SQLite** for unit tests
- **File-based SQLite** for integration tests
- **Backup/restore** for test data consistency

### Data Backend Abstraction
- **Unified Registry API** works with both JSON and SQLite
- **Automatic fallback** from SQLite to JSON during development
- **Migration tools** for promoting JSON to SQLite
- **Export tools** for backing up SQLite to JSON

---

**Note:** This schema supports the game's evolution from simple JSON-based data to a full relational database while maintaining backward compatibility and development flexibility.
