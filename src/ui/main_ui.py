"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Main UI Framework - Numbered Menu System                                   ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Core UI framework with tcod rendering and numbered menus   ║
║  Last-Updated  : 2025-08-04                                                 ║
║  Version       : v0.0.8                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass, field, field
from enum import Enum
from typing import List, Dict, Any, Optional, Callable, Tuple
import textwrap

import tcod
import tcod.console
import tcod.context
import tcod.tileset
import tcod.event
from abc import ABC, abstractmethod

from src.core.signals import get_signal_bus, CoreSignal
from src.utils.logging import Log


class ScreenState(Enum):
    """Possible screen states for the UI system."""

    MAIN_MENU = "main_menu"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    INVENTORY = "inventory"
    CHARACTER = "character"
    SETTINGS = "settings"


@dataclass
class MenuOption:
    """A single menu option with key, text, and action."""

    key: str
    text: str
    action: str
    enabled: bool = True
    description: Optional[str] = None
    hotkey: Optional[str] = None
    disabled_reason: Optional[str] = None


@dataclass
class StatusData:
    """Data for the status header display."""

    location: str = "Unknown Location"
    gold: int = 0
    time: str = "00:00"
    day: int = 1
    hp: int = 100
    max_hp: int = 100
    mana: int = 50
    max_mana: int = 50
    ammo: int = 12
    character_name: Optional[str] = None
    health: Optional[Tuple[int, int]] = None  # (current, max)
    mana_tuple: Optional[Tuple[int, int]] = (
        None  # (current, max) - different from mana field
    )


@dataclass
class UIConfig:
    """Configuration for the UI system."""

    width: int = 120  # Larger width for more detailed display
    height: int = 50  # Larger height for more content
    screen_width: int = 120  # Keep both for compatibility
    screen_height: int = 50
    border_style: str = "double"
    show_timestamps: bool = False
    border_char_horizontal: str = "═"
    border_char_vertical: str = "║"
    border_char_corner_tl: str = "╔"
    border_char_corner_tr: str = "╗"
    border_char_corner_bl: str = "╚"
    border_char_corner_br: str = "╝"
    border_char_junction_t: str = "╦"
    border_char_junction_b: str = "╩"
    border_char_junction_l: str = "╠"
    border_char_junction_r: str = "╣"
    status_height: int = 3
    menu_height: int = 5  # Increased to 5 to accommodate the "More Options" line
    main_area_color: Tuple[int, int, int] = (
        255,
        255,
        255,
    )  # Bright white for main text
    border_color: Tuple[int, int, int] = (180, 180, 180)  # Brighter gray for borders
    menu_color: Tuple[int, int, int] = (220, 220, 255)  # Brighter blue for menus
    status_color: Tuple[int, int, int] = (255, 255, 160)  # Brighter yellow for status

    def __post_init__(self):
        """Sync width/height with screen_width/screen_height."""
        self.screen_width = self.width
        self.screen_height = self.height


class MenuScreen:
    """A complete menu screen with title, status, and options."""

    def __init__(
        self,
        title: str,
        arg2=None,
        arg3=None,
        status: Optional[StatusData] = None,
        description: str = "",
        options: Optional[List[MenuOption]] = None,
    ):
        """Initialize screen with flexible constructor for backwards compatibility."""
        self.title = title
        self.content_lines = []

        # Handle different calling patterns
        if options is not None:
            # MenuScreen(title="...", options=[...], description="...", ...)
            self.options = options
            self.description = description
            self.status = status
        elif isinstance(arg2, list):
            # MenuScreen(title, options, ...)
            self.options = arg2
            self.description = description
            self.status = status
        elif isinstance(arg2, str) and isinstance(arg3, list):
            # MenuScreen(title, description, options)
            self.description = arg2
            self.options = arg3
            self.status = status
        elif arg2 is None:
            # MenuScreen(title, [], ...)
            self.options = []
            self.description = description
            self.status = status
        else:
            # Fallback
            self.options = arg2 if isinstance(arg2, list) else []
            self.description = description
            self.status = status

        # Expandable menu support
        self.menu_page = 0
        self.max_visible_options = 9  # Show 1-9, use 0 for next page
        self.all_options = self.options.copy() if self.options else []

        # Update visible options
        self._update_visible_options()

    def _update_visible_options(self) -> None:
        """Update visible options based on current page."""
        start_idx = self.menu_page * self.max_visible_options
        end_idx = start_idx + self.max_visible_options

        # Get options for this page
        page_options = self.all_options[start_idx:end_idx]

        # Reassign keys 1-9 for this page
        for i, option in enumerate(page_options):
            option.key = str(i + 1)

        # Add "next page" option if there are more options
        if end_idx < len(self.all_options):
            next_page_option = MenuOption(
                "0", f"More Options... (Page {self.menu_page + 2})", "next_menu_page"
            )
            page_options.append(next_page_option)

        self.options = page_options

    def next_menu_page(self) -> None:
        """Go to the next page of menu options."""
        max_page = (len(self.all_options) - 1) // self.max_visible_options
        if self.menu_page < max_page:
            self.menu_page += 1
            self._update_visible_options()

    def add_option(self, option: MenuOption) -> None:
        """Add a menu option to this screen."""
        self.all_options.append(option)
        self._update_visible_options()

    def add_content_line(self, line: str) -> None:
        """Add a line of content to the main text area."""
        self.content_lines.append(line)

    def get_option(self, key: str) -> Optional[MenuOption]:
        """Get option by key."""
        return self.get_option_by_key(key)

    def get_enabled_options(self) -> List[MenuOption]:
        """Get all enabled options."""
        return [opt for opt in self.options if opt.enabled]

    def clear_content(self) -> None:
        """Clear all content lines."""
        self.content_lines.clear()

    def get_option_by_key(self, key: str) -> Optional[MenuOption]:
        """Get a menu option by its key."""
        for option in self.options:
            if option.key == key and option.enabled:
                return option
        return None


class InputHandler:
    """Handles keyboard and mouse input for the UI."""

    def __init__(self, current_screen: Optional[MenuScreen] = None):
        """Initialize input handler."""
        self.current_screen = current_screen

    def process_input(self, key: str) -> Optional[MenuOption]:
        """Process a key input and return the corresponding menu option."""
        if not self.current_screen:
            return None

        option = self.current_screen.get_option(key)
        if option and option.enabled:
            return option
        return None

    def handle_event(self, event: tcod.event.Event) -> Optional[str]:
        """Handle a tcod event and return action if any."""
        if isinstance(event, tcod.event.KeyDown):
            return self.handle_keydown(event)
        return None

    def handle_keydown(self, event: tcod.event.KeyDown) -> Optional[str]:
        """Handle keydown events."""
        key_sym = event.sym

        # Handle number keys (0-9)
        if tcod.event.KeySym.N0 <= key_sym <= tcod.event.KeySym.N9:
            number = str(key_sym - tcod.event.KeySym.N0)
            return f"menu_option_{number}"

        # Handle escape
        if key_sym == tcod.event.K_ESCAPE:
            return "escape"

        # Handle enter
        if key_sym == tcod.event.K_RETURN:
            return "enter"

        # Handle common hotkeys
        if key_sym == tcod.event.K_f:
            return "fight"
        elif key_sym == tcod.event.K_d:
            return "defend"
        elif key_sym == tcod.event.K_i:
            return "inventory"
        elif key_sym == tcod.event.K_a:
            return "ability"

        return None


class MainUI:
    """Main UI framework class using tcod for rendering."""

    def __init__(self, config: Optional[UIConfig] = None):
        """Initialize the main UI."""
        self.config = config or UIConfig()
        self.console: Optional[tcod.Console] = None
        self.context: Optional[tcod.context.Context] = None
        self.status_data = StatusData()
        self.input_handler = InputHandler()
        self.running = True
        self.current_state = ScreenState.MAIN_MENU
        self.should_exit = False

        # Import here to avoid circular imports
        from src.ui.main_menu_screen import MainMenuScreen

        self.current_screen: Optional[MenuScreen] = MainMenuScreen(self)

        Log.p("MainUI", ["UI framework initialized"])

    def initialize(self) -> None:
        """Initialize the tcod console and context for graphical display."""
        Log.p(
            "MainUI",
            [
                f"Initializing {self.config.screen_width}x{self.config.screen_height} graphical window..."
            ],
        )

        # Create console using new API
        self.console = tcod.console.Console(
            self.config.screen_width, self.config.screen_height
        )

        try:
            # Try to load a built-in truetype font for better graphics and readability
            tileset = None

            # Try to use a system monospace font with larger size for better readability
            try:
                tileset = tcod.tileset.load_truetype_font(
                    "DejaVuSansMono-Bold.ttf",  # Use bold variant for better visibility
                    0,
                    18,  # Increased font size for better readability
                )
                Log.p("MainUI", ["Loaded DejaVu Sans Mono Bold font"])
            except:
                try:
                    # Fallback to regular DejaVu Sans Mono but larger
                    tileset = tcod.tileset.load_truetype_font(
                        "DejaVuSansMono.ttf",
                        0,
                        18,  # Increased font size
                    )
                    Log.p("MainUI", ["Loaded DejaVu Sans Mono font (regular)"])
                except:
                    try:
                        # Fallback to another common font
                        tileset = tcod.tileset.load_truetype_font(
                            "LiberationMono-Bold.ttf",
                            0,
                            18,
                        )
                        Log.p("MainUI", ["Loaded Liberation Mono Bold font"])
                    except:
                        try:
                            # Try regular Liberation Mono
                            tileset = tcod.tileset.load_truetype_font(
                                "LiberationMono-Regular.ttf",
                                0,
                                18,
                            )
                            Log.p("MainUI", ["Loaded Liberation Mono font"])
                        except:
                            # Final fallback - no tileset (use default)
                            tileset = None
                            Log.p("MainUI", ["Using default font"])

            # Create graphical context
            self.context = tcod.context.new(
                columns=self.config.screen_width,
                rows=self.config.screen_height,
                tileset=tileset,
                title="🎮 Broken Divinity - ASCII Roguelike",
                vsync=True,
            )
            Log.p("MainUI", ["Graphical window created successfully"])

        except Exception as e:
            Log.p("MainUI", [f"Graphics initialization failed: {e}"])
            # Fall back to text mode
            self._run_text_mode()
            return

        Log.p("MainUI", ["Console and context initialized for graphical display"])

    def _font_exists(self) -> bool:
        """Check if custom font file exists."""
        try:
            from pathlib import Path

            return Path("data/fonts/terminal.png").exists()
        except:
            return False

    def set_screen(self, screen: MenuScreen) -> None:
        """Set the current screen to display."""
        self.current_screen = screen
        Log.p("MainUI", [f"Screen changed to: {screen.title}"])

    def change_screen(self, screen: MenuScreen) -> None:
        """Change to a new screen (alias for set_screen)."""
        self.set_screen(screen)

    def push_screen(self, screen: MenuScreen) -> None:
        """Push a new screen onto the screen stack."""
        if not hasattr(self, "screen_stack"):
            self.screen_stack = []
        if self.current_screen:
            self.screen_stack.append(self.current_screen)
        self.set_screen(screen)

    def pop_screen(self) -> Optional[MenuScreen]:
        """Pop the current screen and return to the previous one."""
        if not hasattr(self, "screen_stack") or not self.screen_stack:
            return None
        previous_screen = self.screen_stack.pop()
        self.set_screen(previous_screen)
        return previous_screen

    def update_status(self, status_data: StatusData) -> None:
        """Update the status bar data."""
        self.status_data = status_data

    def update_dynamic_status(self) -> None:
        """Update status with dynamic information like current location and time."""
        if not self.status_data:
            return

        # Update location based on current screen
        if self.current_screen:
            new_location = self._get_location_from_screen(self.current_screen.title)
            if new_location != self.status_data.location:
                self.status_data.location = new_location

        # Update time (increment by 1 minute each render for now)
        self._increment_time()

    def _get_location_from_screen(self, screen_title: str) -> str:
        """Get location name based on current screen title."""
        location_map = {
            "Broken Divinity - Main Menu": "Detective Bureau",
            "Character Creation": "Detective Bureau - Personnel",
            "Character Background Selection": "Detective Bureau - Personnel",
            "Detective Apartment": "Your Apartment",
            "Combat": "Crime Scene",
            "Exploration": "Investigation Site",
            "Investigation": "Investigation Site",
            "Equipment": "Equipment Room",
            "Inventory": "Equipment Room",
        }

        for key, location in location_map.items():
            if key in screen_title:
                return location

        return "Unknown Location"

    def _increment_time(self) -> None:
        """Increment game time by small amounts."""
        if not self.status_data.time:
            self.status_data.time = "08:00"
            return

        try:
            # Parse current time
            hours, minutes = map(int, self.status_data.time.split(":"))

            # Increment by 1 minute (you can adjust this)
            minutes += 1
            if minutes >= 60:
                minutes = 0
                hours += 1
                if hours >= 24:
                    hours = 0
                    self.status_data.day += 1

            # Format back to string
            self.status_data.time = f"{hours:02d}:{minutes:02d}"
        except (ValueError, AttributeError):
            # If parsing fails, reset to default
            self.status_data.time = "08:00"

    def render(self) -> None:
        """Render the current UI state to the console."""
        # Update dynamic status information
        self.update_dynamic_status()

        if not self.console:
            # Fallback for testing: render to print
            self._render_to_print()
            return

        # Clear console
        self.console.clear()

        # Render components
        self._render_borders()
        self._render_status_header()
        self._render_main_content()
        self._render_menu_area()

        # Present to screen
        if self.context:
            self.context.present(self.console)

    def _render_to_print(self) -> None:
        """Render UI state using print for testing."""
        if not self.current_screen:
            return

        # Render status data
        if self.status_data:
            status_text = (
                f"Location: {self.status_data.location}    "
                f"Gold: {self.status_data.gold:,}    "
                f"Time: {self.status_data.time} Day {self.status_data.day}"
            )
            print(status_text)

        # Render screen title
        print(f"=== {self.current_screen.title} ===")

        # Render description
        if self.current_screen.description:
            print(self.current_screen.description)

        # Render options
        for option in self.current_screen.options:
            if option.enabled:
                print(f"{option.key}. {option.text}")
            else:
                disabled_note = (
                    f" ({option.disabled_reason})"
                    if option.disabled_reason
                    else " (disabled)"
                )
                print(f"{option.key}. {option.text}{disabled_note}")

        # Render content lines
        for line in self.current_screen.content_lines:
            print(line)

    def _render_borders(self) -> None:
        """Render the ASCII borders around UI regions."""
        if not self.console:
            return

        w, h = self.config.screen_width, self.config.screen_height
        status_h = self.config.status_height
        menu_h = self.config.menu_height

        # Top border (around status)
        self._draw_horizontal_border(0, 0, w)
        self._draw_horizontal_border(0, status_h - 1, w)

        # Middle border (separating content from menu)
        menu_start = h - menu_h
        self._draw_horizontal_border(0, menu_start - 1, w)

        # Bottom border
        self._draw_horizontal_border(0, h - 1, w)

        # Vertical borders
        for y in range(h):
            self.console.print(
                0, y, self.config.border_char_vertical, fg=self.config.border_color
            )
            self.console.print(
                w - 1, y, self.config.border_char_vertical, fg=self.config.border_color
            )

        # Corner and junction characters
        self._draw_border_junctions(w, h, status_h, menu_h)

    def _draw_horizontal_border(self, x: int, y: int, width: int) -> None:
        """Draw a horizontal border line."""
        if not self.console:
            return

        for i in range(1, width - 1):
            self.console.print(
                x + i,
                y,
                self.config.border_char_horizontal,
                fg=self.config.border_color,
            )

    def _draw_border_junctions(
        self, w: int, h: int, status_h: int, menu_h: int
    ) -> None:
        """Draw corner and junction characters."""
        if not self.console:
            return

        # Top corners
        self.console.print(
            0, 0, self.config.border_char_corner_tl, fg=self.config.border_color
        )
        self.console.print(
            w - 1, 0, self.config.border_char_corner_tr, fg=self.config.border_color
        )

        # Bottom corners
        self.console.print(
            0, h - 1, self.config.border_char_corner_bl, fg=self.config.border_color
        )
        self.console.print(
            w - 1, h - 1, self.config.border_char_corner_br, fg=self.config.border_color
        )

        # Status area junctions
        self.console.print(
            0,
            status_h - 1,
            self.config.border_char_junction_l,
            fg=self.config.border_color,
        )
        self.console.print(
            w - 1,
            status_h - 1,
            self.config.border_char_junction_r,
            fg=self.config.border_color,
        )

        # Menu area junctions
        menu_start = h - menu_h
        self.console.print(
            0,
            menu_start - 1,
            self.config.border_char_junction_l,
            fg=self.config.border_color,
        )
        self.console.print(
            w - 1,
            menu_start - 1,
            self.config.border_char_junction_r,
            fg=self.config.border_color,
        )

    def _render_status_header(self) -> None:
        """Render the status header with location, gold, time, etc."""
        if not self.console:
            return

        status_text = (
            f" Location: {self.status_data.location}    "
            f"Gold: {self.status_data.gold:,}    "
            f"Time: {self.status_data.time} Day {self.status_data.day}"
        )

        # HP/Mana bar on second line
        hp_text = f" HP: {self.status_data.hp}/{self.status_data.max_hp}    "
        mana_text = f"Mana: {self.status_data.mana}/{self.status_data.max_mana}    "
        ammo_text = f"Ammo: {self.status_data.ammo}"

        stats_text = hp_text + mana_text + ammo_text

        # Render status lines
        self.console.print(2, 1, status_text, fg=self.config.status_color)
        self.console.print(2, 2, stats_text, fg=self.config.status_color)

    def _render_main_content(self) -> None:
        """Render the main content area."""
        if not self.console or not self.current_screen:
            return

        start_y = self.config.status_height
        end_y = self.config.screen_height - self.config.menu_height
        content_height = end_y - start_y - 1

        # Render screen title if present
        y_offset = start_y + 1
        if self.current_screen.title:
            title_line = f"=== {self.current_screen.title} ==="
            self.console.print(2, y_offset, title_line, fg=self.config.main_area_color)
            y_offset += 2

        # Render description if present
        if self.current_screen.description:
            # Use text wrapping for description
            wrapped_lines = textwrap.wrap(
                self.current_screen.description, width=self.config.screen_width - 4
            )
            for i, line in enumerate(wrapped_lines):
                if y_offset + i < end_y - 1:
                    self.console.print(
                        2, y_offset + i, line, fg=self.config.main_area_color
                    )
            y_offset += len(wrapped_lines) + 1

        # Render content lines
        for i, line in enumerate(self.current_screen.content_lines):
            if y_offset + i < end_y - 1:
                self.console.print(
                    2, y_offset + i, line, fg=self.config.main_area_color
                )

    def _render_menu_area(self) -> None:
        """Render the menu options at the bottom."""
        if not self.console or not self.current_screen:
            return

        menu_start_y = self.config.screen_height - self.config.menu_height + 1

        # Arrange options in 3 columns
        col_width = (self.config.screen_width - 4) // 3

        for i, option in enumerate(
            self.current_screen.options
        ):  # Iterate through all visible options
            if not option.enabled:
                continue

            col = i % 3
            row = i // 3
            x = 2 + (col * col_width)
            y = menu_start_y + row

            if y >= self.config.screen_height - 1:
                break

            option_text = f"{option.key}. {option.text}"
            color = self.config.menu_color if option.enabled else (100, 100, 100)

            self.console.print(x, y, option_text, fg=color)

    def _generate_border_line(self, width: int, style: str, position: str) -> str:
        """Generate a border line with the specified style and position.

        Args:
            width: Width of the border line
            style: "single", "double", or "thick"
            position: "top", "middle", "bottom"
        """
        if style == "single":
            chars = {
                "top": ("┌", "─", "┐"),
                "middle": ("├", "─", "┤"),
                "bottom": ("└", "─", "┘"),
            }
        elif style == "double":
            chars = {
                "top": ("╔", "═", "╗"),
                "middle": ("╠", "═", "╣"),
                "bottom": ("╚", "═", "╝"),
            }
        else:  # thick
            chars = {
                "top": ("┏", "━", "┓"),
                "middle": ("┣", "━", "┫"),
                "bottom": ("┗", "━", "┛"),
            }

        left, middle, right = chars[position]
        return left + middle * (width - 2) + right

    def _render_menu_options(
        self, options: List[MenuOption], columns: int = 1
    ) -> List[str]:
        """Render menu options in the specified number of columns.

        Args:
            options: List of menu options to render
            columns: Number of columns to arrange options in

        Returns:
            List of formatted strings representing the menu
        """
        if not options:
            return []

        lines = []
        option_groups = [
            options[i : i + columns] for i in range(0, len(options), columns)
        ]

        for group in option_groups:
            line_parts = []
            for option in group:
                if option.enabled:
                    part = f"{option.key}. {option.text}"
                else:
                    disabled_note = (
                        f" ({option.disabled_reason})"
                        if option.disabled_reason
                        else " (disabled)"
                    )
                    part = f"{option.key}. {option.text}{disabled_note}"
                line_parts.append(part)
            lines.append("  ".join(line_parts))

        return lines

    def handle_input(self) -> Optional[str]:
        """Handle input events and return action if any."""
        if not self.context:
            return None

        for event in tcod.event.wait():
            if event.type == "QUIT":
                self.running = False
                return "quit"

            action = self.input_handler.handle_event(event)
            if action:
                Log.p("MainUI", [f"Input action: {action}"])
                return action

        return None

    def process_action(self, action: str) -> bool:
        """Process an action and return whether it was handled."""
        if not self.current_screen:
            return False

        # Handle menu option selections
        if action.startswith("menu_option_"):
            key = action.split("_")[-1]
            option = self.current_screen.get_option_by_key(key)
            if option:
                Log.p(
                    "WarsimUI",
                    [f"Menu option selected: {option.text} ({option.action})"],
                )
                # Emit signal for action
                signal_bus = get_signal_bus()
                signal_bus.emit(
                    CoreSignal.UI_ACTION,
                    "WarsimUI",
                    {
                        "action": option.action,
                        "option": option.text,
                        "screen": self.current_screen.title,
                    },
                )

                # Route action to current screen handler
                if option.action == "next_menu_page":
                    self.current_screen.next_menu_page()
                elif hasattr(self.current_screen, "handle_action"):
                    self.current_screen.handle_action(option.action)
                else:
                    Log.p(
                        "MainUI",
                        [
                            f"Screen {self.current_screen.title} has no handle_action method"
                        ],
                    )

                return True

        # Handle other actions
        elif action == "escape":
            Log.p("MainUI", ["Escape pressed"])
            return True

        return False

    def process_input(self, key: str) -> Optional[str]:
        """Process a key input and return the corresponding action."""
        if not self.current_screen:
            return None

        option = self.current_screen.get_option(key)
        if option and option.enabled:
            return option.action
        return None

    def run_main_loop(self) -> None:
        """Run the main UI loop."""
        if not self.context:
            self.initialize()

        # If context is still None after initialization, run in text mode
        if not self.context:
            Log.p("MainUI", ["Running in text-only mode (no graphics context)"])
            self._run_text_mode()
            return

        Log.p("MainUI", ["Starting main UI loop"])

        while self.running:
            self.render()
            action = self.handle_input()

            if action:
                self.process_action(action)

        Log.p("MainUI", ["Main UI loop ended"])

    def _run_text_mode(self) -> None:
        """Run the game in text-only mode for terminal display."""
        print("\n" + "=" * 60)
        print("🎮 BROKEN DIVINITY - ASCII ROGUELIKE")
        print("=" * 60)

        try:
            while self.running and not self.should_exit:
                # Clear screen and show current screen
                print("\n" * 2)  # Add some spacing

                if self.current_screen:
                    # Display screen title
                    print(f"📍 {self.current_screen.title}")
                    print("-" * len(self.current_screen.title))

                    # Display menu options
                    if (
                        hasattr(self.current_screen, "options")
                        and self.current_screen.options
                    ):
                        print("\nAvailable Actions:")
                        for i, option in enumerate(self.current_screen.options, 1):
                            status = "✓" if option.enabled else "✗"
                            print(f"  {i}. {status} {option.text}")

                    # Display status if available
                    if self.status_data:
                        print(
                            f"\n📊 Status: {self.status_data.location} | "
                            f"HP: {self.status_data.hp}/{self.status_data.max_hp} | "
                            f"Gold: {self.status_data.gold}"
                        )

                print(f"\n💬 Game running in text mode. Press Ctrl+C to exit.")
                print(f"⏳ Main menu system is active...")

                # Simple sleep loop with exit check
                import time

                time.sleep(2)

        except KeyboardInterrupt:
            Log.p("MainUI", ["Game interrupted by user"])
            print("\n🔚 Game ended by user. Thanks for playing!")
            self.running = False

    def shutdown(self) -> None:
        """Clean shutdown of the UI system."""
        self.running = False
        if self.context:
            self.context.close()
        Log.p("MainUI", ["UI framework shutdown"])


# Factory functions for common screens
def create_main_menu_screen() -> MenuScreen:
    """Create the main menu screen."""
    screen = MenuScreen("Main Menu", [], description="Welcome to Broken Divinity")
    screen.add_option(MenuOption("1", "Start Investigation", "start_game"))
    screen.add_option(MenuOption("2", "Load Game", "load_game"))
    screen.add_option(MenuOption("3", "Settings", "settings"))
    screen.add_option(MenuOption("4", "Quit", "quit"))
    return screen


def create_exploration_screen() -> MenuScreen:
    """Create a basic exploration screen."""
    screen = MenuScreen(
        "Downtown Alley", [], description="A narrow alley between two buildings..."
    )
    screen.add_option(MenuOption("1", "Examine Area", "examine"))
    screen.add_option(MenuOption("2", "Search for Clues", "search"))
    screen.add_option(MenuOption("3", "Talk to NPC", "talk"))
    screen.add_option(MenuOption("4", "Enter Building", "enter"))
    screen.add_option(MenuOption("5", "Character Stats", "character"))
    screen.add_option(MenuOption("6", "Inventory", "inventory"))
    screen.add_option(MenuOption("7", "Settings", "settings"))
    return screen


def create_combat_screen() -> MenuScreen:
    """Create a combat screen with F-D-I-A options."""
    screen = MenuScreen(
        "Combat", [], description="You are in combat with hostile entities!"
    )
    screen.add_option(MenuOption("1", "Fight", "combat_fight", hotkey="f"))
    screen.add_option(MenuOption("2", "Defend", "combat_defend", hotkey="d"))
    screen.add_option(MenuOption("3", "Inventory", "combat_inventory", hotkey="i"))
    screen.add_option(MenuOption("4", "Use Ability", "combat_ability", hotkey="a"))
    screen.add_option(MenuOption("5", "Flee", "combat_flee"))
    return screen


# EOF
