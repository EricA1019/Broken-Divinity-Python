"""
Test suite for logging utilities.

Tests the Log class and tagged logging functionality.
"""

import io
import sys
from unittest.mock import patch

import pytest

from src.utils.logging import Log


class TestLog:
    """Test the Log utility class."""
    
    def test_log_simple_message(self):
        """Test logging a simple message with tag."""
        with patch('builtins.print') as mock_print:
            Log.p("Test", ["Hello", "World"])
            mock_print.assert_called_once_with("[Test] Hello World")
    
    def test_log_no_args(self):
        """Test logging with no arguments."""
        with patch('builtins.print') as mock_print:
            Log.p("Test")
            mock_print.assert_called_once_with("[Test] ")
    
    def test_log_empty_args(self):
        """Test logging with empty args list."""
        with patch('builtins.print') as mock_print:
            Log.p("Test", [])
            mock_print.assert_called_once_with("[Test] ")
    
    def test_log_mixed_types(self):
        """Test logging with mixed argument types."""
        with patch('builtins.print') as mock_print:
            Log.p("EntityReg", ["Loaded", 5, "entities", True])
            mock_print.assert_called_once_with("[EntityReg] Loaded 5 entities True")
    
    def test_log_format_follows_style_guide(self):
        """Test that log format follows the style guide."""
        # Capture stdout to verify exact format
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            Log.p("CombatMgr", ["Attack", "deals", 10, "damage"])
        
        output = captured_output.getvalue().strip()
        assert output == "[CombatMgr] Attack deals 10 damage"
        assert output.startswith("[CombatMgr]")


# Integration test placeholder
def test_logging_integration():
    """Integration test for logging system."""
    # TODO(hop2): Add integration test when main game loop exists
    assert True


#EOF
