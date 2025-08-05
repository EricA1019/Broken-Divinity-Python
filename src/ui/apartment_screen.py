"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Apartment Screen                                                            ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Apartment exploration screen using MainUI framework        ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.11                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
from pathlib import Path
from typing import List, Dict

from src.ui.main_ui import MenuScreen, MenuOption
from src.utils.logging import Log


class ApartmentScreen(MenuScreen):
    """A data-driven screen for exploring Morrison's apartment."""

    def __init__(self, location_file: str = "data/locations/apartment.json"):
        self.tag = "ApartUI"
        self.location_data = self._load_location_data(location_file)

        if not self.location_data:
            # Handle error case where data loading fails
            super().__init__("Error", description="Failed to load location data.")
            self.options = [MenuOption("1", "Back", "go_back")]
            return

        super().__init__(
            title=self.location_data.get("name", "Unknown Location"),
            description=self.location_data.get("initial_description", ""),
        )

        self.options = self._create_menu_options()
        self.examination_result = ""
        Log.p(
            self.tag, [f"Apartment screen initialized with data from {location_file}"]
        )

    def _load_location_data(self, file_path: str) -> Dict:
        """Load location data from a JSON file."""
        try:
            path = Path(file_path)
            if not path.exists():
                Log.p(self.tag, [f"ERROR: Location file not found at {file_path}"])
                return {}
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            Log.p(self.tag, [f"ERROR: Failed to load or parse {file_path}: {e}"])
            return {}

    def _create_menu_options(self) -> List[MenuOption]:
        """Create menu options from the loaded location data."""
        options = []
        explorable_items = self.location_data.get("explorable_items", {})

        for item_key, item_data in explorable_items.items():
            # The key for the option doesn't matter here, as it will be reassigned by MenuScreen
            options.append(
                MenuOption(
                    key="",  # Key will be set by the UI framework
                    text=item_data.get("text", "Unknown Option"),
                    action=f"examine:{item_key}",
                )
            )
        return options

    def handle_action(self, action: str):
        """Handle a menu action selection in a data-driven way."""
        if action.startswith("examine:"):
            item_key = action.split(":")[1]
            self._examine_item(item_key)
        elif action == "go_back":
            # This would be handled by the main UI to pop the screen
            pass
        else:
            Log.p(self.tag, [f"Unknown action: {action}"])

    def _examine_item(self, item_key: str):
        """Examine an item using data from the loaded JSON."""
        item_data = self.location_data.get("explorable_items", {}).get(item_key)

        if not item_data:
            self.examination_result = (
                f"You see nothing special about the {item_key.replace('_', ' ')}."
            )
            Log.p(self.tag, [f"No data found for item key: {item_key}"])
        else:
            self.examination_result = item_data.get(
                "description", "It's just an ordinary object."
            )
            Log.p(self.tag, [f"Examined {item_key}"])

        self.description = f"""{self.location_data.get("name", "Unknown Location")}

{self.examination_result}

Select another action to continue exploring:"""


# EOF
