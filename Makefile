# Broken Divinity - Enhanced Close-to-Shore Workflow
# Makefile for automated testing and validation commands

PYTHON := .venv/bin/python
PYTEST := $(PYTHON) -m pytest

# Test commands by category
.PHONY: test-unit test-integration test-smoke test-game-flow test-all test-scratch

test-unit:
	@echo "Running unit tests..."
	$(PYTEST) tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	$(PYTEST) tests/integration/ -v

test-smoke:
	@echo "Running smoke tests..."
	$(PYTEST) tests/smoke/ -v

test-game-flow:
	@echo "Running game flow tests..."
	$(PYTEST) tests/game_flow/ -v

test-all:
	@echo "Running all tests..."
	$(PYTEST) tests/ -v

test-scratch:
	@echo "Running scratch tests..."
	$(PYTEST) scratch_tests/ -q

# Validation commands
.PHONY: validate-schemas validate-boot validate-data validate-db

validate-schemas:
	@echo "Validating database schema..."
	$(PYTHON) -m src.data.migrations validate

validate-boot:
	@echo "Running boot test..."
	$(PYTHON) -m src.main --boot-test

validate-db:
	@echo "Validating database integrity..."
	$(PYTHON) -m src.data.database validate

validate-data: validate-schemas validate-db validate-boot
	@echo "All data validation complete"

# Workflow commands
.PHONY: test-pre-commit test-hop-complete test-debug

test-pre-commit: test-all validate-data
	@echo "Pre-commit validation complete"

test-hop-complete: test-pre-commit
	@echo "Automated tests complete. Run manual player test next."

test-debug:
	@echo "Running tests with debug output..."
	$(PYTEST) tests/ -v -s --tb=long

# Game commands
.PHONY: run run-debug

run:
	@echo "Starting game..."
	$(PYTHON) -m src.main

run-debug:
	@echo "Starting game with debug output..."
	$(PYTHON) -m src.main --debug --verbose

# Development commands
.PHONY: install format clean migrate-db reset-db

install:
	@echo "Installing dependencies..."
	.venv/bin/pip install -e .[dev]

format:
	@echo "Formatting code..."
	.venv/bin/black src/ tests/

migrate-db:
	@echo "Running database migrations..."
	$(PYTHON) -m src.data.migrations migrate

reset-db:
	@echo "Resetting database (WARNING: destroys data)..."
	$(PYTHON) -m src.data.database reset

clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache *.egg-info

# Help
.PHONY: help

help:
	@echo "Broken Divinity - Enhanced Close-to-Shore Workflow"
	@echo ""
	@echo "Test Commands:"
	@echo "  test-unit         Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-smoke        Run smoke tests only"
	@echo "  test-game-flow    Run game flow tests only"
	@echo "  test-all          Run all tests"
	@echo "  test-scratch      Run scratch/debug tests"
	@echo ""
	@echo "Validation Commands:"
	@echo "  validate-schemas  Validate JSON schema compliance"
	@echo "  validate-boot     Run game boot test"
	@echo "  validate-data     Run all data validation"
	@echo ""
	@echo "Workflow Commands:"
	@echo "  test-pre-commit   Full automated test suite"
	@echo "  test-hop-complete Everything + reminder for manual test"
	@echo "  test-debug        Run tests with verbose output"
	@echo ""
	@echo "Game Commands:"
	@echo "  run               Start the game"
	@echo "  run-debug         Start game with debug output"
	@echo ""
	@echo "Development Commands:"
	@echo "  install           Install dependencies"
	@echo "  format            Format code with Black"
	@echo "  migrate-db        Run database migrations"
	@echo "  reset-db          Reset database (destroys data)"
	@echo "  clean             Clean cache files"
	@echo "  help              Show this help message"

# Default target
.DEFAULT_GOAL := help
