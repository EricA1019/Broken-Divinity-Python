"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Character Creation Screen                                                   ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019               ║
║  Purpose       : Character background selection and customization           ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.12                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
from typing import List

from src.ui.main_ui import MenuOption, MenuScreen
from src.game.character_creation import CharacterCreator, CharacterBackground

log = logging.getLogger("[CharCreate]")


class CharacterCreationScreen(MenuScreen):
    """Character creation screen with background selection."""

    def __init__(self, main_ui, character_creator: CharacterCreator):
        """Initialize character creation screen."""
        initial_description = """Choose your character's background:

Each background provides unique abilities, starting items, and role-playing opportunities.
Your choice will affect how NPCs react to you and what options are available during investigations."""

        super().__init__("Create Your Character", description=initial_description)
        self.main_ui = main_ui
        self.character_creator = character_creator
        self.selected_background = None
        self.options = self._build_background_options()
        log.info("Character creation screen initialized")

    def _build_background_options(self) -> List[MenuOption]:
        """Build menu options for background selection."""
        options = []

        # Add background options
        for i, background in enumerate(self.character_creator.available_backgrounds, 1):
            options.append(
                MenuOption(str(i), background.display_name, f"select_{background.id}")
            )

        # Add back option
        options.append(
            MenuOption(str(len(options) + 1), "Back to Main Menu", "back_to_main")
        )

        log.debug(f"Built {len(options)} character creation options")
        return options

    def handle_action(self, action: str) -> None:
        """Handle character creation actions."""
        log.debug(f"Handling action: {action}")

        if action.startswith("select_"):
            background_id = action.replace("select_", "")
            self._select_background(background_id)
        elif action == "back_to_main":
            self._back_to_main_menu()
        else:
            log.warning(f"Unknown action: {action}")

    def _select_background(self, background_id: str) -> None:
        """Select a character background and create character."""
        log.info(f"Selected background: {background_id}")

        # Find the selected background
        background = next(
            (
                bg
                for bg in self.character_creator.available_backgrounds
                if bg.id == background_id
            ),
            None,
        )

        if not background:
            log.error(f"Background not found: {background_id}")
            return

        # Update screen description with background details
        self.description = f"""
Selected: {background.display_name}

{background.description}

{background.flavor_text}

Starting Benefits:
• Abilities: {', '.join(background.starting_abilities) if background.starting_abilities else 'None'}
• Items: {', '.join(background.starting_items) if background.starting_items else 'None'}
• Status Effects: {', '.join(background.starting_status_effects) if background.starting_status_effects else 'None'}

Creating character...
"""

        log.info(f"Character background selected: {background.display_name}")
        log.debug(f"Background description: {background.description}")

        # Store the selected background
        self.selected_background = background

        # Create character with selected background
        character = self.character_creator.create_character(background)

        # Store character data (for now, we'll just transition to apartment)
        # TODO: In next hop, integrate with save system
        log.info(f"Character created, transitioning to apartment")
        self._start_game_with_character(character)

    def _start_game_with_character(self, character) -> None:
        """Start the game with the created character."""
        from src.ui.apartment_screen import ApartmentScreen
        from src.game.locations import ApartmentLocation
        from src.game.character_state import CharacterState

        # Initialize game state with character
        character_state = CharacterState()

        # Apply starting status effects
        for status_id in character.starting_status_effects:
            character_state.apply_status_effect(status_id)
            log.debug(f"Applied starting status effect: {status_id}")

        apartment = ApartmentLocation()
        apartment_screen = ApartmentScreen(apartment)
        # Note: We'll need to pass character_state to apartment in future

        self.main_ui.change_screen(apartment_screen)

    def _back_to_main_menu(self) -> None:
        """Return to main menu."""
        log.info("Returning to main menu")
        from src.ui.main_menu_screen import MainMenuScreen

        main_menu = MainMenuScreen(self.main_ui)
        self.main_ui.change_screen(main_menu)


# EOF
