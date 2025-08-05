"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Data Backend Abstraction Layer                                             ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Unified interface for JSON and SQLite data backends        ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.12                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Iterator

from src.data.database import DatabaseManager, DatabaseError
from src.utils.logging import Log


class DataBackend(ABC):
    """Abstract base class for data backends."""

    @abstractmethod
    def get_item(self, table: str, name: str) -> Optional[Dict[str, Any]]:
        """Get a single item by name."""
        pass

    @abstractmethod
    def get_all_items(
        self, table: str, item_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all items from a table, optionally filtered by type."""
        pass

    @abstractmethod
    def save_item(self, table: str, name: str, data: Dict[str, Any]) -> None:
        """Save an item to the backend."""
        pass

    @abstractmethod
    def delete_item(self, table: str, name: str) -> bool:
        """Delete an item from the backend."""
        pass

    @abstractmethod
    def search_items(self, table: str, **filters) -> List[Dict[str, Any]]:
        """Search items with filters."""
        pass

    @abstractmethod
    def get_relationships(
        self, primary_table: str, secondary_table: str, primary_name: str
    ) -> List[str]:
        """Get related items (e.g., entity abilities)."""
        pass


class JSONDataBackend(DataBackend):
    """JSON file-based data backend for compatibility."""

    def __init__(self, data_root: str = "data"):
        """Initialize JSON backend."""
        self.tag = "JSONBackend"
        self.data_root = Path(data_root)
        self._cache: Dict[str, Dict[str, Dict[str, Any]]] = {}
        Log.p(self.tag, [f"JSON backend initialized with root: {data_root}"])

    def _load_table_data(self, table: str) -> Dict[str, Dict[str, Any]]:
        """Load and cache data for a table."""
        if table in self._cache:
            return self._cache[table]

        table_data = {}
        table_path = self.data_root / table

        if table_path.exists():
            # Load all JSON files in the table directory
            for json_file in table_path.rglob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Handle different JSON formats
                    items = []
                    if isinstance(data, list):
                        items = data
                    elif isinstance(data, dict):
                        if "items" in data:
                            items = data["items"]
                        else:
                            items = [data]

                    # Index by name
                    for item in items:
                        if "name" in item:
                            table_data[item["name"]] = item

                except Exception as e:
                    Log.p(self.tag, [f"ERROR loading {json_file}: {e}"])

        self._cache[table] = table_data
        return table_data

    def get_item(self, table: str, name: str) -> Optional[Dict[str, Any]]:
        """Get a single item by name."""
        table_data = self._load_table_data(table)
        return table_data.get(name)

    def get_all_items(
        self, table: str, item_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all items from a table, optionally filtered by type."""
        table_data = self._load_table_data(table)
        items = list(table_data.values())

        if item_type:
            # Filter by type field
            type_field = self._get_type_field(table)
            items = [item for item in items if item.get(type_field) == item_type]

        return items

    def save_item(self, table: str, name: str, data: Dict[str, Any]) -> None:
        """Save an item to the backend."""
        # For JSON backend, this would save to a file
        # For now, just update cache (could implement file writing)
        if table not in self._cache:
            self._load_table_data(table)

        self._cache[table][name] = data
        Log.p(self.tag, [f"Saved {name} to {table} (cache only)"])

    def delete_item(self, table: str, name: str) -> bool:
        """Delete an item from the backend."""
        if table not in self._cache:
            self._load_table_data(table)

        if name in self._cache[table]:
            del self._cache[table][name]
            Log.p(self.tag, [f"Deleted {name} from {table}"])
            return True
        return False

    def search_items(self, table: str, **filters) -> List[Dict[str, Any]]:
        """Search items with filters."""
        items = self.get_all_items(table)

        for key, value in filters.items():
            items = [item for item in items if item.get(key) == value]

        return items

    def get_relationships(
        self, primary_table: str, secondary_table: str, primary_name: str
    ) -> List[str]:
        """Get related items (e.g., entity abilities)."""
        primary_item = self.get_item(primary_table, primary_name)
        if not primary_item:
            return []

        # Look for relationship fields - try various naming patterns
        # Handle the special case where "abilities" -> "ability"
        if secondary_table == "abilities":
            singular_form = "ability"
        elif secondary_table.endswith("ies"):
            singular_form = secondary_table[:-3] + "y"  # "abilities" -> "ability"
        elif secondary_table.endswith("s"):
            singular_form = secondary_table[:-1]  # "items" -> "item"
        else:
            singular_form = secondary_table

        relationship_fields = [
            secondary_table,  # "abilities"
            singular_form,  # "ability"
            f"{secondary_table}_list",  # "abilities_list"
            f"{singular_form}_list",  # "ability_list"
        ]

        for field in relationship_fields:
            if field in primary_item:
                related = primary_item[field]
                if isinstance(related, str):
                    return [related]
                elif isinstance(related, list):
                    return related

        return []

    def _get_type_field(self, table: str) -> str:
        """Get the type field name for a table."""
        type_mapping = {
            "entities": "entity_type",
            "abilities": "ability_type",
            "status_effects": "effect_type",
            "buffs": "buff_type",
            "suffixes": "applies_to",
            "locations": "location_type",
        }
        return type_mapping.get(table, "type")


class SQLiteDataBackend(DataBackend):
    """SQLite database backend for performance and relationships."""

    def __init__(self, db_path: str = "data/game.db"):
        """Initialize SQLite backend."""
        self.tag = "SQLiteBackend"
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.initialize()
        Log.p(self.tag, [f"SQLite backend initialized with database: {db_path}"])

    def get_item(self, table: str, name: str) -> Optional[Dict[str, Any]]:
        """Get a single item by name."""
        if not self.db_manager.connection:
            return None

        cursor = self.db_manager.connection.cursor()
        cursor.execute(f"SELECT data FROM {table} WHERE name = ?", (name,))
        row = cursor.fetchone()

        if row:
            return json.loads(row["data"])
        return None

    def get_all_items(
        self, table: str, item_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all items from a table, optionally filtered by type."""
        if not self.db_manager.connection:
            return []

        cursor = self.db_manager.connection.cursor()

        if item_type:
            type_field = self._get_type_field(table)
            cursor.execute(
                f"SELECT data FROM {table} WHERE {type_field} = ?", (item_type,)
            )
        else:
            cursor.execute(f"SELECT data FROM {table}")

        rows = cursor.fetchall()
        return [json.loads(row["data"]) for row in rows]

    def save_item(self, table: str, name: str, data: Dict[str, Any]) -> None:
        """Save an item to the backend."""
        if not self.db_manager.connection:
            raise DatabaseError("No database connection")

        cursor = self.db_manager.connection.cursor()
        data_json = json.dumps(data, indent=2)

        # Determine type and additional fields
        type_field = self._get_type_field(table)
        item_type = data.get(type_field, "unknown")

        if table == "entities":
            cursor.execute(
                """
                INSERT OR REPLACE INTO entities (name, data, entity_type) 
                VALUES (?, ?, ?)
            """,
                (name, data_json, item_type),
            )

        elif table == "abilities":
            mana_cost = data.get("mana_cost", 0)
            cursor.execute(
                """
                INSERT OR REPLACE INTO abilities (name, data, ability_type, mana_cost) 
                VALUES (?, ?, ?, ?)
            """,
                (name, data_json, item_type, mana_cost),
            )

        elif table == "status_effects":
            duration = data.get("duration", -1)
            cursor.execute(
                """
                INSERT OR REPLACE INTO status_effects (name, data, effect_type, duration) 
                VALUES (?, ?, ?, ?)
            """,
                (name, data_json, item_type, duration),
            )

        elif table == "buffs":
            cursor.execute(
                """
                INSERT OR REPLACE INTO buffs (name, data, buff_type) 
                VALUES (?, ?, ?)
            """,
                (name, data_json, item_type),
            )

        elif table == "suffixes":
            applies_to = data.get("applies_to", "unknown")
            cursor.execute(
                """
                INSERT OR REPLACE INTO suffixes (name, data, applies_to) 
                VALUES (?, ?, ?)
            """,
                (name, data_json, applies_to),
            )

        elif table == "locations":
            cursor.execute(
                """
                INSERT OR REPLACE INTO locations (name, data, location_type) 
                VALUES (?, ?, ?)
            """,
                (name, data_json, item_type),
            )

        self.db_manager.connection.commit()
        Log.p(self.tag, [f"Saved {name} to {table}"])

    def delete_item(self, table: str, name: str) -> bool:
        """Delete an item from the backend."""
        if not self.db_manager.connection:
            return False

        cursor = self.db_manager.connection.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE name = ?", (name,))

        affected = cursor.rowcount > 0
        if affected:
            self.db_manager.connection.commit()
            Log.p(self.tag, [f"Deleted {name} from {table}"])

        return affected

    def search_items(self, table: str, **filters) -> List[Dict[str, Any]]:
        """Search items with filters."""
        if not self.db_manager.connection:
            return []

        cursor = self.db_manager.connection.cursor()

        # Build WHERE clause from filters
        where_clauses = []
        params = []

        for key, value in filters.items():
            if key in [
                "name",
                "entity_type",
                "ability_type",
                "effect_type",
                "buff_type",
                "applies_to",
                "location_type",
                "mana_cost",
                "duration",
            ]:
                # Direct column search
                where_clauses.append(f"{key} = ?")
                params.append(value)
            else:
                # JSON field search using JSON_EXTRACT for better compatibility
                where_clauses.append(f"JSON_EXTRACT(data, '$.{key}') = ?")
                params.append(value)

        if where_clauses:
            where_sql = " AND ".join(where_clauses)
            cursor.execute(f"SELECT data FROM {table} WHERE {where_sql}", params)
        else:
            cursor.execute(f"SELECT data FROM {table}")

        rows = cursor.fetchall()
        return [json.loads(row["data"]) for row in rows]

    def get_relationships(
        self, primary_table: str, secondary_table: str, primary_name: str
    ) -> List[str]:
        """Get related items (e.g., entity abilities)."""
        if not self.db_manager.connection:
            return []

        cursor = self.db_manager.connection.cursor()

        # Try relationship table first
        if primary_table == "entities" and secondary_table == "abilities":
            cursor.execute(
                """
                SELECT ability_name FROM entity_abilities 
                WHERE entity_name = ?
            """,
                (primary_name,),
            )
            rows = cursor.fetchall()
            return [row["ability_name"] for row in rows]

        # Fall back to JSON data
        primary_item = self.get_item(primary_table, primary_name)
        if primary_item:
            # Look for relationship fields in JSON data - try various naming patterns
            # Handle the special case where "abilities" -> "ability"
            if secondary_table == "abilities":
                singular_form = "ability"
            elif secondary_table.endswith("ies"):
                singular_form = secondary_table[:-3] + "y"  # "abilities" -> "ability"
            elif secondary_table.endswith("s"):
                singular_form = secondary_table[:-1]  # "items" -> "item"
            else:
                singular_form = secondary_table

            relationship_fields = [
                secondary_table,  # "abilities"
                singular_form,  # "ability"
                f"{secondary_table}_list",  # "abilities_list"
                f"{singular_form}_list",  # "ability_list"
            ]

            for field in relationship_fields:
                if field in primary_item:
                    related = primary_item[field]
                    if isinstance(related, str):
                        return [related]
                    elif isinstance(related, list):
                        return related

        return []

    def _get_type_field(self, table: str) -> str:
        """Get the type field name for a table."""
        type_mapping = {
            "entities": "entity_type",
            "abilities": "ability_type",
            "status_effects": "effect_type",
            "buffs": "buff_type",
            "suffixes": "applies_to",
            "locations": "location_type",
        }
        return type_mapping.get(table, "type")

    def close(self) -> None:
        """Close database connection."""
        if self.db_manager:
            self.db_manager.close()


class DataBackendFactory:
    """Factory for creating data backends."""

    @staticmethod
    def create_backend(backend_type: str = "sqlite", **kwargs) -> DataBackend:
        """Create a data backend instance."""
        if backend_type.lower() == "json":
            return JSONDataBackend(**kwargs)
        elif backend_type.lower() == "sqlite":
            return SQLiteDataBackend(**kwargs)
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")


# EOF
