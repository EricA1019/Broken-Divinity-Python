"""Test data backend abstraction layer."""

import json
import sqlite3
import tempfile
from pathlib import Path
import pytest

from src.data.backend import (
    DataBackend,
    JSONDataBackend,
    SQLiteDataBackend,
    DataBackendFactory,
)


class TestDataBackendFactory:
    """Test the data backend factory."""

    def test_create_json_backend(self):
        """Test creating JSON backend."""
        backend = DataBackendFactory.create_backend("json", data_root="test_data")
        assert isinstance(backend, JSONDataBackend)

    def test_create_sqlite_backend(self):
        """Test creating SQLite backend."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            db_path = temp_db.name

        backend = DataBackendFactory.create_backend("sqlite", db_path=db_path)
        assert isinstance(backend, SQLiteDataBackend)

        backend.close()
        Path(db_path).unlink(missing_ok=True)

    def test_invalid_backend_type(self):
        """Test creating invalid backend type."""
        with pytest.raises(ValueError):
            DataBackendFactory.create_backend("invalid")


class TestJSONDataBackend:
    """Test JSON data backend."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_data_dir = tempfile.mkdtemp()
        self.data_path = Path(self.temp_data_dir)
        self.backend = JSONDataBackend(self.temp_data_dir)

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_data_dir, ignore_errors=True)

    def create_test_json_file(self, folder: str, filename: str, data):
        """Helper to create test JSON files."""
        folder_path = self.data_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = folder_path / f"{filename}.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        return file_path

    def test_get_item(self):
        """Test getting a single item."""
        test_data = [
            {"name": "TestEntity", "entity_type": "player", "health": 100},
            {"name": "TestMonster", "entity_type": "enemy", "health": 50},
        ]

        self.create_test_json_file("entities", "test", test_data)

        # Get existing item
        item = self.backend.get_item("entities", "TestEntity")
        assert item is not None
        assert item["name"] == "TestEntity"
        assert item["health"] == 100

        # Get non-existing item
        item = self.backend.get_item("entities", "NonExistent")
        assert item is None

    def test_get_all_items(self):
        """Test getting all items."""
        test_data = [
            {"name": "Player", "entity_type": "player", "health": 100},
            {"name": "Goblin", "entity_type": "enemy", "health": 30},
            {"name": "Orc", "entity_type": "enemy", "health": 50},
        ]

        self.create_test_json_file("entities", "test", test_data)

        # Get all items
        all_items = self.backend.get_all_items("entities")
        assert len(all_items) == 3

        # Get items by type
        enemies = self.backend.get_all_items("entities", "enemy")
        assert len(enemies) == 2
        assert all(item["entity_type"] == "enemy" for item in enemies)

    def test_save_item(self):
        """Test saving an item."""
        # Save new item
        test_item = {"name": "NewEntity", "entity_type": "player", "health": 100}
        self.backend.save_item("entities", "NewEntity", test_item)

        # Verify it was saved
        saved_item = self.backend.get_item("entities", "NewEntity")
        assert saved_item is not None
        assert saved_item["name"] == "NewEntity"

    def test_delete_item(self):
        """Test deleting an item."""
        test_data = [{"name": "ToDelete", "entity_type": "test"}]
        self.create_test_json_file("entities", "test", test_data)

        # Verify item exists
        item = self.backend.get_item("entities", "ToDelete")
        assert item is not None

        # Delete item
        deleted = self.backend.delete_item("entities", "ToDelete")
        assert deleted is True

        # Verify item is gone
        item = self.backend.get_item("entities", "ToDelete")
        assert item is None

        # Try to delete non-existent item
        deleted = self.backend.delete_item("entities", "NonExistent")
        assert deleted is False

    def test_search_items(self):
        """Test searching items with filters."""
        test_data = [
            {"name": "Player", "entity_type": "player", "level": 5},
            {"name": "Goblin", "entity_type": "enemy", "level": 1},
            {"name": "Elite Goblin", "entity_type": "enemy", "level": 3},
        ]

        self.create_test_json_file("entities", "test", test_data)

        # Search by entity_type
        enemies = self.backend.search_items("entities", entity_type="enemy")
        assert len(enemies) == 2

        # Search by level
        level_3 = self.backend.search_items("entities", level=3)
        assert len(level_3) == 1
        assert level_3[0]["name"] == "Elite Goblin"

        # Search with multiple filters
        enemy_level_1 = self.backend.search_items(
            "entities", entity_type="enemy", level=1
        )
        assert len(enemy_level_1) == 1
        assert enemy_level_1[0]["name"] == "Goblin"

    def test_get_relationships(self):
        """Test getting relationships."""
        entity_data = [
            {
                "name": "Warrior",
                "entity_type": "player",
                "abilities": ["Slash", "Block"],
            },
            {
                "name": "Mage",
                "entity_type": "player",
                "ability": "Fireball",  # Single ability
            },
        ]

        self.create_test_json_file("entities", "test", entity_data)

        # Test list of abilities
        warrior_abilities = self.backend.get_relationships(
            "entities", "abilities", "Warrior"
        )
        assert warrior_abilities == ["Slash", "Block"]

        # Test single ability
        mage_abilities = self.backend.get_relationships("entities", "abilities", "Mage")
        assert mage_abilities == ["Fireball"]

        # Test non-existent entity
        no_abilities = self.backend.get_relationships(
            "entities", "abilities", "NonExistent"
        )
        assert no_abilities == []

    def test_different_json_formats(self):
        """Test handling different JSON file formats."""
        # Array format
        array_data = [{"name": "ArrayItem", "entity_type": "test"}]
        self.create_test_json_file("entities", "array", array_data)

        # Object with items format
        items_data = {
            "version": "1.0",
            "items": [{"name": "ItemsItem", "entity_type": "test"}],
        }
        self.create_test_json_file("entities", "items", items_data)

        # Single object format
        single_data = {"name": "SingleItem", "entity_type": "test"}
        self.create_test_json_file("entities", "single", single_data)

        # Verify all items are loaded
        all_items = self.backend.get_all_items("entities")
        names = [item["name"] for item in all_items]

        assert "ArrayItem" in names
        assert "ItemsItem" in names
        assert "SingleItem" in names


class TestSQLiteDataBackend:
    """Test SQLite data backend."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        self.backend = SQLiteDataBackend(self.db_path)

    def teardown_method(self):
        """Clean up test environment."""
        self.backend.close()
        Path(self.db_path).unlink(missing_ok=True)

    def test_get_item(self):
        """Test getting a single item."""
        # Save test item
        test_item = {"name": "TestEntity", "entity_type": "player", "health": 100}
        self.backend.save_item("entities", "TestEntity", test_item)

        # Get existing item
        item = self.backend.get_item("entities", "TestEntity")
        assert item is not None
        assert item["name"] == "TestEntity"
        assert item["health"] == 100

        # Get non-existing item
        item = self.backend.get_item("entities", "NonExistent")
        assert item is None

    def test_get_all_items(self):
        """Test getting all items."""
        # Save test items
        entities = [
            {"name": "Player", "entity_type": "player", "health": 100},
            {"name": "Goblin", "entity_type": "enemy", "health": 30},
            {"name": "Orc", "entity_type": "enemy", "health": 50},
        ]

        for entity in entities:
            self.backend.save_item("entities", entity["name"], entity)

        # Get all items
        all_items = self.backend.get_all_items("entities")
        assert len(all_items) == 3

        # Get items by type
        enemies = self.backend.get_all_items("entities", "enemy")
        assert len(enemies) == 2
        assert all(item["entity_type"] == "enemy" for item in enemies)

    def test_save_and_delete_item(self):
        """Test saving and deleting items."""
        # Save item
        test_item = {"name": "ToDelete", "entity_type": "test", "health": 100}
        self.backend.save_item("entities", "ToDelete", test_item)

        # Verify it was saved
        saved_item = self.backend.get_item("entities", "ToDelete")
        assert saved_item is not None
        assert saved_item["name"] == "ToDelete"

        # Delete item
        deleted = self.backend.delete_item("entities", "ToDelete")
        assert deleted is True

        # Verify item is gone
        item = self.backend.get_item("entities", "ToDelete")
        assert item is None

        # Try to delete non-existent item
        deleted = self.backend.delete_item("entities", "NonExistent")
        assert deleted is False

    def test_search_items(self):
        """Test searching items with filters."""
        # Save test items
        entities = [
            {"name": "Player", "entity_type": "player", "level": 5},
            {"name": "Goblin", "entity_type": "enemy", "level": 1},
            {"name": "Elite Goblin", "entity_type": "enemy", "level": 3},
        ]

        for entity in entities:
            self.backend.save_item("entities", entity["name"], entity)

        # Search by entity_type
        enemies = self.backend.search_items("entities", entity_type="enemy")
        assert len(enemies) == 2

        # Search by multiple filters
        enemy_level_1 = self.backend.search_items(
            "entities", entity_type="enemy", level=1
        )
        assert len(enemy_level_1) == 1
        assert enemy_level_1[0]["name"] == "Goblin"

    def test_abilities_with_mana_cost(self):
        """Test saving abilities with mana cost."""
        ability_data = {
            "name": "Fireball",
            "ability_type": "offensive",
            "mana_cost": 25,
            "damage": 50,
            "description": "A powerful fire spell",
        }

        self.backend.save_item("abilities", "Fireball", ability_data)

        # Verify it was saved with mana_cost
        saved_ability = self.backend.get_item("abilities", "Fireball")
        assert saved_ability is not None
        assert saved_ability["mana_cost"] == 25

        # Verify in database directly
        assert self.backend.db_manager.connection is not None
        cursor = self.backend.db_manager.connection.cursor()
        cursor.execute("SELECT mana_cost FROM abilities WHERE name = ?", ("Fireball",))
        row = cursor.fetchone()
        assert row["mana_cost"] == 25

    def test_get_relationships_with_relationship_table(self):
        """Test getting relationships using relationship table."""
        # Save entities and abilities
        warrior_data = {"name": "Warrior", "entity_type": "player"}
        ability_data = {"name": "Slash", "ability_type": "offensive"}

        self.backend.save_item("entities", "Warrior", warrior_data)
        self.backend.save_item("abilities", "Slash", ability_data)

        # Add relationship manually to test relationship table
        assert self.backend.db_manager.connection is not None
        cursor = self.backend.db_manager.connection.cursor()
        cursor.execute(
            """
            INSERT INTO entity_abilities (entity_name, ability_name) 
            VALUES (?, ?)
        """,
            ("Warrior", "Slash"),
        )
        self.backend.db_manager.connection.commit()

        # Test getting relationships
        abilities = self.backend.get_relationships("entities", "abilities", "Warrior")
        assert abilities == ["Slash"]

    def test_get_relationships_from_json_data(self):
        """Test getting relationships from JSON data."""
        # Save entity with abilities in JSON data
        entity_data = {
            "name": "Mage",
            "entity_type": "player",
            "abilities": ["Fireball", "Heal"],
        }

        self.backend.save_item("entities", "Mage", entity_data)

        # Test getting relationships from JSON
        mage_item = self.backend.get_item("entities", "Mage")
        print(f"DEBUG: Saved Mage item: {mage_item}")
        abilities = self.backend.get_relationships("entities", "abilities", "Mage")
        print(f"DEBUG: Found abilities: {abilities}")
        assert abilities == ["Fireball", "Heal"]


class TestBackendCompatibility:
    """Test that both backends provide the same interface."""

    def setup_method(self):
        """Set up test environment with both backends."""
        # JSON backend
        self.temp_data_dir = tempfile.mkdtemp()
        self.json_backend = JSONDataBackend(self.temp_data_dir)

        # SQLite backend
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.sqlite_backend = SQLiteDataBackend(self.db_path)

        # Test data
        self.test_entity = {
            "name": "TestEntity",
            "entity_type": "player",
            "health": 100,
            "mana": 50,
        }

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_data_dir, ignore_errors=True)

        self.sqlite_backend.close()
        Path(self.db_path).unlink(missing_ok=True)

    def test_both_backends_same_interface(self):
        """Test that both backends implement the same interface."""
        backends = [self.json_backend, self.sqlite_backend]

        for backend in backends:
            # Test save and get
            backend.save_item("entities", "TestEntity", self.test_entity)
            retrieved = backend.get_item("entities", "TestEntity")

            assert retrieved is not None
            assert retrieved["name"] == "TestEntity"
            assert retrieved["health"] == 100

            # Test get_all_items
            all_items = backend.get_all_items("entities")
            assert len(all_items) >= 1

            # Test search
            players = backend.search_items("entities", entity_type="player")
            assert len(players) >= 1

            # Test delete
            deleted = backend.delete_item("entities", "TestEntity")
            assert deleted is True

            # Verify deletion
            retrieved = backend.get_item("entities", "TestEntity")
            assert retrieved is None


# EOF
