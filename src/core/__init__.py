"""
Core systems for Broken Divinity.

This package contains the fundamental infrastructure components that all other
systems depend on, including the signal bus and base registry classes.
"""

from .signals import SignalBus, CoreSignal, get_signal_bus
from .registry import BaseRegistry

__all__ = [
    "SignalBus",
    "CoreSignal",
    "get_signal_bus",
    "BaseRegistry",
]
