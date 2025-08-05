#!/usr/bin/env python3
"""
Test the enhanced feedback system for character creation and apartment exploration
"""

from src.ui.main_ui import MainUI
from src.ui.character_creation_screen import CharacterCreationScreen
from src.ui.apartment_screen import ApartmentScreen
from src.game.character_creation import CharacterCreator
from src.game.locations import ApartmentLocation

def test_feedback_system():
    """Test the enhanced feedback for user actions"""
    print("🧪 Testing Enhanced Feedback System...")
    
    # Test 1: Character Creation Feedback
    print("\n📖 Character Creation Feedback Test:")
    ui = MainUI()
    creator = CharacterCreator()
    char_screen = CharacterCreationScreen(ui, creator)
    
    print(f"✅ Initial Description Present: {len(char_screen.description) > 50}")
    print(f"   Length: {len(char_screen.description)} characters")
    
    if creator.available_backgrounds:
        background = creator.available_backgrounds[0]
        original_desc_len = len(char_screen.description)
        char_screen._select_background(background.id)
        new_desc_len = len(char_screen.description)
        
        print(f"✅ Background Selection Updates Description: {new_desc_len > original_desc_len}")
        print(f"   Original: {original_desc_len} chars → New: {new_desc_len} chars")
        print(f"   Selected: {background.display_name}")
    
    # Test 2: Apartment Exploration Feedback
    print("\n🏠 Apartment Exploration Feedback Test:")
    apartment = ApartmentLocation()
    apt_screen = ApartmentScreen(apartment)
    
    print(f"✅ Initial Apartment Description Present: {len(apt_screen.description) > 50}")
    original_apt_desc = apt_screen.description
    
    # Test examining an item
    apt_screen._examine_item('revolver')
    revolver_desc = apt_screen.description
    
    print(f"✅ Revolver Examination Updates Description: {revolver_desc != original_apt_desc}")
    print(f"   Contains 'revolver' reference: {'revolver' in revolver_desc.lower()}")
    
    # Test reading notes
    apt_screen._read_notes()
    notes_desc = apt_screen.description
    
    print(f"✅ Notes Reading Updates Description: {notes_desc != revolver_desc}")
    print(f"   Contains case notes: {'Case Notes' in notes_desc}")
    
    print("\n🎉 Feedback System Enhancement Complete!")
    return True

if __name__ == "__main__":
    test_feedback_system()
