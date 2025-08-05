#!/usr/bin/env python3
"""
JSON Schema Validation Script

Validates all JSON data fi        # Map directories to schema types
        type_mapping = {
            "abilities": "abilities",
            "status_effects": "status_effects",
            "character_backgrounds": "character_backgrounds",
            "locations": "locations",
            "characters": "characters",
            "items": "items"
        }nst their schemas before development begins.
This prevents data file errors and ensures consistency across the project.

Usage:
    python validate_json.py
    python validate_json.py --schemas-dir schemas/
    python validate_json.py --data-dir data/
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("ERROR: jsonschema package not installed")
    print("Install with: pip install jsonschema")
    sys.exit(1)


class JSONValidator:
    """Validates JSON files against schemas."""

    def __init__(
        self, schemas_dir: Path = Path("schemas"), data_dir: Path = Path("data")
    ):
        self.schemas_dir = schemas_dir
        self.data_dir = data_dir
        self.schemas: Dict[str, dict] = {}
        self.errors: List[str] = []

    def load_schemas(self) -> bool:
        """Load all schema files from schemas directory."""
        if not self.schemas_dir.exists():
            self.errors.append(f"Schemas directory not found: {self.schemas_dir}")
            return False

        schema_files = list(self.schemas_dir.glob("*_schema.json"))
        if not schema_files:
            self.errors.append(f"No schema files found in {self.schemas_dir}")
            return False

        for schema_file in schema_files:
            try:
                with open(schema_file, "r", encoding="utf-8") as f:
                    schema = json.load(f)

                # Validate schema itself
                Draft7Validator.check_schema(schema)

                # Extract data type from filename (e.g., "abilities_schema.json" -> "abilities")
                data_type = schema_file.stem.replace("_schema", "")
                self.schemas[data_type] = schema

                print(f"✓ Loaded schema: {data_type}")

            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid JSON in schema {schema_file}: {e}")
                return False
            except jsonschema.SchemaError as e:
                self.errors.append(f"Invalid schema {schema_file}: {e}")
                return False
            except Exception as e:
                self.errors.append(f"Error loading schema {schema_file}: {e}")
                return False

        return True

    def find_data_files(self) -> Dict[str, List[Path]]:
        """Find all JSON data files organized by type."""
        data_files: Dict[str, List[Path]] = {}

        if not self.data_dir.exists():
            self.errors.append(f"Data directory not found: {self.data_dir}")
            return data_files

        # Map directories to schema types
        type_mapping = {
            "abilities": "abilities",
            "status_effects": "status_effects",
            "locations": "locations",
            "characters": "characters",
            "items": "items",
        }

        for subdir, schema_type in type_mapping.items():
            subdir_path = self.data_dir / subdir
            if subdir_path.exists():
                json_files = list(subdir_path.glob("*.json"))
                if json_files:
                    data_files[schema_type] = json_files

        return data_files

    def validate_file(
        self, file_path: Path, schema: dict
    ) -> Tuple[bool, Optional[str]]:
        """Validate a single JSON file against a schema."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            validate(instance=data, schema=schema)
            return True, None

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except ValidationError as e:
            return False, f"Schema validation failed: {e.message}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def validate_all(self) -> bool:
        """Validate all data files against their schemas."""
        if not self.load_schemas():
            return False

        data_files = self.find_data_files()
        if not data_files:
            print("No data files found to validate")
            return True

        total_files = 0
        valid_files = 0

        for data_type, files in data_files.items():
            if data_type not in self.schemas:
                print(f"⚠ No schema found for data type: {data_type}")
                continue

            schema = self.schemas[data_type]
            print(f"\n📁 Validating {data_type} files...")

            for file_path in files:
                total_files += 1
                is_valid, error_msg = self.validate_file(file_path, schema)

                if is_valid:
                    print(f"  ✓ {file_path.name}")
                    valid_files += 1
                else:
                    print(f"  ✗ {file_path.name}: {error_msg}")
                    self.errors.append(f"{file_path}: {error_msg}")

        print(f"\n📊 Validation Summary:")
        print(f"  Total files: {total_files}")
        print(f"  Valid files: {valid_files}")
        print(f"  Invalid files: {total_files - valid_files}")

        if self.errors:
            print(f"\n❌ Validation failed with {len(self.errors)} errors:")
            for error in self.errors:
                print(f"  • {error}")
            return False
        else:
            print(f"\n✅ All JSON files are valid!")
            return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate JSON data files against schemas"
    )
    parser.add_argument(
        "--schemas-dir",
        type=Path,
        default=Path("schemas"),
        help="Directory containing schema files (default: schemas/)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing data files (default: data/)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    print("🔍 JSON Schema Validation")
    print("=" * 50)

    validator = JSONValidator(args.schemas_dir, args.data_dir)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
