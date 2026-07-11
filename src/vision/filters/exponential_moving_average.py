import typing
from src.vision.filters.base_filter import BaseFilter


class ExponentialMovingAverage(BaseFilter):
    """Implements an Exponential Moving Average (EMA) filter for 2D coordinates.

    EMA applies decreasing weights to older coordinates exponentially. It provides
    an efficient, low-latency smoothing mechanism ideal for real-time HCI loops.
    Mathematical formulation:
        S_t = alpha * Y_t + (1 - alpha) * S_{t-1}
    Where:
        S_t   = smoothed coordinate at step t
        Y_t   = raw coordinate at step t
        alpha = smoothing factor (0 < alpha <= 1)
    """

    def __init__(self, alpha: float = 0.3) -> None:
        """Initializes the EMA filter.

        Args:
            alpha: The smoothing coefficient (0.0 to 1.0).
                Smaller values increase smoothing (stability) but introduce lag.
                Larger values reduce lag (responsiveness) but retain more noise.

        Raises:
            ValueError: If alpha is not within the range (0.0, 1.0].
        """
        if not (0.0 < alpha <= 1.0):
            raise ValueError("Smoothing factor 'alpha' must satisfy 0.0 < alpha <= 1.0")

        self.alpha = alpha
        self._state: typing.Optional[typing.Tuple[float, float]] = None

    def filter(
        self, value: typing.Tuple[float, float]
    ) -> typing.Tuple[float, float]:
        """Applies EMA smoothing to the incoming 2D coordinates.

        Args:
            value: A tuple of raw (x, y) coordinates.

        Returns:
            A tuple of smoothed (x, y) coordinates.
        """
        raw_x, raw_y = value

        # If there is no historical tracking state, initialize state to current value
        if self._state is None:
            self._state = (raw_x, raw_y)
            return self._state

        prev_x, prev_y = self._state

        # Compute EMA recursive weighted average
        smoothed_x = self.alpha * raw_x + (1.0 - self.alpha) * prev_x
        smoothed_y = self.alpha * raw_y + (1.0 - self.alpha) * prev_y

        # Update internal filter state
        self._state = (smoothed_x, smoothed_y)
        return self._state

    def reset(self) -> None:
        """Resets the internal tracking history buffer."""
        self._state = None
