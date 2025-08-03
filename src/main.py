"""
Broken Divinity - Main Entry Point

Entry point for the ASCII roguelike game.
"""

import sys
from typing import NoReturn

from src.utils.logging import Log


def main() -> NoReturn:
    """Main entry point for Broken Divinity."""
    Log.p("Main", ["Starting Broken Divinity ASCII Roguelike v0.1.0"])
    
    try:
        # TODO(hop2): Initialize tcod window
        Log.p("Main", ["Game initialized successfully"])
        
        # TODO(hop2): Main game loop
        print("Broken Divinity - Coming Soon!")
        print("Press any key to exit...")
        input()
        
    except KeyboardInterrupt:
        Log.p("Main", ["Game interrupted by user"])
    except Exception as e:
        Log.p("Main", ["Fatal error:", str(e)])
        sys.exit(1)
    finally:
        Log.p("Main", ["Game shutdown complete"])
    
    sys.exit(0)


if __name__ == "__main__":
    main()

#EOF
