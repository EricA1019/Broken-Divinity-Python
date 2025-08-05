# SQLite-First Development Workflow

**Version:** v0.0.12  
**Date:** 2025-08-05  
**Author:** Eric Acosta  

## Overview

Broken Divinity now uses a **SQLite-first development workflow** where:
- **SQLite database** (`data/game.db`) is the primary data store
- **JSON files** (`data/test_data/`) are used for testing and development
- **Registry abstraction** provides unified access to both data sources
- **Migration tools** promote tested JSON content to the database

## Development Workflow

### 1. Content Development Phase
**Location:** `data/test_data/`

```bash
# Create new content in JSON format for rapid iteration
data/test_data/
├── entities/
│   ├── new_character.json
│   └── test_enemies.json
├── abilities/
│   ├── new_spells.json
│   └── detective_skills.json
└── locations/
    ├── new_areas.json
    └── test_dungeons.json
```

**Benefits:**
- Fast iteration with JSON editing
- Easy version control tracking
- Human-readable content format
- Simple testing and validation

### 2. Testing and Validation Phase
**Tools:** VS Code Tasks, pytest

```bash
# Test with JSON backend
python -m pytest tests/unit/test_backend.py::TestJSONDataBackend -v

# Validate JSON schemas
python -c "from src.data.migrations import JSONMigrator; # validation code"

# Test game functionality with JSON data
python -m src.main  # Uses JSON backend during development
```

**Tasks Available:**
- `Test: All` - Run complete test suite
- `Test: Unit` - Unit tests only
- `Database: Validate` - Check database integrity

### 3. Migration to Production Phase
**Tools:** Migration scripts, Database tasks

```bash
# Migrate tested JSON to SQLite
Ctrl+Shift+P → "Tasks: Run Task" → "Database: Migrate JSON"

# Or manually:
python -c "
from src.data.migrations import migrate_json_to_sqlite
migrate_json_to_sqlite('data/test_data', 'data/game.db')
"
```

**Validation:**
```bash
# Test with SQLite backend
python -m pytest tests/unit/test_backend.py::TestSQLiteDataBackend -v

# Validate database
Ctrl+Shift+P → "Tasks: Run Task" → "Database: Validate"

# Test game with database
python -m src.main  # Uses SQLite backend in production
```

### 4. Backup and Maintenance Phase
**Tools:** Export scripts, Backup tasks

```bash
# Export database to JSON for backup
Ctrl+Shift+P → "Tasks: Run Task" → "Database: Export JSON"

# Reset database (development only)
Ctrl+Shift+P → "Tasks: Run Task" → "Database: Reset"
```

## VS Code Integration

### Available Tasks
**Testing Tasks:**
- `Test: All` - Complete test suite
- `Test: Unit` - Unit tests only  
- `Test: Integration` - Integration tests
- `Test: Smoke` - Critical path tests
- `Test: Game Flow` - User journey tests
- `Test: Pre-Commit` - Pre-commit validation

**Database Tasks:**
- `Database: Initialize` - Create fresh database
- `Database: Migrate JSON` - Import test_data to database
- `Database: Export JSON` - Export database to backup
- `Database: Validate` - Check database integrity
- `Database: Reset` - Wipe and recreate database

**Build Tasks:**
- `Build: Game` - Build and run game
- `Format Code` - Apply Black formatting

### Environment Variables
Automatically set in VS Code terminal:
```bash
PYTHONPATH="${workspaceFolder}/src"
BD_DB_PATH="${workspaceFolder}/data/game.db"
BD_TEST_DATA_PATH="${workspaceFolder}/data/test_data"
```

## Data Backend Abstraction

### Registry Usage
```python
from src.data.backend import DataBackendFactory

# Development with JSON
json_backend = DataBackendFactory.create_backend("json", data_root="data/test_data")
registry = SomeRegistry(backend=json_backend)

# Production with SQLite  
sqlite_backend = DataBackendFactory.create_backend("sqlite", db_path="data/game.db")
registry = SomeRegistry(backend=sqlite_backend)

# Unified API regardless of backend
entity = registry.get("PlayerCharacter")
abilities = registry.get_all_by_type("offensive")
```

### Configuration-Based Switching
```python
# In main.py or config
import os

backend_type = os.getenv("BD_BACKEND", "sqlite")  # Default to SQLite
data_path = os.getenv("BD_DB_PATH", "data/game.db")

if backend_type == "json":
    data_path = os.getenv("BD_TEST_DATA_PATH", "data/test_data")

backend = DataBackendFactory.create_backend(backend_type, 
                                          db_path=data_path if backend_type == "sqlite" else None,
                                          data_root=data_path if backend_type == "json" else None)
```

## Best Practices

### Content Development
1. **Start with JSON** - Create content in `data/test_data/`
2. **Test incrementally** - Validate each JSON file
3. **Use schemas** - Ensure JSON matches expected structure
4. **Version control** - Track JSON changes in git
5. **Migrate when stable** - Only promote tested content

### Database Management
1. **Regular backups** - Export to JSON before major changes
2. **Schema versioning** - Track database schema changes
3. **Migration testing** - Test migrations on copies first
4. **Rollback capability** - Keep JSON backups for rollback
5. **Performance monitoring** - Watch query performance

### Testing Strategy
1. **Test both backends** - Ensure JSON and SQLite compatibility
2. **Integration tests** - Test registry abstraction layer
3. **Migration tests** - Validate JSON → SQLite conversion
4. **Performance tests** - Compare backend performance
5. **Data integrity tests** - Verify data consistency

## File Organization

### Directory Structure
```
data/
├── game.db                    # Primary SQLite database
├── backup/                    # JSON exports from database
│   ├── entities.json
│   ├── abilities.json
│   └── locations.json
├── migrations/               # Database schema migrations
│   ├── 001_initial_schema.sql
│   └── 002_add_relationships.sql
└── test_data/               # JSON files for development
    ├── entities/
    │   ├── player_character.json
    │   └── test_enemies.json
    ├── abilities/
    │   ├── detective_abilities.json
    │   └── combat_abilities.json
    └── locations/
        ├── apartment_complex.json
        └── downtown_areas.json
```

### File Naming Conventions
- **Database:** `game.db` (primary), `test.db` (testing)
- **JSON Test Data:** `{content_type}/{descriptive_name}.json`
- **JSON Backups:** `{table_name}.json` (matches database tables)
- **Migrations:** `{number}_{description}.sql`

## Troubleshooting

### Common Issues
1. **Backend mismatch** - Check environment variables
2. **Missing data** - Verify migration completed
3. **Schema errors** - Check database version
4. **Performance issues** - Consider indexes and query optimization
5. **Test failures** - Ensure both backends have same data

### Debug Commands
```bash
# Check database status
python -c "from src.data.database import DatabaseManager; db = DatabaseManager(); db.validate()"

# Check backend configuration
python -c "from src.data.backend import DataBackendFactory; print(DataBackendFactory.create_backend('sqlite'))"

# Compare JSON vs SQLite data
python -c "
from src.data.backend import JSONDataBackend, SQLiteDataBackend
json_backend = JSONDataBackend('data/test_data')
sqlite_backend = SQLiteDataBackend('data/game.db')
print('JSON entities:', len(json_backend.get_all_items('entities')))
print('SQLite entities:', len(sqlite_backend.get_all_items('entities')))
"
```

---

This workflow enables rapid content development while maintaining production database performance and reliability.
