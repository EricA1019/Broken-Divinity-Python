#!/usr/bin/env python3
"""
Test apartment screen functionality
"""

from src.ui.main_ui import MainUI
from src.ui.apartment_screen import ApartmentScreen
from src.game.locations import ApartmentLocation

def test_apartment_screen():
    """Test apartment screen menu functionality"""
    print("🧪 Testing apartment screen...")
    
    # Create apartment and UI
    apartment = ApartmentLocation()
    apartment_screen = ApartmentScreen(apartment)
    ui = MainUI()
    ui.current_screen = apartment_screen
    
    print(f"Screen title: {apartment_screen.title}")
    print(f"Has handle_action: {hasattr(apartment_screen, 'handle_action')}")
    print(f"Number of options: {len(apartment_screen.options)}")
    
    # Test some apartment actions
    actions_to_test = ["menu_option_1", "menu_option_3", "menu_option_7"]
    
    for action in actions_to_test:
        print(f"\nTesting {action}:")
        option = apartment_screen.get_option_by_key(action.split("_")[-1])
        if option:
            print(f"  Option: {option.text} -> {option.action}")
            result = ui.process_action(action)
            print(f"  Processed: {result}")
            if hasattr(apartment_screen, 'examination_result') and apartment_screen.examination_result:
                print(f"  Result: {apartment_screen.examination_result[:100]}...")
        else:
            print(f"  No option found for key")

if __name__ == "__main__":
    test_apartment_screen()
