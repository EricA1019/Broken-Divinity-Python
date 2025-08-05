"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  JSON to SQLite Migration Utilities                                         ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Convert existing JSON data files to SQLite database        ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.12                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
import os

from src.data.database import DatabaseManager, DatabaseError
from src.utils.logging import Log


class JSONMigrator:
    """Migrates JSON data files to SQLite database."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize migrator with database manager."""
        self.tag = "JSONMigrator"
        self.db_manager = db_manager
        Log.p(self.tag, ["JSON migrator initialized"])

    def migrate_all_json_data(self, data_root: str = "data") -> None:
        """Migrate all JSON data from file system to database."""
        data_path = Path(data_root)
        if not data_path.exists():
            Log.p(self.tag, [f"Data directory not found: {data_root}"])
            return

        Log.p(self.tag, [f"Starting migration from {data_root}"])

        # Migration order matters due to relationships
        migration_order = [
            ("entities", "entity_type"),
            ("abilities", "ability_type"),
            ("status_effects", "effect_type"),
            ("buffs", "buff_type"),
            ("suffixes", "applies_to"),
            ("locations", "location_type"),
        ]

        for folder_name, type_field in migration_order:
            folder_path = data_path / folder_name
            if folder_path.exists():
                count = self._migrate_folder(folder_path, folder_name, type_field)
                Log.p(self.tag, [f"Migrated {count} {folder_name} from JSON"])

        # Migrate relationships
        self._migrate_entity_abilities()

        Log.p(self.tag, ["JSON migration completed"])

    def _migrate_folder(
        self, folder_path: Path, table_name: str, type_field: str
    ) -> int:
        """Migrate all JSON files in a folder to a database table."""
        if not self.db_manager.connection:
            raise DatabaseError("No database connection")

        count = 0
        cursor = self.db_manager.connection.cursor()

        # Find all JSON files recursively
        for json_file in folder_path.rglob("*.json"):
            try:
                items = self._load_json_file(json_file)

                for item in items:
                    # Validate required fields
                    if "name" not in item:
                        Log.p(self.tag, [f"Skipping item without name in {json_file}"])
                        continue

                    # Determine type from folder structure or data
                    item_type = self._determine_item_type(item, json_file, type_field)

                    # Insert into database
                    self._insert_item(cursor, table_name, item, item_type, type_field)
                    count += 1

            except Exception as e:
                Log.p(self.tag, [f"ERROR migrating {json_file}: {e}"])

        self.db_manager.connection.commit()
        return count

    def _load_json_file(self, json_file: Path) -> List[Dict[str, Any]]:
        """Load and parse a JSON file, handling different formats."""
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle different JSON formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if "items" in data:
                return data["items"]
            else:
                # Single item format
                return [data]
        else:
            Log.p(self.tag, [f"Unknown JSON format in {json_file}"])
            return []

    def _determine_item_type(
        self, item: Dict[str, Any], json_file: Path, type_field: str
    ) -> str:
        """Determine the type/category of an item."""
        # First check if item has explicit type field
        if type_field in item:
            return str(item[type_field])

        # Infer from filename
        filename = json_file.stem
        if filename.endswith("_abilities"):
            return "ability"
        elif filename.endswith("_entities"):
            return "entity"
        elif filename.endswith("_effects"):
            return "status_effect"

        # Infer from parent directory
        parent_name = json_file.parent.name
        type_mapping = {
            "entities": "entity",
            "abilities": "ability",
            "status_effects": "status_effect",
            "buffs": "buff",
            "suffixes": "suffix",
            "locations": "location",
        }

        return type_mapping.get(parent_name, "unknown")

    def _insert_item(
        self,
        cursor: sqlite3.Cursor,
        table_name: str,
        item: Dict[str, Any],
        item_type: str,
        type_field: str,
    ) -> None:
        """Insert an item into the appropriate database table."""
        name = item["name"]
        data_json = json.dumps(item, indent=2)

        # Build insert query based on table
        if table_name == "entities":
            cursor.execute(
                """
                INSERT OR REPLACE INTO entities (name, data, entity_type) 
                VALUES (?, ?, ?)
            """,
                (name, data_json, item_type),
            )

        elif table_name == "abilities":
            mana_cost = item.get("mana_cost", 0)
            cursor.execute(
                """
                INSERT OR REPLACE INTO abilities (name, data, ability_type, mana_cost) 
                VALUES (?, ?, ?, ?)
            """,
                (name, data_json, item_type, mana_cost),
            )

        elif table_name == "status_effects":
            duration = item.get("duration", -1)
            cursor.execute(
                """
                INSERT OR REPLACE INTO status_effects (name, data, effect_type, duration) 
                VALUES (?, ?, ?, ?)
            """,
                (name, data_json, item_type, duration),
            )

        elif table_name == "buffs":
            cursor.execute(
                """
                INSERT OR REPLACE INTO buffs (name, data, buff_type) 
                VALUES (?, ?, ?)
            """,
                (name, data_json, item_type),
            )

        elif table_name == "suffixes":
            applies_to = item.get("applies_to", "unknown")
            cursor.execute(
                """
                INSERT OR REPLACE INTO suffixes (name, data, applies_to) 
                VALUES (?, ?, ?)
            """,
                (name, data_json, applies_to),
            )

        elif table_name == "locations":
            cursor.execute(
                """
                INSERT OR REPLACE INTO locations (name, data, location_type) 
                VALUES (?, ?, ?)
            """,
                (name, data_json, item_type),
            )

    def _migrate_entity_abilities(self) -> None:
        """Migrate entity-ability relationships."""
        if not self.db_manager.connection:
            return

        cursor = self.db_manager.connection.cursor()

        # Get all entities and check for abilities
        cursor.execute("SELECT name, data FROM entities")
        entities = cursor.fetchall()

        for entity_row in entities:
            entity_name = entity_row["name"]
            entity_data = json.loads(entity_row["data"])

            # Look for abilities in entity data
            abilities = entity_data.get("abilities", [])
            if isinstance(abilities, str):
                abilities = [abilities]

            for ability_name in abilities:
                # Check if ability exists in database
                cursor.execute(
                    "SELECT name FROM abilities WHERE name = ?", (ability_name,)
                )
                if cursor.fetchone():
                    # Insert relationship
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO entity_abilities (entity_name, ability_name) 
                        VALUES (?, ?)
                    """,
                        (entity_name, ability_name),
                    )

        self.db_manager.connection.commit()
        Log.p(self.tag, ["Entity-ability relationships migrated"])

    def export_to_json(self, output_dir: str = "data/backup") -> None:
        """Export database content back to JSON files for backup/development."""
        if not self.db_manager.connection:
            raise DatabaseError("No database connection")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        cursor = self.db_manager.connection.cursor()

        # Export each table
        tables = [
            "entities",
            "abilities",
            "status_effects",
            "buffs",
            "suffixes",
            "locations",
        ]

        for table in tables:
            cursor.execute(f"SELECT name, data FROM {table}")
            rows = cursor.fetchall()

            if rows:
                items = []
                for row in rows:
                    item_data = json.loads(row["data"])
                    items.append(item_data)

                # Write to JSON file
                output_file = output_path / f"{table}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(items, f, indent=2, ensure_ascii=False)

                Log.p(self.tag, [f"Exported {len(items)} {table} to {output_file}"])

        Log.p(self.tag, [f"Database exported to JSON in {output_dir}"])


def migrate_json_to_sqlite(
    data_root: str = "data", db_path: str = "data/game.db"
) -> None:
    """Convenience function to migrate all JSON data to SQLite."""
    db_manager = DatabaseManager(db_path)

    try:
        db_manager.initialize()
        migrator = JSONMigrator(db_manager)
        migrator.migrate_all_json_data(data_root)

        Log.p("Migration", ["JSON to SQLite migration completed successfully"])

    except Exception as e:
        Log.p("Migration", [f"ERROR: Migration failed: {e}"])
        raise
    finally:
        db_manager.close()


# EOF
