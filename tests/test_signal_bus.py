"""
Tests for the SignalBus system.

Tests the core pub/sub functionality, thread safety, and error handling
following the "public API only" testing approach.

Author: GitHub Copilot
"""

import pytest
import threading
import time
from unittest.mock import Mock

from src.core.signals import (
    SignalBus,
    CoreSignal,
    SignalData,
    get_signal_bus,
    reset_signal_bus,
)


class TestSignalData:
    """Test SignalData validation and functionality."""

    def test_valid_signal_data_creation(self):
        """Test creating valid signal data."""
        signal_data = SignalData(
            signal_type=CoreSignal.REGISTRY_INITIALIZED,
            source="TestSource",
            data={"test": "value"},
            timestamp=time.time(),
        )

        assert signal_data.signal_type == CoreSignal.REGISTRY_INITIALIZED
        assert signal_data.source == "TestSource"
        assert signal_data.data == {"test": "value"}
        assert isinstance(signal_data.timestamp, float)

    def test_invalid_signal_type(self):
        """Test validation of invalid signal type."""
        with pytest.raises(ValueError, match="Invalid signal type"):
            SignalData(
                signal_type=None,  # type: ignore
                source="TestSource",
                data={},
                timestamp=time.time(),
            )

    def test_invalid_source(self):
        """Test validation of invalid source."""
        with pytest.raises(ValueError, match="Source must be a non-empty string"):
            SignalData(
                signal_type=CoreSignal.REGISTRY_INITIALIZED,
                source="",
                data={},
                timestamp=time.time(),
            )

    def test_invalid_data(self):
        """Test validation of invalid data."""
        with pytest.raises(ValueError, match="Data must be a dictionary"):
            SignalData(
                signal_type=CoreSignal.REGISTRY_INITIALIZED,
                source="TestSource",
                data="invalid",  # type: ignore
                timestamp=time.time(),
            )


class TestSignalBus:
    """Test SignalBus functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.signal_bus = SignalBus()

    def teardown_method(self):
        """Clean up test environment."""
        self.signal_bus.clear_subscribers()
        self.signal_bus.clear_history()

    def test_basic_emit_and_listen(self):
        """Test basic signal emission and listening."""
        received_signals = []

        def listener(signal_data):
            received_signals.append(signal_data)

        # Subscribe to signal
        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, listener)

        # Emit signal
        test_data = {"test": "value"}
        self.signal_bus.emit(CoreSignal.REGISTRY_INITIALIZED, "TestSource", test_data)

        # Verify signal was received
        assert len(received_signals) == 1
        signal = received_signals[0]
        assert signal.signal_type == CoreSignal.REGISTRY_INITIALIZED
        assert signal.source == "TestSource"
        assert signal.data == test_data

    def test_multiple_subscribers(self):
        """Test multiple subscribers for the same signal."""
        received_1 = []
        received_2 = []

        def listener1(signal_data):
            received_1.append(signal_data)

        def listener2(signal_data):
            received_2.append(signal_data)

        # Subscribe both listeners
        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, listener1)
        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, listener2)

        # Emit signal
        self.signal_bus.emit(CoreSignal.REGISTRY_INITIALIZED, "TestSource")

        # Both should receive the signal
        assert len(received_1) == 1
        assert len(received_2) == 1
        assert received_1[0].signal_type == received_2[0].signal_type

    def test_different_signal_types(self):
        """Test that listeners only receive their signal types."""
        registry_signals = []
        combat_signals = []

        def registry_listener(signal_data):
            registry_signals.append(signal_data)

        def combat_listener(signal_data):
            combat_signals.append(signal_data)

        # Subscribe to different signals
        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, registry_listener)
        self.signal_bus.listen(CoreSignal.COMBAT_STARTED, combat_listener)

        # Emit both types
        self.signal_bus.emit(CoreSignal.REGISTRY_INITIALIZED, "RegistrySource")
        self.signal_bus.emit(CoreSignal.COMBAT_STARTED, "CombatSource")

        # Each listener should only receive their signal type
        assert len(registry_signals) == 1
        assert len(combat_signals) == 1
        assert registry_signals[0].signal_type == CoreSignal.REGISTRY_INITIALIZED
        assert combat_signals[0].signal_type == CoreSignal.COMBAT_STARTED

    def test_unlisten(self):
        """Test unsubscribing from signals."""
        received_signals = []

        def listener(signal_data):
            received_signals.append(signal_data)

        # Subscribe and emit
        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, listener)
        self.signal_bus.emit(CoreSignal.REGISTRY_INITIALIZED, "TestSource")
        assert len(received_signals) == 1

        # Unsubscribe and emit again
        result = self.signal_bus.unlisten(CoreSignal.REGISTRY_INITIALIZED, listener)
        assert result is True

        self.signal_bus.emit(CoreSignal.REGISTRY_INITIALIZED, "TestSource")
        assert len(received_signals) == 1  # Should not have increased

    def test_unlisten_nonexistent_callback(self):
        """Test unsubscribing a callback that wasn't subscribed."""

        def dummy_listener(signal_data):
            pass

        result = self.signal_bus.unlisten(
            CoreSignal.REGISTRY_INITIALIZED, dummy_listener
        )
        assert result is False

    def test_emit_with_no_data(self):
        """Test emitting signals without data payload."""
        received_signals = []

        def listener(signal_data):
            received_signals.append(signal_data)

        self.signal_bus.listen(CoreSignal.COMBAT_STARTED, listener)
        self.signal_bus.emit(CoreSignal.COMBAT_STARTED, "TestSource")

        assert len(received_signals) == 1
        assert received_signals[0].data == {}

    def test_subscriber_count(self):
        """Test getting subscriber count for signal types."""

        def listener1(signal_data):
            pass

        def listener2(signal_data):
            pass

        # Initially no subscribers
        assert (
            self.signal_bus.get_subscriber_count(CoreSignal.REGISTRY_INITIALIZED) == 0
        )

        # Add subscribers
        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, listener1)
        assert (
            self.signal_bus.get_subscriber_count(CoreSignal.REGISTRY_INITIALIZED) == 1
        )

        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, listener2)
        assert (
            self.signal_bus.get_subscriber_count(CoreSignal.REGISTRY_INITIALIZED) == 2
        )

        # Remove subscriber
        self.signal_bus.unlisten(CoreSignal.REGISTRY_INITIALIZED, listener1)
        assert (
            self.signal_bus.get_subscriber_count(CoreSignal.REGISTRY_INITIALIZED) == 1
        )

    def test_signal_history(self):
        """Test signal history functionality."""
        # Emit some signals
        self.signal_bus.emit(CoreSignal.REGISTRY_INITIALIZED, "Source1", {"test": 1})
        self.signal_bus.emit(CoreSignal.COMBAT_STARTED, "Source2", {"test": 2})

        # Check history
        history = self.signal_bus.get_signal_history()
        assert len(history) == 2
        assert history[0].signal_type == CoreSignal.REGISTRY_INITIALIZED
        assert history[1].signal_type == CoreSignal.COMBAT_STARTED

        # Check limited history
        recent = self.signal_bus.get_signal_history(1)
        assert len(recent) == 1
        assert recent[0].signal_type == CoreSignal.COMBAT_STARTED

    def test_clear_subscribers(self):
        """Test clearing all subscribers."""

        def listener(signal_data):
            pass

        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, listener)
        self.signal_bus.listen(CoreSignal.COMBAT_STARTED, listener)

        assert (
            self.signal_bus.get_subscriber_count(CoreSignal.REGISTRY_INITIALIZED) == 1
        )
        assert self.signal_bus.get_subscriber_count(CoreSignal.COMBAT_STARTED) == 1

        self.signal_bus.clear_subscribers()

        assert (
            self.signal_bus.get_subscriber_count(CoreSignal.REGISTRY_INITIALIZED) == 0
        )
        assert self.signal_bus.get_subscriber_count(CoreSignal.COMBAT_STARTED) == 0

    def test_exception_in_callback(self):
        """Test that exceptions in callbacks don't break signal emission."""
        received_good_signals = []

        def bad_listener(signal_data):
            raise Exception("Test exception")

        def good_listener(signal_data):
            received_good_signals.append(signal_data)

        # Subscribe both listeners
        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, bad_listener)
        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, good_listener)

        # Emit signal - should not crash and good listener should still work
        self.signal_bus.emit(CoreSignal.REGISTRY_INITIALIZED, "TestSource")

        assert len(received_good_signals) == 1

    def test_thread_safety(self):
        """Test thread safety of signal emission and subscription."""
        received_signals = []
        lock = threading.Lock()

        def listener(signal_data):
            with lock:
                received_signals.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, listener)

        # Emit signals from multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(
                target=self.signal_bus.emit,
                args=(CoreSignal.REGISTRY_INITIALIZED, f"Source{i}", {"index": i}),
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All signals should have been received
        assert len(received_signals) == 10

        # Check that all indices are present
        indices = sorted([signal.data["index"] for signal in received_signals])
        assert indices == list(range(10))


class TestGlobalSignalBus:
    """Test global signal bus functionality."""

    def setup_method(self):
        """Set up test environment."""
        reset_signal_bus()  # Ensure clean state

    def teardown_method(self):
        """Clean up test environment."""
        reset_signal_bus()

    def test_get_signal_bus_singleton(self):
        """Test that get_signal_bus returns the same instance."""
        bus1 = get_signal_bus()
        bus2 = get_signal_bus()

        assert bus1 is bus2
        assert isinstance(bus1, SignalBus)

    def test_reset_signal_bus(self):
        """Test resetting the global signal bus."""
        bus1 = get_signal_bus()

        # Add a subscriber
        def listener(signal_data):
            pass

        bus1.listen(CoreSignal.REGISTRY_INITIALIZED, listener)
        assert bus1.get_subscriber_count(CoreSignal.REGISTRY_INITIALIZED) == 1

        # Reset and get new bus
        reset_signal_bus()
        bus2 = get_signal_bus()

        # Should be a different instance with no subscribers
        assert bus1 is not bus2
        assert bus2.get_subscriber_count(CoreSignal.REGISTRY_INITIALIZED) == 0


class TestSignalValidation:
    """Test signal validation and error handling."""

    def setup_method(self):
        """Set up test environment."""
        self.signal_bus = SignalBus()

    def test_invalid_listen_signal_type(self):
        """Test listening with invalid signal type."""

        def listener(signal_data):
            pass

        with pytest.raises(ValueError, match="Invalid signal type"):
            self.signal_bus.listen(None, listener)  # type: ignore

    def test_invalid_listen_callback(self):
        """Test listening with invalid callback."""
        with pytest.raises(ValueError, match="Callback must be callable"):
            self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, "not_callable")  # type: ignore

    def test_emit_creates_valid_signal_data(self):
        """Test that emit creates valid SignalData objects."""
        received_signals = []

        def listener(signal_data):
            received_signals.append(signal_data)

        self.signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, listener)
        self.signal_bus.emit(
            CoreSignal.REGISTRY_INITIALIZED, "TestSource", {"key": "value"}
        )

        assert len(received_signals) == 1
        signal = received_signals[0]
        assert isinstance(signal, SignalData)
        assert signal.signal_type == CoreSignal.REGISTRY_INITIALIZED
        assert signal.source == "TestSource"
        assert signal.data == {"key": "value"}
        assert isinstance(signal.timestamp, float)


# EOF
