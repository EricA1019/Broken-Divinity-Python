"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SQLite Database Manager                                                     ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : SQLite database layer for game content and save data       ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.12                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sqlite3
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Any
import json

from src.core.signals import get_signal_bus, CoreSignal
from src.utils.logging import Log


class DatabaseError(Exception):
    """Exception raised for database-related errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.__cause__ = cause


class DatabaseManager:
    """Manages SQLite database for game content and save data."""

    def __init__(self, db_path: str = "data/game.db"):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file, or ":memory:" for in-memory
        """
        self.tag = "Database"
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        Log.p(self.tag, [f"Database manager created for {db_path}"])

    def initialize(self) -> None:
        """Initialize database connection and create schema."""
        try:
            # Create directory if needed (unless memory database)
            if self.db_path != ":memory:":
                db_file = Path(self.db_path)
                db_file.parent.mkdir(parents=True, exist_ok=True)

            # Connect to database
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name

            Log.p(self.tag, [f"Connected to database: {self.db_path}"])

            # Create schema
            self._create_schema()

            # Emit initialization signal
            signal_bus = get_signal_bus()
            signal_bus.emit(CoreSignal.DATABASE_INITIALIZED, source="DatabaseManager")

            Log.p(self.tag, ["Database initialized successfully"])

        except sqlite3.Error as e:
            error_msg = f"Failed to initialize database: {e}"
            Log.p(self.tag, [f"ERROR: {error_msg}"])
            raise DatabaseError(error_msg, e)

    def _create_schema(self) -> None:
        """Create database schema with all required tables."""
        if not self.connection:
            raise DatabaseError("No database connection")

        cursor = self.connection.cursor()

        # Schema version tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Content tables (store JSON data with metadata for indexing)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS abilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                ability_type TEXT,
                mana_cost INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS status_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                effect_type TEXT,
                duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS buffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                buff_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS suffixes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                applies_to TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                location_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Relationship tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_abilities (
                entity_name TEXT REFERENCES entities(name),
                ability_name TEXT REFERENCES abilities(name),
                PRIMARY KEY (entity_name, ability_name)
            )
        """
        )

        # Create indexes for performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_abilities_type ON abilities(ability_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_abilities_mana ON abilities(mana_cost)"
        )

        # Set initial schema version if not exists
        cursor.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        )
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO schema_version (version) VALUES (1)")

        self.connection.commit()
        Log.p(self.tag, ["Database schema created"])

    def get_schema_version(self) -> int:
        """Get current database schema version."""
        if not self.connection:
            raise DatabaseError("No database connection")

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        )
        result = cursor.fetchone()
        return result[0] if result else 0

    def validate(self) -> bool:
        """Validate database integrity."""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            is_valid = result and result[0] == "ok"

            Log.p(self.tag, [f"Database validation: {'PASS' if is_valid else 'FAIL'}"])
            return is_valid

        except sqlite3.Error as e:
            Log.p(self.tag, [f"Database validation error: {e}"])
            return False

    def backup(self, backup_path: str) -> None:
        """Create a backup of the database."""
        if not self.connection:
            raise DatabaseError("No database connection")

        if self.db_path == ":memory:":
            raise DatabaseError("Cannot backup in-memory database")

        try:
            # Ensure backup directory exists
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)

            # Create backup using SQLite backup API
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()

            Log.p(self.tag, [f"Database backed up to: {backup_path}"])

        except sqlite3.Error as e:
            error_msg = f"Failed to backup database: {e}"
            Log.p(self.tag, [f"ERROR: {error_msg}"])
            raise DatabaseError(error_msg, e)

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            Log.p(self.tag, ["Database connection closed"])

    def __enter__(self):
        """Context manager entry."""
        if not self.connection:
            self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# EOF
