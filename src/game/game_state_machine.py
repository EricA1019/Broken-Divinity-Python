"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Game State Machine                                                          ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Game state management and screen transitions               ║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.9                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Callable

from src.utils.logging import Log
from src.ui.main_ui import MainUI, MenuScreen, MenuOption, StatusData
from src.core.signals import get_signal_bus, CoreSignal


class GameState(Enum):
    """Game states for screen management."""

    MAIN_MENU = "main_menu"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    INVESTIGATION = "investigation"
    CHARACTER = "character"
    INVENTORY = "inventory"
    SETTINGS = "settings"
    SAVE_LOAD = "save_load"
    EXIT = "exit"


@dataclass
class StateTransition:
    """Valid state transition definition."""

    from_state: GameState
    to_state: GameState
    action: str
    description: str


class GameStateMachine:
    """Manages game states and screen transitions."""

    def __init__(self):
        """Initialize game state machine."""
        self.current_state = GameState.MAIN_MENU
        self.previous_state: Optional[GameState] = None
        self.ui = MainUI()
        self.signal_bus = get_signal_bus()

        # Define valid state transitions
        self._setup_transitions()

        # Screen creation methods
        self._screen_creators: Dict[GameState, Callable] = {
            GameState.MAIN_MENU: self._create_main_menu_screen,
            GameState.EXPLORATION: self._create_exploration_screen,
            GameState.COMBAT: self._create_combat_screen,
            GameState.INVESTIGATION: self._create_investigation_screen,
            GameState.CHARACTER: self._create_character_screen,
            GameState.INVENTORY: self._create_inventory_screen,
            GameState.SETTINGS: self._create_settings_screen,
            GameState.SAVE_LOAD: self._create_save_load_screen,
        }

        Log.p(
            "StateMachine",
            [f"Game state machine initialized in {self.current_state.value} state"],
        )

    def _setup_transitions(self) -> None:
        """Setup valid state transitions."""
        self.valid_transitions: List[StateTransition] = [
            # From Main Menu
            StateTransition(
                GameState.MAIN_MENU,
                GameState.EXPLORATION,
                "start_game",
                "Start new game",
            ),
            StateTransition(
                GameState.MAIN_MENU, GameState.SAVE_LOAD, "load_game", "Load saved game"
            ),
            StateTransition(
                GameState.MAIN_MENU, GameState.SETTINGS, "settings", "Game settings"
            ),
            StateTransition(GameState.MAIN_MENU, GameState.EXIT, "exit", "Exit game"),
            # From Exploration
            StateTransition(
                GameState.EXPLORATION,
                GameState.COMBAT,
                "enter_combat",
                "Enter combat encounter",
            ),
            StateTransition(
                GameState.EXPLORATION,
                GameState.INVESTIGATION,
                "investigate",
                "Start investigation",
            ),
            StateTransition(
                GameState.EXPLORATION,
                GameState.CHARACTER,
                "character",
                "View character sheet",
            ),
            StateTransition(
                GameState.EXPLORATION,
                GameState.INVENTORY,
                "inventory",
                "Manage inventory",
            ),
            StateTransition(
                GameState.EXPLORATION, GameState.SETTINGS, "settings", "Game settings"
            ),
            StateTransition(
                GameState.EXPLORATION,
                GameState.SAVE_LOAD,
                "save_game",
                "Save/load game",
            ),
            StateTransition(
                GameState.EXPLORATION,
                GameState.MAIN_MENU,
                "main_menu",
                "Return to main menu",
            ),
            # From Combat
            StateTransition(
                GameState.COMBAT,
                GameState.EXPLORATION,
                "end_combat",
                "End combat encounter",
            ),
            StateTransition(
                GameState.COMBAT,
                GameState.CHARACTER,
                "character",
                "View character sheet",
            ),
            StateTransition(
                GameState.COMBAT, GameState.INVENTORY, "inventory", "Use items"
            ),
            # From Investigation
            StateTransition(
                GameState.INVESTIGATION,
                GameState.EXPLORATION,
                "end_investigation",
                "End investigation",
            ),
            StateTransition(
                GameState.INVESTIGATION,
                GameState.COMBAT,
                "enter_combat",
                "Combat during investigation",
            ),
            StateTransition(
                GameState.INVESTIGATION,
                GameState.CHARACTER,
                "character",
                "View character sheet",
            ),
            # From Character/Inventory/Settings - can go back to previous state
            StateTransition(
                GameState.CHARACTER,
                GameState.EXPLORATION,
                "back",
                "Return to exploration",
            ),
            StateTransition(
                GameState.CHARACTER, GameState.COMBAT, "back", "Return to combat"
            ),
            StateTransition(
                GameState.CHARACTER,
                GameState.INVESTIGATION,
                "back",
                "Return to investigation",
            ),
            StateTransition(
                GameState.INVENTORY,
                GameState.EXPLORATION,
                "back",
                "Return to exploration",
            ),
            StateTransition(
                GameState.INVENTORY, GameState.COMBAT, "back", "Return to combat"
            ),
            StateTransition(
                GameState.INVENTORY,
                GameState.INVESTIGATION,
                "back",
                "Return to investigation",
            ),
            StateTransition(
                GameState.SETTINGS, GameState.MAIN_MENU, "back", "Return to main menu"
            ),
            StateTransition(
                GameState.SETTINGS,
                GameState.EXPLORATION,
                "back",
                "Return to exploration",
            ),
            StateTransition(
                GameState.SAVE_LOAD, GameState.MAIN_MENU, "back", "Return to main menu"
            ),
            StateTransition(
                GameState.SAVE_LOAD,
                GameState.EXPLORATION,
                "back",
                "Return to exploration",
            ),
        ]

    def transition_to(self, new_state: GameState) -> bool:
        """Transition to a new state if valid."""
        if not self.can_transition_to(new_state):
            Log.p(
                "StateMachine",
                [
                    f"Invalid transition from {self.current_state.value} to {new_state.value}"
                ],
            )
            return False

        old_state = self.current_state
        self.previous_state = old_state
        self.current_state = new_state

        Log.p(
            "StateMachine",
            [f"State transition: {old_state.value} -> {new_state.value}"],
        )

        # Emit screen changed signal
        self.signal_bus.emit(
            CoreSignal.SCREEN_CHANGED,
            "GameStateMachine",
            {"from_state": old_state.value, "to_state": new_state.value},
        )

        return True

    def can_transition_to(self, target_state: GameState) -> bool:
        """Check if transition to target state is valid."""
        for transition in self.valid_transitions:
            if (
                transition.from_state == self.current_state
                and transition.to_state == target_state
            ):
                return True
        return False

    def get_valid_transitions(self) -> List[StateTransition]:
        """Get all valid transitions from current state."""
        return [t for t in self.valid_transitions if t.from_state == self.current_state]

    def go_back(self) -> bool:
        """Return to previous state if possible."""
        if self.previous_state is None:
            Log.p("StateMachine", ["Cannot go back - no previous state"])
            return False

        return self.transition_to(self.previous_state)

    def get_current_screen(self) -> MenuScreen:
        """Get the current screen for the active state."""
        creator = self._screen_creators.get(self.current_state)
        if creator:
            return creator()

        # Fallback for unimplemented states
        return MenuScreen(
            title=f"State: {self.current_state.value}",
            description="This screen is not yet implemented.",
            options=[MenuOption("9", "Back", "Return to previous screen")],
        )

    def handle_menu_action(self, action: str) -> bool:
        """Handle menu action and perform state transitions."""
        if self.current_state == GameState.MAIN_MENU:
            return self._handle_main_menu_action(action)
        elif self.current_state == GameState.EXPLORATION:
            return self._handle_exploration_action(action)
        elif self.current_state == GameState.COMBAT:
            return self._handle_combat_action(action)
        elif self.current_state == GameState.INVESTIGATION:
            return self._handle_investigation_action(action)
        elif self.current_state == GameState.CHARACTER:
            return self._handle_character_action(action)
        elif self.current_state == GameState.INVENTORY:
            return self._handle_inventory_action(action)
        elif self.current_state == GameState.SETTINGS:
            return self._handle_settings_action(action)
        elif self.current_state == GameState.SAVE_LOAD:
            return self._handle_save_load_action(action)

        return False

    def _handle_main_menu_action(self, action: str) -> bool:
        """Handle main menu actions."""
        if action == "1":  # Start Game
            return self.transition_to(GameState.EXPLORATION)
        elif action == "2":  # Load Game
            return self.transition_to(GameState.SAVE_LOAD)
        elif action == "3":  # Settings
            return self.transition_to(GameState.SETTINGS)
        elif action == "9":  # Exit
            return self.transition_to(GameState.EXIT)
        return False

    def _handle_exploration_action(self, action: str) -> bool:
        """Handle exploration actions."""
        if action == "1":  # Investigate
            return self.transition_to(GameState.INVESTIGATION)
        elif action == "2":  # Combat
            return self.transition_to(GameState.COMBAT)
        elif action == "4":  # Character
            return self.transition_to(GameState.CHARACTER)
        elif action == "5":  # Inventory
            return self.transition_to(GameState.INVENTORY)
        elif action == "7":  # Settings
            return self.transition_to(GameState.SETTINGS)
        elif action == "8":  # Save Game
            return self.transition_to(GameState.SAVE_LOAD)
        elif action == "9":  # Main Menu
            return self.transition_to(GameState.MAIN_MENU)
        return False

    def _handle_combat_action(self, action: str) -> bool:
        """Handle combat actions."""
        if action == "9":  # End Combat (for testing)
            return self.transition_to(GameState.EXPLORATION)
        return False

    def _handle_investigation_action(self, action: str) -> bool:
        """Handle investigation actions."""
        if action == "9":  # End Investigation
            return self.transition_to(GameState.EXPLORATION)
        return False

    def _handle_character_action(self, action: str) -> bool:
        """Handle character screen actions."""
        if action == "9":  # Back
            return self.go_back()
        return False

    def _handle_inventory_action(self, action: str) -> bool:
        """Handle inventory actions."""
        if action == "9":  # Back
            return self.go_back()
        return False

    def _handle_settings_action(self, action: str) -> bool:
        """Handle settings actions."""
        if action == "9":  # Back
            return self.go_back()
        return False

    def _handle_save_load_action(self, action: str) -> bool:
        """Handle save/load actions."""
        if action == "9":  # Back
            return self.go_back()
        return False

    # Screen creation methods

    def _create_main_menu_screen(self) -> MenuScreen:
        """Create main menu screen."""
        status = StatusData(location="Main Menu", time="--:--", gold=0)

        options = [
            MenuOption("1", "Start Game", "Begin new investigation"),
            MenuOption("2", "Load Game", "Continue saved game"),
            MenuOption("3", "Settings", "Game configuration"),
            MenuOption("9", "Exit", "Quit game"),
        ]

        screen = MenuScreen(
            title="Broken Divinity - Main Menu",
            description="Welcome to Broken Divinity - ASCII Detective Investigation Game\n\nA supernatural mystery awaits your investigation...",
            options=options,
            status=status,
        )

        return screen

    def _create_exploration_screen(self) -> MenuScreen:
        """Create exploration screen stub."""
        status = StatusData(location="Central District", time="14:30", hp=20, max_hp=20)

        options = [
            MenuOption("1", "Investigate", "Begin investigation", enabled=False),
            MenuOption("2", "Combat", "Test combat system"),
            MenuOption("3", "Explore", "Travel to locations", enabled=False),
            MenuOption("4", "Character", "View character sheet"),
            MenuOption("5", "Inventory", "Manage equipment"),
            MenuOption("6", "Abilities", "View abilities", enabled=False),
            MenuOption("7", "Settings", "Game settings"),
            MenuOption("8", "Save Game", "Save/load game"),
            MenuOption("9", "Main Menu", "Return to main menu"),
        ]

        screen = MenuScreen(
            title="Exploration - Central District",
            description="Under Development - Exploration System\n\nThis will be the main exploration interface where you can:\n• Travel between locations\n• Discover investigation sites\n• Encounter random events\n• Manage your detective's activities",
            options=options,
            status=status,
        )

        return screen

    def _create_combat_screen(self) -> MenuScreen:
        """Create combat screen with live battle data if available."""
        # Check if we have an active battle to display
        from src.game.battle_manager import BattleManager

        battle_mgr = BattleManager()

        if battle_mgr.is_battle_active():
            # Create screen with live battle data
            player = battle_mgr.player
            enemies = battle_mgr.get_living_enemies()

            # Update status with player data
            status = StatusData(
                location="Combat: Live Battle",
                time=f"Turn {1}",  # TODO: Get actual turn from turn manager
                hp=player.current_hp if player else 20,
                max_hp=player.max_hp if player else 20,
                mana=player.current_mana if player else 0,
                max_mana=player.max_mana if player else 0,
            )

            # Build description with live battle info
            if player and enemies:
                enemy_names = [e.name for e in enemies]
                enemy_list = ", ".join(enemy_names)
                description = f"⚔️ LIVE COMBAT: {player.name} vs {enemy_list}\n\n"
                description += f"🧙 {player.name}: {player.current_hp}/{player.max_hp} HP, {player.current_mana}/{player.max_mana} MP\n"

                for enemy in enemies:
                    status_icon = "💀" if not enemy.is_alive() else "👹"
                    description += f"{status_icon} {enemy.name}: {enemy.current_hp}/{enemy.max_hp} HP, {enemy.current_mana}/{enemy.max_mana} MP\n"

                description += "\n🎯 Choose your action:"
                title = f"Combat: {player.name} vs {enemy_list}"
            else:
                description = "Combat system ready - no active battle"
                title = "Combat Encounter"
        else:
            # Fallback to demo mode
            status = StatusData(
                location="Combat Encounter", time="Turn 1", hp=20, max_hp=20
            )
            description = "Under Development - Combat System\n\nThis will be the turn-based combat interface featuring:\n• Initiative-based turn order\n• Detective abilities and equipment\n• Status effects and tactical decisions\n• Enemy AI and multiple encounter types"
            title = "Combat Encounter"

        options = [
            MenuOption(
                "1", "Attack", "Basic attack", enabled=battle_mgr.is_battle_active()
            ),
            MenuOption(
                "2", "Defend", "Defensive stance", enabled=battle_mgr.is_battle_active()
            ),
            MenuOption("3", "Take Cover", "Improve defense", enabled=False),
            MenuOption("4", "Use Ability", "Special abilities", enabled=False),
            MenuOption("5", "Use Item", "Consume items", enabled=False),
            MenuOption("6", "Examine", "Study enemy", enabled=False),
            MenuOption("7", "Check Status", "View status effects", enabled=False),
            MenuOption("8", "Attempt Flee", "Try to escape", enabled=False),
            MenuOption("9", "End Combat", "End combat (testing)"),
        ]

        screen = MenuScreen(
            title=title, description=description, options=options, status=status
        )

        return screen

    def _create_investigation_screen(self) -> MenuScreen:
        """Create investigation screen stub."""
        status = StatusData(location="Crime Scene Alpha", time="Evidence: 0/7", gold=0)

        options = [
            MenuOption("1", "Examine Area", "Search for evidence", enabled=False),
            MenuOption("2", "Collect Evidence", "Gather clues", enabled=False),
            MenuOption("3", "Follow Trail", "Track leads", enabled=False),
            MenuOption("4", "Interview", "Question witnesses", enabled=False),
            MenuOption("5", "Check Prints", "Forensic analysis", enabled=False),
            MenuOption("6", "Analyze Clues", "Review evidence", enabled=False),
            MenuOption("7", "Case File", "View case notes", enabled=False),
            MenuOption("8", "Contact Backup", "Call for help", enabled=False),
            MenuOption("9", "Leave Scene", "End investigation"),
        ]

        screen = MenuScreen(
            title="Investigation - Crime Scene",
            description="Under Development - Investigation System\n\nThis will be the investigation interface featuring:\n• Evidence collection and analysis\n• Witness interviews and interrogation\n• Clue correlation and deduction\n• Case file management and progression",
            options=options,
            status=status,
        )

        return screen

    def _create_character_screen(self) -> MenuScreen:
        """Create character screen stub."""
        status = StatusData(location="Character Sheet", time="Level 1", gold=0)

        options = [
            MenuOption("1", "Allocate Points", "Distribute stat points", enabled=False),
            MenuOption("2", "Review Stats", "View attributes", enabled=False),
            MenuOption("3", "Equipment", "Manage gear", enabled=False),
            MenuOption("4", "Abilities", "Skill management", enabled=False),
            MenuOption("5", "Inventory", "View items", enabled=False),
            MenuOption("6", "Save Character", "Save progress", enabled=False),
            MenuOption("7", "Progression", "Level history", enabled=False),
            MenuOption("8", "Case History", "Past investigations", enabled=False),
            MenuOption("9", "Return", "Go back"),
        ]

        screen = MenuScreen(
            title="Character Sheet - Detective",
            description="Under Development - Character Management\n\nThis will be the character progression interface featuring:\n• Stat allocation and upgrades\n• Equipment and gear management\n• Ability point distribution\n• Experience tracking and level progression",
            options=options,
            status=status,
        )

        return screen

    def _create_inventory_screen(self) -> MenuScreen:
        """Create inventory screen stub."""
        status = StatusData(location="Inventory", time="Items: 0/20", gold=0)

        options = [
            MenuOption("1", "View Items", "List all items", enabled=False),
            MenuOption("2", "Use Item", "Consume/equip", enabled=False),
            MenuOption("3", "Drop Item", "Remove from inventory", enabled=False),
            MenuOption("4", "Equipment", "Manage gear", enabled=False),
            MenuOption("5", "Sort Items", "Organize inventory", enabled=False),
            MenuOption("6", "Item Details", "Examine closely", enabled=False),
            MenuOption("7", "Quick Use", "Fast access items", enabled=False),
            MenuOption("8", "Trade/Shop", "Buy/sell items", enabled=False),
            MenuOption("9", "Return", "Go back"),
        ]

        screen = MenuScreen(
            title="Inventory & Equipment",
            description="Under Development - Inventory System\n\nThis will be the inventory management interface featuring:\n• Item storage and organization\n• Equipment durability tracking\n• Weapon and gear customization\n• Trading and shop interactions",
            options=options,
            status=status,
        )

        return screen

    def _create_settings_screen(self) -> MenuScreen:
        """Create settings screen stub."""
        status = StatusData(location="Settings", time="v0.0.9", gold=0)

        options = [
            MenuOption("1", "Display", "Screen settings", enabled=False),
            MenuOption("2", "Audio", "Sound settings", enabled=False),
            MenuOption("3", "Controls", "Key bindings", enabled=False),
            MenuOption("4", "Gameplay", "Game options", enabled=False),
            MenuOption("5", "Accessibility", "Access options", enabled=False),
            MenuOption("6", "Graphics", "Visual settings", enabled=False),
            MenuOption("7", "Save Settings", "Apply changes", enabled=False),
            MenuOption("8", "Reset Defaults", "Restore defaults", enabled=False),
            MenuOption("9", "Return", "Go back"),
        ]

        screen = MenuScreen(
            title="Game Settings",
            description="Under Development - Settings System\n\nThis will be the configuration interface featuring:\n• Display and graphics options\n• Audio and sound settings\n• Control customization\n• Accessibility features",
            options=options,
            status=status,
        )

        return screen

    def _create_save_load_screen(self) -> MenuScreen:
        """Create save/load screen stub."""
        status = StatusData(location="Save/Load", time="Slot Status", gold=0)

        options = [
            MenuOption("1", "Quick Save", "Save to slot 1", enabled=False),
            MenuOption("2", "Save Game", "Choose save slot", enabled=False),
            MenuOption("3", "Load Game", "Choose load slot", enabled=False),
            MenuOption("4", "Delete Save", "Remove save file", enabled=False),
            MenuOption("5", "Save Info", "View save details", enabled=False),
            MenuOption("6", "Export Save", "Backup save file", enabled=False),
            MenuOption("7", "Import Save", "Restore save file", enabled=False),
            MenuOption("8", "Auto Save", "Configure auto save", enabled=False),
            MenuOption("9", "Return", "Go back"),
        ]

        screen = MenuScreen(
            title="Save & Load Game",
            description="Under Development - Save System\n\nThis will be the save/load interface featuring:\n• Multiple save slot management\n• Auto-save functionality\n• Save file backup and restore\n• Game state preservation",
            options=options,
            status=status,
        )

        return screen


# EOF
