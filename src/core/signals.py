"""
Signal Bus System for Broken Divinity.

Provides a central pub/sub communication system for loose coupling between
components. All components communicate via signals rather than direct calls.

Author: GitHub Copilot
"""

import threading
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from src.utils.logging import Log


class CoreSignal(Enum):
    """Core signal types used throughout the application."""

    # Registry signals
    REGISTRY_INITIALIZED = auto()
    REGISTRY_RELOADED = auto()
    REGISTRY_ERROR = auto()

    # Database signals
    DATABASE_INITIALIZED = auto()
    DATABASE_ERROR = auto()

    # UI Signals
    UI_ACTION = "ui_action"
    UI_ACTION_SELECTED = "ui_action_selected"
    SCREEN_CHANGED = "screen_changed"

    # Combat signals
    COMBAT_STARTED = auto()
    COMBAT_ENDED = auto()
    TURN_STARTED = auto()
    TURN_ENDED = auto()

    # Entity signals
    ENTITY_CREATED = auto()
    ENTITY_DESTROYED = auto()
    ENTITY_HP_CHANGED = auto()
    ENTITY_DIED = auto()

    # Ability signals
    ABILITY_USED = auto()
    ABILITY_COOLDOWN_STARTED = auto()
    ABILITY_COOLDOWN_ENDED = auto()

    # Status effect signals
    STATUS_APPLIED = auto()
    STATUS_REMOVED = auto()
    STATUS_TICK = auto()

    # UI signals
    UI_UPDATE_REQUESTED = auto()
    UI_ERROR = auto()


@dataclass
class SignalData:
    """Container for signal payload data."""

    signal_type: CoreSignal
    source: str
    data: Dict[str, Any]
    timestamp: float

    def __post_init__(self):
        """Validate signal data after creation."""
        if not isinstance(self.signal_type, CoreSignal):
            raise ValueError(f"Invalid signal type: {self.signal_type}")
        if not isinstance(self.source, str) or not self.source:
            raise ValueError(f"Source must be a non-empty string: {self.source}")
        if not isinstance(self.data, dict):
            raise ValueError(f"Data must be a dictionary: {type(self.data)}")


class SignalBus:
    """
    Central pub/sub communication system.

    Provides thread-safe signal emission and subscription for loose coupling
    between game components.
    """

    def __init__(self):
        """Initialize the signal bus."""
        self._subscribers: Dict[CoreSignal, List[Callable]] = {}
        self._lock = threading.Lock()
        self._signal_history: List[SignalData] = []
        self._max_history = 1000  # Keep last 1000 signals for debugging

        Log.p("SignalBus", ["Initialized signal bus"])

    def listen(
        self, signal_type: CoreSignal, callback: Callable[[SignalData], None]
    ) -> None:
        """
        Subscribe to a signal type.

        Args:
            signal_type: The type of signal to listen for
            callback: Function to call when signal is emitted
        """
        if not isinstance(signal_type, CoreSignal):
            raise ValueError(f"Invalid signal type: {signal_type}")
        if not callable(callback):
            raise ValueError(f"Callback must be callable: {callback}")

        with self._lock:
            if signal_type not in self._subscribers:
                self._subscribers[signal_type] = []
            self._subscribers[signal_type].append(callback)

        Log.p("SignalBus", ["Registered listener for", signal_type.name])

    def unlisten(
        self, signal_type: CoreSignal, callback: Callable[[SignalData], None]
    ) -> bool:
        """
        Unsubscribe from a signal type.

        Args:
            signal_type: The type of signal to stop listening for
            callback: The callback function to remove

        Returns:
            True if callback was found and removed, False otherwise
        """
        with self._lock:
            if signal_type in self._subscribers:
                try:
                    self._subscribers[signal_type].remove(callback)
                    Log.p("SignalBus", ["Unregistered listener for", signal_type.name])
                    return True
                except ValueError:
                    pass
        return False

    def emit(
        self,
        signal_type: CoreSignal,
        source: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit a signal to all subscribers.

        Args:
            signal_type: The type of signal to emit
            source: Source component name (for debugging)
            data: Optional payload data
        """
        import time

        if data is None:
            data = {}

        # Create signal data with validation
        signal_data = SignalData(
            signal_type=signal_type, source=source, data=data, timestamp=time.time()
        )

        # Store in history for debugging
        with self._lock:
            self._signal_history.append(signal_data)
            if len(self._signal_history) > self._max_history:
                self._signal_history.pop(0)

            # Get subscribers for this signal type
            subscribers = self._subscribers.get(signal_type, []).copy()

        Log.p(
            "SignalBus",
            [
                "Emitting",
                signal_type.name,
                "from",
                source,
                "to",
                len(subscribers),
                "subscribers",
            ],
        )

        # Call all subscribers (outside the lock to prevent deadlocks)
        for callback in subscribers:
            try:
                callback(signal_data)
            except Exception as e:
                Log.p(
                    "SignalBus",
                    [
                        "ERROR: Subscriber callback failed for",
                        signal_type.name,
                        ":",
                        str(e),
                    ],
                )

    def get_subscriber_count(self, signal_type: CoreSignal) -> int:
        """
        Get the number of subscribers for a signal type.

        Args:
            signal_type: The signal type to check

        Returns:
            Number of subscribers
        """
        with self._lock:
            return len(self._subscribers.get(signal_type, []))

    def get_signal_history(self, count: Optional[int] = None) -> List[SignalData]:
        """
        Get recent signal history for debugging.

        Args:
            count: Number of recent signals to return (default: all)

        Returns:
            List of recent signals
        """
        with self._lock:
            if count is None:
                return self._signal_history.copy()
            return self._signal_history[-count:] if count > 0 else []

    def clear_subscribers(self) -> None:
        """Clear all subscribers (useful for testing)."""
        with self._lock:
            self._subscribers.clear()
            Log.p("SignalBus", ["Cleared all subscribers"])

    def clear_history(self) -> None:
        """Clear signal history (useful for testing)."""
        with self._lock:
            self._signal_history.clear()
            Log.p("SignalBus", ["Cleared signal history"])


# Global signal bus instance
_global_signal_bus: Optional[SignalBus] = None
_bus_lock = threading.Lock()


def get_signal_bus() -> SignalBus:
    """
    Get the global signal bus instance.

    Returns:
        Global SignalBus instance
    """
    global _global_signal_bus

    if _global_signal_bus is None:
        with _bus_lock:
            if _global_signal_bus is None:
                _global_signal_bus = SignalBus()

    return _global_signal_bus


def reset_signal_bus() -> None:
    """
    Reset the global signal bus (useful for testing).

    Warning: This will clear all subscribers and history.
    """
    global _global_signal_bus

    with _bus_lock:
        _global_signal_bus = None
        Log.p("SignalBus", ["Reset global signal bus"])


# EOF
