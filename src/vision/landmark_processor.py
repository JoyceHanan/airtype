import logging
import typing
from dataclasses import dataclass

from src.vision.hand_tracker import Landmark
from src.vision.filters.base_filter import BaseFilter
from src.vision.filters.exponential_moving_average import ExponentialMovingAverage

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FingertipData:
    """Encapsulates raw and smoothed coordinate metrics for the tracked fingertip.

    Attributes:
        pixel_coords: The raw (x, y) coordinates mapped to image resolution.
        smoothed_pixel_coords: The smoothed (x, y) coordinates mapped to image resolution.
        normalized_coords: The raw (x, y) coordinates normalized between 0.0 and 1.0.
        smoothed_normalized_coords: The smoothed (x, y) coordinates normalized between 0.0 and 1.0.
        depth: The relative distance of the fingertip along the Z-axis.
    """
    pixel_coords: typing.Tuple[int, int]
    smoothed_pixel_coords: typing.Tuple[int, int]
    normalized_coords: typing.Tuple[float, float]
    smoothed_normalized_coords: typing.Tuple[float, float]
    depth: float


class LandmarkProcessor:
    """Transforms raw hand tracking coordinates into structured, smoothed fingertip data.

    Abstracts pointer extraction, coordinate spaces mapping, and noise smoothing.
    Utilizes an interchangeable filtering strategy conforming to the Open/Closed Principle.
    """

    INDEX_FINGER_TIP_INDEX = 8

    def __init__(self, coord_filter: typing.Optional[BaseFilter] = None) -> None:
        """Initializes the LandmarkProcessor with an optional smoothing filter.

        Args:
            coord_filter: A filter implementing `BaseFilter` to smooth index coordinates.
                Defaults to an ExponentialMovingAverage filter with alpha=0.3.
        """
        # If no filter is specified, load the default EMA algorithm configuration
        self.filter = coord_filter or ExponentialMovingAverage(alpha=0.3)

    def extract_fingertip(
        self,
        landmarks: typing.List[Landmark],
        frame_width: int,
        frame_height: int,
    ) -> typing.Optional[FingertipData]:
        """Extracts, filters, and maps coordinates for the index fingertip.

        Args:
            landmarks: A list of 21 tracked `Landmark` data points.
            frame_width: The physical width of the video frame in pixels.
            frame_height: The physical height of the video frame in pixels.

        Returns:
            A `FingertipData` object containing raw and smoothed coordinates,
            or None if the tracking data is empty or incomplete.
        """
        if len(landmarks) <= self.INDEX_FINGER_TIP_INDEX:
            logger.warning(
                f"Incomplete landmark tracking. Expected at least "
                f"{self.INDEX_FINGER_TIP_INDEX + 1} nodes, got {len(landmarks)}."
            )
            return None

        # Extract raw coordinates
        index_tip = landmarks[self.INDEX_FINGER_TIP_INDEX]
        raw_norm = (index_tip.x, index_tip.y)

        # 1. Apply smoothing in normalized coordinates space (resolution-independent)
        smoothed_norm_x, smoothed_norm_y = self.filter.filter(raw_norm)

        # 2. Convert raw normalized coordinates to pixel space and clip bounds
        raw_px_x = int(index_tip.x * frame_width)
        raw_px_y = int(index_tip.y * frame_height)
        raw_px_x = max(0, min(raw_px_x, frame_width - 1))
        raw_px_y = max(0, min(raw_px_y, frame_height - 1))

        # 3. Convert smoothed normalized coordinates to pixel space and clip bounds
        smooth_px_x = int(smoothed_norm_x * frame_width)
        smooth_px_y = int(smoothed_norm_y * frame_height)
        smooth_px_x = max(0, min(smooth_px_x, frame_width - 1))
        smooth_px_y = max(0, min(smooth_px_y, frame_height - 1))

        # Return updated structured data block
        return FingertipData(
            pixel_coords=(raw_px_x, raw_px_y),
            smoothed_pixel_coords=(smooth_px_x, smooth_px_y),
            normalized_coords=raw_norm,
            smoothed_normalized_coords=(smoothed_norm_x, smoothed_norm_y),
            depth=index_tip.z,
        )

    def reset_filters(self) -> None:
        """Resets the internal tracking history state of the coordinate filter.

        Must be triggered when hand tracking is lost to prevent the smoothed coordinate
        pointer from snapping across the screen upon subsequent re-detection.
        """
        logger.debug("Resetting landmark processor coordinate filters.")
        self.filter.reset()
