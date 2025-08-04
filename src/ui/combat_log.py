"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Combat Log System                                                           ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : Scrollable message history with colors and timestamps      ║
║  Last-Updated  : 2025-08-03                                                 ║
║  Version       : v0.1.7                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.utils.logging import Log


class LogLevel(Enum):
    """Log message priority levels."""
    
    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warning"
    ERROR = "error"
    COMBAT = "combat"
    SYSTEM = "system"


@dataclass
class LogMessage:
    """A single log message with metadata."""
    
    timestamp: datetime
    level: LogLevel
    message: str
    color: Optional[str] = None
    
    def formatted_time(self) -> str:
        """Get formatted timestamp string."""
        return self.timestamp.strftime("%H:%M:%S")
    
    def get_display_color(self) -> str:
        """Get the display color for this message."""
        if self.color:
            return self.color
            
        # Default colors by level
        color_map = {
            LogLevel.DEBUG: "gray",
            LogLevel.INFO: "white", 
            LogLevel.WARNING: "yellow",
            LogLevel.ERROR: "red",
            LogLevel.COMBAT: "orange",
            LogLevel.SYSTEM: "cyan"
        }
        return color_map.get(self.level, "white")


class CombatLog:
    """
    Scrollable message history component for the game.
    
    Manages message storage, display formatting, and scrolling functionality.
    """
    
    def __init__(self, max_messages: int = 1000, max_display_lines: int = 10):
        """
        Initialize the combat log.
        
        Args:
            max_messages: Maximum messages to store in history
            max_display_lines: Maximum lines to display at once
        """
        self.max_messages = max_messages
        self.max_display_lines = max_display_lines
        self.messages: List[LogMessage] = []
        self.scroll_position = 0  # 0 = showing most recent messages
        
        Log.p("CombatLog", ["Initialized", "with", max_messages, "max messages"])
        
        # Add welcome message
        self.add_message("Combat log initialized", LogLevel.SYSTEM, "cyan")
    
    def add_message(self, text: str, level: LogLevel = LogLevel.INFO, color: Optional[str] = None) -> None:
        """
        Add a new message to the log.
        
        Args:
            text: Message content
            level: Message priority level
            color: Optional custom color override
        """
        message = LogMessage(
            timestamp=datetime.now(),
            level=level,
            message=text,
            color=color
        )
        
        self.messages.append(message)
        
        # Trim old messages if we exceed the limit
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
            Log.p("CombatLog", ["Trimmed", "old", "messages"])
        
        # Auto-scroll to newest message when new content is added
        self.scroll_position = 0
        
        Log.p("CombatLog", ["Added", level.value, "message:", text[:50]])
    
    def scroll_up(self, lines: int = 1) -> bool:
        """
        Scroll up in the message history.
        
        Args:
            lines: Number of lines to scroll up
            
        Returns:
            True if scrolling occurred, False if already at top
        """
        max_scroll = max(0, len(self.messages) - self.max_display_lines)
        new_position = min(self.scroll_position + lines, max_scroll)
        
        if new_position != self.scroll_position:
            self.scroll_position = new_position
            Log.p("CombatLog", ["Scrolled", "up", "to", "position", self.scroll_position])
            return True
        
        return False
    
    def scroll_down(self, lines: int = 1) -> bool:
        """
        Scroll down in the message history.
        
        Args:
            lines: Number of lines to scroll down
            
        Returns:
            True if scrolling occurred, False if already at bottom
        """
        new_position = max(0, self.scroll_position - lines)
        
        if new_position != self.scroll_position:
            self.scroll_position = new_position
            Log.p("CombatLog", ["Scrolled", "down", "to", "position", self.scroll_position])
            return True
        
        return False
    
    def get_visible_messages(self) -> List[LogMessage]:
        """
        Get the currently visible messages based on scroll position.
        
        Returns:
            List of messages to display
        """
        if not self.messages:
            return []
        
        # Calculate the range of messages to show
        total_messages = len(self.messages)
        start_index = max(0, total_messages - self.max_display_lines - self.scroll_position)
        end_index = total_messages - self.scroll_position
        
        return self.messages[start_index:end_index]
    
    def get_formatted_lines(self, width: int = 80) -> List[Tuple[str, str]]:
        """
        Get formatted display lines with colors.
        
        Args:
            width: Maximum width for each line
            
        Returns:
            List of (text, color) tuples for display
        """
        visible_messages = self.get_visible_messages()
        formatted_lines = []
        
        for message in visible_messages:
            # Format: [HH:MM:SS] Message text
            timestamp = message.formatted_time()
            prefix = f"[{timestamp}] "
            max_text_width = width - len(prefix)
            
            # Truncate message if too long
            text = message.message
            if len(text) > max_text_width:
                text = text[:max_text_width - 3] + "..."
            
            full_line = prefix + text
            color = message.get_display_color()
            
            formatted_lines.append((full_line, color))
        
        # Pad with empty lines if needed
        while len(formatted_lines) < self.max_display_lines:
            formatted_lines.insert(0, ("", "white"))
        
        return formatted_lines
    
    def clear_messages(self) -> None:
        """Clear all messages from the log."""
        self.messages.clear()
        self.scroll_position = 0
        Log.p("CombatLog", ["Cleared", "all", "messages"])
    
    def get_stats(self) -> dict:
        """Get log statistics for debugging."""
        return {
            "total_messages": len(self.messages),
            "scroll_position": self.scroll_position,
            "max_display_lines": self.max_display_lines,
            "can_scroll_up": self.scroll_position < len(self.messages) - self.max_display_lines,
            "can_scroll_down": self.scroll_position > 0
        }

    # Convenience methods for common message types
    def log_combat(self, message: str) -> None:
        """Add a combat-related message."""
        self.add_message(message, LogLevel.COMBAT, "orange")
    
    def log_system(self, message: str) -> None:
        """Add a system message."""
        self.add_message(message, LogLevel.SYSTEM, "cyan")
    
    def log_warning(self, message: str) -> None:
        """Add a warning message."""
        self.add_message(message, LogLevel.WARNING, "yellow")
    
    def log_error(self, message: str) -> None:
        """Add an error message."""
        self.add_message(message, LogLevel.ERROR, "red")

#EOF
