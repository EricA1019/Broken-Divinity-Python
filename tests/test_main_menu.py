"""
Test cases for main menu system and character creation functionality.
Following enhanced Close-to-Shore workflow with test-first development.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.ui.main_ui import MainUI
from src.game.character_creation import CharacterCreator, CharacterBackground
from src.ui.main_menu_screen import MainMenuScreen
from src.ui.character_creation_screen import CharacterCreationScreen


class TestMainMenuSystem:
    """Test main menu as game entry point."""

    def test_main_menu_screen_creation(self):
        """Main menu screen should initialize with proper title and options."""
        main_ui = MainUI()
        menu_screen = MainMenuScreen(main_ui)

        assert menu_screen.title == "Broken Divinity - Main Menu"
        assert len(menu_screen.options) >= 4

        option_texts = [opt.text for opt in menu_screen.options]
        assert "New Game" in option_texts
        assert "Continue Game" in option_texts
        assert "Settings" in option_texts
        assert "Exit" in option_texts

    def test_main_menu_new_game_option(self):
        """New Game option should lead to character creation."""
        main_ui = MainUI()
        menu_screen = MainMenuScreen(main_ui)

        new_game_option = next(
            opt for opt in menu_screen.options if opt.text == "New Game"
        )
        assert new_game_option is not None
        assert new_game_option.action == "new_game"

    def test_main_menu_continue_game_option(self):
        """Continue Game option should lead to apartment (existing save)."""
        main_ui = MainUI()
        menu_screen = MainMenuScreen(main_ui)

        continue_option = next(
            opt for opt in menu_screen.options if opt.text == "Continue Game"
        )
        assert continue_option is not None
        assert continue_option.action == "continue_game"

    def test_main_menu_exit_option(self):
        """Exit option should properly close the game."""
        main_ui = MainUI()
        menu_screen = MainMenuScreen(main_ui)

        exit_option = next(opt for opt in menu_screen.options if opt.text == "Exit")
        assert exit_option is not None
        assert exit_option.action == "exit_game"


class TestCharacterCreationSystem:
    """Test detailed character creation with backgrounds."""

    def test_character_creator_initialization(self):
        """Character creator should load available backgrounds."""
        creator = CharacterCreator()
        assert creator is not None
        assert hasattr(creator, "available_backgrounds")
        assert len(creator.available_backgrounds) >= 3  # detective, survivor, scholar

    def test_character_background_loading(self):
        """Character backgrounds should load from JSON data."""
        creator = CharacterCreator()
        backgrounds = creator.available_backgrounds

        background_ids = [bg.id for bg in backgrounds]
        assert "detective" in background_ids
        assert "survivor" in background_ids
        assert "scholar" in background_ids

    def test_detective_background_properties(self):
        """Detective background should have correct stat modifiers and items."""
        creator = CharacterCreator()
        detective_bg = next(
            bg for bg in creator.available_backgrounds if bg.id == "detective"
        )

        assert detective_bg.display_name == "Detective"
        assert detective_bg.stat_modifiers["perception"] == 2
        assert detective_bg.stat_modifiers["intelligence"] == 1
        assert detective_bg.stat_modifiers["strength"] == -1
        assert "service_revolver" in detective_bg.starting_items
        assert "hungover" in detective_bg.starting_status_effects

    def test_survivor_background_properties(self):
        """Survivor background should have correct stat modifiers and items."""
        creator = CharacterCreator()
        survivor_bg = next(
            bg for bg in creator.available_backgrounds if bg.id == "survivor"
        )

        assert survivor_bg.display_name == "Survivor"
        assert survivor_bg.stat_modifiers["stamina"] == 2
        assert survivor_bg.stat_modifiers["dexterity"] == 2
        assert "survival_knife" in survivor_bg.starting_items
        assert len(survivor_bg.starting_status_effects) == 0

    def test_scholar_background_properties(self):
        """Scholar background should have correct stat modifiers and items."""
        creator = CharacterCreator()
        scholar_bg = next(
            bg for bg in creator.available_backgrounds if bg.id == "scholar"
        )

        assert scholar_bg.display_name == "Scholar"
        assert scholar_bg.stat_modifiers["intelligence"] == 3
        assert scholar_bg.stat_modifiers["mana"] == 2
        assert scholar_bg.stat_modifiers["strength"] == -2
        assert "divine_texts" in scholar_bg.starting_items
        assert "existential_dread" in scholar_bg.starting_status_effects

    def test_character_creation_screen_initialization(self):
        """Character creation screen should display background options."""
        main_ui = MainUI()
        creator = CharacterCreator()
        creation_screen = CharacterCreationScreen(main_ui, creator)

        assert creation_screen.title == "Create Your Character"
        assert len(creation_screen.options) >= 4  # 3 backgrounds + back option

        option_texts = [opt.text for opt in creation_screen.options]
        assert "Detective" in option_texts
        assert "Survivor" in option_texts
        assert "Scholar" in option_texts
        assert "Back to Main Menu" in option_texts

    def test_character_selection_updates_state(self):
        """Selecting a background should update character state."""
        main_ui = MainUI()
        creator = CharacterCreator()

        # Select detective background
        detective_bg = next(
            bg for bg in creator.available_backgrounds if bg.id == "detective"
        )
        character = creator.create_character(detective_bg)

        assert character is not None
        assert character.background_id == "detective"
        assert character.base_stats["perception"] == 12  # 10 base + 2 modifier
        assert character.base_stats["strength"] == 9  # 10 base - 1 modifier


class TestMainMenuIntegration:
    """Test integration between main menu and existing systems."""

    def test_main_menu_replaces_apartment_as_entry(self):
        """Main menu should be the new entry point instead of apartment."""
        main_ui = MainUI()

        # Initial screen should be main menu
        assert isinstance(main_ui.current_screen, MainMenuScreen)
        assert main_ui.current_screen.title == "Broken Divinity - Main Menu"

    def test_continue_game_leads_to_apartment(self):
        """Continue Game should navigate to apartment exploration."""
        main_ui = MainUI()
        main_menu = main_ui.current_screen
        assert isinstance(main_menu, MainMenuScreen)

        continue_option = next(
            opt for opt in main_menu.options if opt.text == "Continue Game"
        )

        # Mock apartment screen transition
        with patch("src.ui.apartment_screen.ApartmentScreen") as mock_apartment:
            main_menu.handle_action(continue_option.action)
            # Should transition to apartment screen
            assert mock_apartment.called

    def test_new_game_leads_to_character_creation(self):
        """New Game should navigate to character creation."""
        main_ui = MainUI()
        main_menu = main_ui.current_screen
        assert isinstance(main_menu, MainMenuScreen)

        new_game_option = next(
            opt for opt in main_menu.options if opt.text == "New Game"
        )

        # Mock character creation screen transition
        with patch(
            "src.ui.character_creation_screen.CharacterCreationScreen"
        ) as mock_creation:
            main_menu.handle_action(new_game_option.action)
            # Should transition to character creation screen
            assert mock_creation.called


class TestCharacterPersistence:
    """Test character data persistence (deferred to next hop)."""

    def test_character_data_structure(self):
        """Character should have proper data structure for future save/load."""
        creator = CharacterCreator()
        detective_bg = next(
            bg for bg in creator.available_backgrounds if bg.id == "detective"
        )
        character = creator.create_character(detective_bg)

        # Character should have serializable data
        assert hasattr(character, "background_id")
        assert hasattr(character, "base_stats")
        assert hasattr(character, "starting_items")
        assert hasattr(character, "starting_abilities")
        assert hasattr(character, "starting_status_effects")

    def test_character_to_dict(self):
        """Character should be convertible to dictionary for saving."""
        creator = CharacterCreator()
        detective_bg = next(
            bg for bg in creator.available_backgrounds if bg.id == "detective"
        )
        character = creator.create_character(detective_bg)

        character_dict = character.to_dict()
        assert isinstance(character_dict, dict)
        assert "background_id" in character_dict
        assert "base_stats" in character_dict
        assert character_dict["background_id"] == "detective"


# Test helper for background JSON validation
class TestCharacterBackgroundValidation:
    """Test that character background JSON files are properly formatted."""

    def test_all_backgrounds_have_required_fields(self):
        """All background JSON files should have required schema fields."""
        creator = CharacterCreator()

        for background in creator.available_backgrounds:
            assert hasattr(background, "id")
            assert hasattr(background, "display_name")
            assert hasattr(background, "description")
            assert hasattr(background, "stat_modifiers")
            assert hasattr(background, "starting_items")

    def test_stat_modifiers_are_integers(self):
        """All stat modifiers should be integer values."""
        creator = CharacterCreator()

        for background in creator.available_backgrounds:
            for stat, modifier in background.stat_modifiers.items():
                assert isinstance(
                    modifier, int
                ), f"Stat {stat} modifier should be integer"

    def test_background_skills_format(self):
        """Background skills should have proper format."""
        creator = CharacterCreator()

        for background in creator.available_backgrounds:
            if hasattr(background, "background_skills"):
                for skill in background.background_skills:
                    assert "name" in skill
                    assert "description" in skill
                    assert "mechanical_effect" in skill


# EOF
