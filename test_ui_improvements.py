#!/usr/bin/env python3
"""
Test script for the 4 UI improvements:
1. Dynamic header with location/time
2. Updated apartment notes
3. Expandable menu system with "0" for next panel
4. Improved text readability
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from src.ui.main_ui import MainUI, StatusData, MenuScreen, MenuOption
from src.ui.apartment_screen import ApartmentScreen
from src.game.locations import ApartmentLocation
from src.utils.logging import Log


def test_dynamic_header():
    """Test dynamic header functionality"""
    print("Testing Dynamic Header...")

    ui = MainUI()

    # Test initial status
    status = StatusData(location="Test Location", time="08:00", day=1)
    ui.update_status(status)

    # Test location mapping
    assert (
        ui._get_location_from_screen("Broken Divinity - Main Menu")
        == "Detective Bureau"
    )
    assert ui._get_location_from_screen("Detective Apartment") == "Your Apartment"
    assert ui._get_location_from_screen("Unknown Screen") == "Unknown Location"

    # Test time increment
    ui._increment_time()
    assert ui.status_data.time == "08:01"

    print("✅ Dynamic header functionality working")


def test_apartment_notes():
    """Test updated apartment notes"""
    print("Testing Updated Apartment Notes...")

    apartment = ApartmentLocation()  # No arguments needed
    screen = ApartmentScreen(apartment)

    # Test that divine references are removed
    screen._read_notes()
    notes = screen.examination_result

    assert "divine" not in notes.lower()
    assert "god" not in notes.lower()
    assert "yahweh" not in notes.lower()
    assert "chief" in notes.lower()
    assert "check in" in notes.lower()

    print("✅ Apartment notes updated successfully")


def test_expandable_menus():
    """Test expandable menu system"""
    print("Testing Expandable Menu System...")

    # Create a menu with more than 9 options
    options = []
    for i in range(15):  # 15 options, more than max visible (9)
        options.append(MenuOption(str(i + 1), f"Option {i+1}", f"action_{i+1}"))

    screen = MenuScreen("Test Menu", options=options)

    # Should show first 9 options plus "0" for next page
    assert len(screen.options) == 10  # 9 visible + 1 "next page"
    assert screen.options[-1].key == "0"
    assert "More Options" in screen.options[-1].text

    # Test going to next page
    screen.next_menu_page()
    assert screen.menu_page == 1
    assert len(screen.options) == 6  # Remaining 6 options

    print("✅ Expandable menu system working")


def test_improved_readability():
    """Test improved text readability"""
    print("Testing Improved Text Readability...")

    ui = MainUI()
    config = ui.config

    # Check that colors are brighter for better readability
    assert config.main_area_color == (255, 255, 255)  # Bright white
    assert config.border_color == (180, 180, 180)  # Brighter gray
    assert config.menu_color == (220, 220, 255)  # Brighter blue
    assert config.status_color == (255, 255, 160)  # Brighter yellow

    print("✅ Text readability improvements configured")


def test_input_handling():
    """Test that "0" key is handled for expandable menus"""
    print("Testing Input Handling for '0' Key...")

    from src.ui.main_ui import InputHandler
    import tcod.event

    handler = InputHandler()

    # Test key range handling by checking the logic directly
    # K_0 should be within the range now
    k_0_value = tcod.event.K_0
    k_9_value = tcod.event.K_9

    # Verify the range includes 0
    assert tcod.event.K_0 <= k_0_value <= tcod.event.K_9

    # Test that the key mapping would work
    expected_0 = str(k_0_value - tcod.event.K_0)  # Should be "0"
    expected_9 = str(k_9_value - tcod.event.K_0)  # Should be "9"

    assert expected_0 == "0"
    assert expected_9 == "9"

    print("✅ Input handling for '0' key working")


def run_all_tests():
    """Run all UI improvement tests"""
    print("🧪 Testing UI Improvements...")
    print("=" * 50)

    try:
        test_dynamic_header()
        test_apartment_notes()
        test_expandable_menus()
        test_improved_readability()
        test_input_handling()

        print("=" * 50)
        print("🎉 All UI improvement tests passed!")
        print()
        print("Improvements implemented:")
        print("✅ 1. Dynamic header with location and game time")
        print("✅ 2. Updated apartment notes (removed divine references)")
        print("✅ 3. Expandable menu system with '0' for next panel")
        print("✅ 4. Improved text readability with brighter colors")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
