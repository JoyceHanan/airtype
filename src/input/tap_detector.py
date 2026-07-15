from enum import Enum, auto
import logging

logger = logging.getLogger(__name__)


class TapState(Enum):
    """Represents states inside the tap detection gesture state machine."""
    IDLE = auto()      # The pointer is hovering or resting above the press plane
    PRESSED = auto()   # The pointer has pushed past the press depth threshold


class TapDetector:
    """Classifies click gestures based on fingertip Z-axis depth tracking.

    Implements a Finite State Machine (FSM) with hysteresis thresholds to provide
    software debouncing and prevent double-trigger inputs in real-time streams.
    """

    def __init__(
        self,
        press_threshold: float = -0.06,
        release_threshold: float = -0.03,
    ) -> None:
        """Initializes the TapDetector.

        Args:
            press_threshold: Relative Z coordinate depth below which (closer to camera)
                the gesture transitions to PRESSED.
            release_threshold: Relative Z coordinate depth above which (further from camera)
                the gesture resets to IDLE.
        """
        # Hysteresis configuration: press threshold must be deeper (more negative) than release threshold
        self.press_threshold = press_threshold
        self.release_threshold = release_threshold
        
        self.state = TapState.IDLE
        logger.info(
            f"TapDetector initialized. Press: {self.press_threshold}, Release: {self.release_threshold}"
        )

    def update(self, z_depth: float) -> bool:
        """Updates the state machine with the latest Z coordinate and checks for tap events.

        Args:
            z_depth: Relative depth coordinate of the fingertip.

        Returns:
            True if a tap event was triggered on this frame (IDLE -> PRESSED transition),
            otherwise False.
        """
        event_triggered = False

        if self.state == TapState.IDLE:
            # Transition to PRESSED if Z-coordinate is more negative than press threshold (closer to camera)
            if z_depth <= self.press_threshold:
                self.state = TapState.PRESSED
                event_triggered = True
                logger.debug(f"Tap state transition: IDLE -> PRESSED (Z: {z_depth:.4f})")
                
        elif self.state == TapState.PRESSED:
            # Return to IDLE if Z-coordinate rises back past release threshold (further from camera)
            if z_depth >= self.release_threshold:
                self.state = TapState.IDLE
                logger.debug(f"Tap state transition: PRESSED -> IDLE (Z: {z_depth:.4f})")

        return event_triggered

    def reset(self) -> None:
        """Resets the state machine back to IDLE."""
        if self.state != TapState.IDLE:
            logger.debug("Resetting TapDetector state to IDLE.")
            self.state = TapState.IDLE
        # No history is stored, so resetting self.state is sufficient
