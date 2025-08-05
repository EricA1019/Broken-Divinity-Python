#!/usr/bin/env python3
"""
Quick test script to verify menu action flow
"""

from src.ui.main_ui import MainUI
from src.ui.main_menu_screen import MainMenuScreen

def test_menu_action_flow():
    """Test that menu actions are properly routed"""
    print("🧪 Testing menu action flow...")
    
    # Create UI and screen
    ui = MainUI()
    screen = MainMenuScreen(ui)
    ui.current_screen = screen
    
    print(f"Current screen: {ui.current_screen.title}")
    print(f"Screen has handle_action: {hasattr(screen, 'handle_action')}")
    
    # Test menu option selection
    option = screen.get_option_by_key("1")  # New Game
    if option:
        print(f"Found option: {option.text} -> {option.action}")
        
        # Test the action processing
        action = "menu_option_1"
        result = ui.process_action(action)
        print(f"Action processed: {result}")
    else:
        print("❌ No option found for key '1'")

if __name__ == "__main__":
    test_menu_action_flow()
