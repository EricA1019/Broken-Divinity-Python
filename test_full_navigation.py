#!/usr/bin/env python3
"""
Test the full menu navigation flow
"""

from src.ui.main_ui import MainUI
from src.ui.main_menu_screen import MainMenuScreen

def test_full_navigation():
    """Test navigation through menu system"""
    print("🧪 Testing full navigation flow...")
    
    # Create UI and start at main menu
    ui = MainUI()
    main_menu = MainMenuScreen(ui)
    ui.current_screen = main_menu
    
    print(f"1. Started at: {ui.current_screen.title}")
    
    # Test "New Game" action
    print("2. Testing 'New Game' selection...")
    result = ui.process_action("menu_option_1")
    print(f"   Action processed: {result}")
    print(f"   Now at: {ui.current_screen.title}")
    
    # Test character creation screen
    if hasattr(ui.current_screen, 'character_creator'):
        backgrounds = ui.current_screen.character_creator.available_backgrounds
        print(f"   Available backgrounds: {len(backgrounds)}")
        if backgrounds:
            print(f"   First background: {backgrounds[0].display_name}")
            
            # Test selecting first background
            print("3. Testing background selection...")
            result = ui.process_action("menu_option_1")
            print(f"   Action processed: {result}")
            print(f"   Now at: {ui.current_screen.title}")
    
    # Test "Continue Game" from main menu
    print("4. Testing 'Continue Game' from main menu...")
    main_menu = MainMenuScreen(ui)
    ui.current_screen = main_menu
    result = ui.process_action("menu_option_2") 
    print(f"   Action processed: {result}")
    print(f"   Now at: {ui.current_screen.title}")

if __name__ == "__main__":
    test_full_navigation()
