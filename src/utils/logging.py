"""
Logging utilities for Broken Divinity.

Provides tagged logging following the project style guide.
"""

from typing import Any, List, Optional


class Log:
    """
    Tagged logging utility following Broken Divinity style guide.
    
    Provides consistent [SystemTag] prefixed messages for debugging.
    """
    
    @staticmethod
    def p(tag: str, args: Optional[List[Any]] = None) -> None:
        """
        Print a tagged log message.
        
        Args:
            tag: System tag (e.g., "Main", "EntityReg", "CombatMgr")
            args: List of arguments to join with spaces
        
        Example:
            Log.p("EntityReg", ["Loaded", 5, "entities"])
            # Output: [EntityReg] Loaded 5 entities
        """
        if args is None:
            args = []
        
        message_parts = [str(arg) for arg in args]
        message = " ".join(message_parts)
        print(f"[{tag}] {message}")


#EOF
