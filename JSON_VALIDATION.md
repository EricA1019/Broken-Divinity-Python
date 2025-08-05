# JSON Validation System

## Overview
The JSON validation system ensures all data files conform to schemas before development begins. This prevents runtime errors and maintains data consistency across the project.

## Usage

### Validate All JSON Files
```bash
python validate_json.py
```

### Using with Virtual Environment
```bash
.venv/bin/python validate_json.py
```

## Schema Files
- `schemas/abilities_schema.json` - Abilities and skill definitions
- `schemas/status_effects_schema.json` - Status effects and buffs/debuffs

## Template Files
- `templates/ability_template.json` - Template for new abilities
- `templates/status_effect_template.json` - Template for new status effects

## Workflow Integration
JSON validation is **Step 2** of the enhanced Close-to-Shore workflow:
1. Hop Planning & Setup
2. **JSON Template Validation** ← Run validation here
3. Test-First Implementation
4. Integration & System Validation
5. Player Experience Testing
6. Documentation & Commit

## Exit Codes
- `0` - All files validate successfully
- `1` - Validation errors found

## Schema Validation Rules
- All required fields must be present
- Field types must match schema definitions
- Enum values must be from allowed lists
- Additional properties handled per schema
