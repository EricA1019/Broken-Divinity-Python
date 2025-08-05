"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Database Layer Unit Tests                                                   ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Unit tests for SQLite database manager                     ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.12                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.data.database import DatabaseManager, DatabaseError
from src.core.signals import get_signal_bus, reset_signal_bus, CoreSignal


class TestDatabaseManager:
    """Test the SQLite database manager."""

    def setup_method(self):
        """Set up test database in temporary location."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_game.db"
        self.db_manager = DatabaseManager(str(self.db_path))

        # Reset signal bus for clean tests
        reset_signal_bus()

    def teardown_method(self):
        """Clean up temporary database."""
        if self.db_manager:
            self.db_manager.close()

        # Clean up all files in temp directory
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_database_manager_initialization(self):
        """Test database manager creates and initializes properly."""
        assert self.db_manager.db_path == str(self.db_path)
        assert self.db_manager.connection is None  # Not connected until first use

    def test_database_connection_and_initialization(self):
        """Test database connects and creates schema."""
        self.db_manager.initialize()

        # Should create database file
        assert self.db_path.exists()

        # Should have connection
        assert self.db_manager.connection is not None

        # Should create all required tables
        cursor = self.db_manager.connection.cursor()

        # Check schema_version table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
        )
        assert cursor.fetchone() is not None

        # Check entities table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='entities'"
        )
        assert cursor.fetchone() is not None

        # Check abilities table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='abilities'"
        )
        assert cursor.fetchone() is not None

    def test_database_schema_version_tracking(self):
        """Test schema version is properly tracked."""
        self.db_manager.initialize()

        # Should have version 1 after initialization
        version = self.db_manager.get_schema_version()
        assert version == 1

    def test_database_in_memory_mode(self):
        """Test database can run in memory for performance."""
        memory_db = DatabaseManager(":memory:")
        memory_db.initialize()

        # Should work the same as file database
        assert memory_db.connection is not None
        version = memory_db.get_schema_version()
        assert version == 1

        memory_db.close()

    def test_database_connection_error_handling(self):
        """Test database handles connection errors gracefully."""
        # Mock sqlite3.connect to raise an error
        import sqlite3
        from unittest.mock import patch

        with patch("sqlite3.connect", side_effect=sqlite3.Error("Connection failed")):
            bad_db = DatabaseManager("some/path/database.db")

            with pytest.raises(DatabaseError):
                bad_db.initialize()

    def test_database_close_connection(self):
        """Test database connection closes properly."""
        self.db_manager.initialize()
        assert self.db_manager.connection is not None

        self.db_manager.close()
        assert self.db_manager.connection is None

    def test_database_validates_integrity(self):
        """Test database can validate its own integrity."""
        self.db_manager.initialize()

        # Should pass validation on clean database
        is_valid = self.db_manager.validate()
        assert is_valid is True

    def test_database_backup_functionality(self):
        """Test database can create backups."""
        self.db_manager.initialize()

        # Add some test data
        if self.db_manager.connection:
            self.db_manager.connection.execute(
                "INSERT INTO entities (name, data, entity_type) VALUES (?, ?, ?)",
                ("test_entity", '{"hp": 100}', "test"),
            )
            self.db_manager.connection.commit()

        # Create backup
        backup_path = Path(self.temp_dir) / "backup.db"
        self.db_manager.backup(str(backup_path))

        assert backup_path.exists()

        # Verify backup contains data
        backup_conn = sqlite3.connect(str(backup_path))
        cursor = backup_conn.cursor()
        cursor.execute("SELECT name FROM entities WHERE name='test_entity'")
        result = cursor.fetchone()
        assert result is not None
        backup_conn.close()


class TestDatabaseError:
    """Test database error handling."""

    def test_database_error_creation(self):
        """Test DatabaseError can be created with message."""
        error = DatabaseError("Test error message")
        assert str(error) == "Test error message"

    def test_database_error_with_cause(self):
        """Test DatabaseError can wrap other exceptions."""
        original_error = sqlite3.Error("SQLite error")
        wrapped_error = DatabaseError("Database operation failed", original_error)

        assert "Database operation failed" in str(wrapped_error)
        assert wrapped_error.__cause__ == original_error


class TestDatabaseIntegration:
    """Test database integration with signals and logging."""

    def setup_method(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_game.db"
        self.db_manager = DatabaseManager(str(self.db_path))
        reset_signal_bus()

    def teardown_method(self):
        """Clean up."""
        if self.db_manager:
            self.db_manager.close()

        # Clean up all files in temp directory
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_database_emits_initialization_signal(self):
        """Test database emits signal when initialized."""
        signal_received = False

        def signal_handler(signal_data):
            nonlocal signal_received
            signal_received = True

        signal_bus = get_signal_bus()
        signal_bus.listen(CoreSignal.DATABASE_INITIALIZED, signal_handler)

        self.db_manager.initialize()

        assert signal_received is True

    @patch("src.utils.logging.Log.p")
    def test_database_logs_operations(self, mock_log):
        """Test database logs important operations."""
        self.db_manager.initialize()

        # Should log initialization
        mock_log.assert_called()

        # Check that database tag was used
        calls = mock_log.call_args_list
        assert any("Database" in str(call) for call in calls)
