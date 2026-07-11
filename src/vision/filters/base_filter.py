from abc import ABC, abstractmethod
import typing


class BaseFilter(ABC):
    """Abstract base class defining the contract for motion smoothing filters.

    This interface allows different smoothing algorithms (e.g., EMA, Kalman,
    One Euro) to be swapped interchangeably in the tracking pipeline.
    """

    @abstractmethod
    def filter(
        self, value: typing.Tuple[float, float]
    ) -> typing.Tuple[float, float]:
        """Filters a 2D coordinate value.

        Args:
            value: A tuple of (x, y) coordinates to filter.

        Returns:
            A tuple of (x, y) smoothed coordinates.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Resets the internal state of the filter.

        This should be called when tracking is lost to prevent historical
        states from distorting subsequent new coordinates (coordinate snapping).
        """
        pass
