"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Data Layer Package                                                          ║
╟──────────────────────────────────────────────────────────────────────────────╢
║  Author        : Eric Acosta ┃ https://github.com/EricA1019                 ║
║  Purpose       : SQLite database layer and data management                  ║
║  Last-Updated  : 2025-08-05                                                 ║
║  Version       : v0.0.12                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from .database import DatabaseManager, DatabaseError

__all__ = ["DatabaseManager", "DatabaseError"]

# EOF
