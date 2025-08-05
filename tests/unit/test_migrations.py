"""Test JSON to SQLite migration functionality."""

import json
import sqlite3
import tempfile
from pathlib import Path
import pytest

from src.data.database import DatabaseManager
from src.data.migrations import JSONMigrator, migrate_json_to_sqlite


class TestJSONMigrator:
    """Test JSON migration functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Create database manager and migrator
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager.initialize()
        self.migrator = JSONMigrator(self.db_manager)

        # Create temporary data directory
        self.temp_data_dir = tempfile.mkdtemp()
        self.data_path = Path(self.temp_data_dir)

    def teardown_method(self):
        """Clean up test environment."""
        if self.db_manager.connection:
            self.db_manager.close()
        Path(self.db_path).unlink(missing_ok=True)

        # Clean up temp data directory
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

    def test_migrate_entities(self):
        """Test migrating entity data."""
        entities_data = [
            {
                "name": "PlayerCharacter",
                "entity_type": "player",
                "health": 100,
                "mana": 50,
                "abilities": ["BasicAttack", "Heal"],
            },
            {"name": "Goblin", "entity_type": "enemy", "health": 30, "damage": 10},
        ]

        self.create_test_json_file("entities", "test_entities", entities_data)

        # Migrate
        count = self.migrator._migrate_folder(
            self.data_path / "entities", "entities", "entity_type"
        )

        assert count == 2

        # Verify data in database
        assert self.db_manager.connection is not None
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT name, entity_type, data FROM entities")
        rows = cursor.fetchall()

        assert len(rows) == 2

        # Check first entity
        player_row = next(r for r in rows if r["name"] == "PlayerCharacter")
        assert player_row["entity_type"] == "player"
        player_data = json.loads(player_row["data"])
        assert player_data["health"] == 100
        assert player_data["abilities"] == ["BasicAttack", "Heal"]

    def test_migrate_abilities(self):
        """Test migrating ability data."""
        abilities_data = [
            {
                "name": "BasicAttack",
                "ability_type": "offensive",
                "mana_cost": 0,
                "damage": 20,
                "description": "A basic attack",
            },
            {
                "name": "Heal",
                "ability_type": "supportive",
                "mana_cost": 15,
                "healing": 25,
                "description": "Restore health",
            },
        ]

        self.create_test_json_file("abilities", "test_abilities", abilities_data)

        # Migrate
        count = self.migrator._migrate_folder(
            self.data_path / "abilities", "abilities", "ability_type"
        )

        assert count == 2

        # Verify data in database
        assert self.db_manager.connection is not None
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT name, ability_type, mana_cost, data FROM abilities")
        rows = cursor.fetchall()

        assert len(rows) == 2

        # Check heal ability
        heal_row = next(r for r in rows if r["name"] == "Heal")
        assert heal_row["ability_type"] == "supportive"
        assert heal_row["mana_cost"] == 15
        heal_data = json.loads(heal_row["data"])
        assert heal_data["healing"] == 25

    def test_migrate_status_effects(self):
        """Test migrating status effect data."""
        effects_data = [
            {
                "name": "Poison",
                "effect_type": "damage_over_time",
                "duration": 5,
                "damage_per_turn": 3,
                "description": "Takes damage each turn",
            },
            {
                "name": "Blessing",
                "effect_type": "buff",
                "duration": 10,
                "stat_bonus": {"strength": 5},
                "description": "Increases strength",
            },
        ]

        self.create_test_json_file("status_effects", "test_effects", effects_data)

        # Migrate
        count = self.migrator._migrate_folder(
            self.data_path / "status_effects", "status_effects", "effect_type"
        )

        assert count == 2

        # Verify data in database
        assert self.db_manager.connection is not None
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT name, effect_type, duration, data FROM status_effects")
        rows = cursor.fetchall()

        assert len(rows) == 2

        # Check poison effect
        poison_row = next(r for r in rows if r["name"] == "Poison")
        assert poison_row["effect_type"] == "damage_over_time"
        assert poison_row["duration"] == 5
        poison_data = json.loads(poison_row["data"])
        assert poison_data["damage_per_turn"] == 3

    def test_migrate_different_json_formats(self):
        """Test migrating different JSON file formats."""
        # Test array format
        array_data = [{"name": "Item1", "entity_type": "test"}]
        self.create_test_json_file("entities", "array_format", array_data)

        # Test object with items format
        items_data = {
            "version": "1.0",
            "items": [{"name": "Item2", "entity_type": "test"}],
        }
        self.create_test_json_file("entities", "items_format", items_data)

        # Test single object format
        single_data = {"name": "Item3", "entity_type": "test"}
        self.create_test_json_file("entities", "single_format", single_data)

        # Migrate
        count = self.migrator._migrate_folder(
            self.data_path / "entities", "entities", "entity_type"
        )

        assert count == 3

        # Verify all items are in database
        assert self.db_manager.connection is not None
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT name FROM entities ORDER BY name")
        names = [row["name"] for row in cursor.fetchall()]

        assert "Item1" in names
        assert "Item2" in names
        assert "Item3" in names

    def test_migrate_entity_abilities_relationships(self):
        """Test migrating entity-ability relationships."""
        # Create entities with abilities
        entities_data = [
            {
                "name": "Warrior",
                "entity_type": "player",
                "abilities": ["Slash", "Block"],
            },
            {"name": "Mage", "entity_type": "player", "abilities": ["Fireball"]},
        ]

        abilities_data = [
            {"name": "Slash", "ability_type": "offensive"},
            {"name": "Block", "ability_type": "defensive"},
            {"name": "Fireball", "ability_type": "offensive"},
        ]

        self.create_test_json_file("entities", "test_entities", entities_data)
        self.create_test_json_file("abilities", "test_abilities", abilities_data)

        # Migrate entities and abilities
        self.migrator._migrate_folder(
            self.data_path / "entities", "entities", "entity_type"
        )
        self.migrator._migrate_folder(
            self.data_path / "abilities", "abilities", "ability_type"
        )

        # Migrate relationships
        self.migrator._migrate_entity_abilities()

        # Verify relationships
        assert self.db_manager.connection is not None
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT entity_name, ability_name FROM entity_abilities")
        relationships = cursor.fetchall()

        assert len(relationships) == 3

        # Check specific relationships
        warrior_abilities = [
            r["ability_name"] for r in relationships if r["entity_name"] == "Warrior"
        ]
        assert "Slash" in warrior_abilities
        assert "Block" in warrior_abilities

        mage_abilities = [
            r["ability_name"] for r in relationships if r["entity_name"] == "Mage"
        ]
        assert "Fireball" in mage_abilities

    def test_migrate_all_json_data(self):
        """Test migrating all JSON data at once."""
        # Create test data for multiple types
        entities_data = [{"name": "TestEntity", "entity_type": "test"}]
        abilities_data = [{"name": "TestAbility", "ability_type": "test"}]
        effects_data = [{"name": "TestEffect", "effect_type": "test"}]

        self.create_test_json_file("entities", "test", entities_data)
        self.create_test_json_file("abilities", "test", abilities_data)
        self.create_test_json_file("status_effects", "test", effects_data)

        # Migrate all
        self.migrator.migrate_all_json_data(str(self.data_path))

        # Verify all data types were migrated
        assert self.db_manager.connection is not None
        cursor = self.db_manager.connection.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM entities")
        assert cursor.fetchone()["count"] == 1

        cursor.execute("SELECT COUNT(*) as count FROM abilities")
        assert cursor.fetchone()["count"] == 1

        cursor.execute("SELECT COUNT(*) as count FROM status_effects")
        assert cursor.fetchone()["count"] == 1

    def test_export_to_json(self):
        """Test exporting database content back to JSON."""
        # Add some test data to database
        assert self.db_manager.connection is not None
        cursor = self.db_manager.connection.cursor()

        cursor.execute(
            """
            INSERT INTO entities (name, data, entity_type) 
            VALUES (?, ?, ?)
        """,
            ("TestEntity", '{"name": "TestEntity", "health": 100}', "test"),
        )

        cursor.execute(
            """
            INSERT INTO abilities (name, data, ability_type, mana_cost) 
            VALUES (?, ?, ?, ?)
        """,
            ("TestAbility", '{"name": "TestAbility", "damage": 20}', "test", 10),
        )

        self.db_manager.connection.commit()

        # Export to JSON
        export_dir = self.temp_data_dir + "/export"
        self.migrator.export_to_json(export_dir)

        # Verify exported files
        export_path = Path(export_dir)
        entities_file = export_path / "entities.json"
        abilities_file = export_path / "abilities.json"

        assert entities_file.exists()
        assert abilities_file.exists()

        # Verify content
        with open(entities_file) as f:
            entities = json.load(f)
        assert len(entities) == 1
        assert entities[0]["name"] == "TestEntity"

        with open(abilities_file) as f:
            abilities = json.load(f)
        assert len(abilities) == 1
        assert abilities[0]["name"] == "TestAbility"

    def test_convenience_function(self):
        """Test the convenience migration function."""
        # Create test data
        entities_data = [{"name": "ConvenienceTest", "entity_type": "test"}]
        self.create_test_json_file("entities", "test", entities_data)

        # Use convenience function
        db_path = self.temp_data_dir + "/convenience.db"
        migrate_json_to_sqlite(str(self.data_path), db_path)

        # Verify migration worked
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM entities")
        rows = cursor.fetchall()

        assert len(rows) == 1
        assert rows[0]["name"] == "ConvenienceTest"

        conn.close()
        Path(db_path).unlink(missing_ok=True)


# EOF
