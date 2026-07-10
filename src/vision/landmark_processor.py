import logging
import typing
from dataclasses import dataclass

from src.vision.hand_tracker import Landmark

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FingertipData:
    """Encapsulates processed coordinate metrics for the tracked fingertip.

    Attributes:
        pixel_coords: The (x, y) coordinates mapped to the resolution grid
            of the active display window.
        normalized_coords: The (x, y) coordinates normalized between 0.0 and 1.0.
            Resolution independent, critical for scaling virtual layouts.
        depth: The relative distance of the fingertip along the Z-axis.
    """
    pixel_coords: typing.Tuple[int, int]
    normalized_coords: typing.Tuple[float, float]
    depth: float


class LandmarkProcessor:
    """Transforms raw hand tracking coordinates into structured fingertip data.

    Abstracts index pointer extraction and coordinate space transformations.
    Ensures that downstream application modules do not rely on raw tracking index
    conventions (e.g., hardcoded landmark indices).
    """

    # Metacarpophalangeal tracking index for the index fingertip in MediaPipe Hands
    INDEX_FINGER_TIP_INDEX = 8

    def __init__(self) -> None:
        """Initializes the LandmarkProcessor."""
        pass

    def extract_fingertip(
        self,
        landmarks: typing.List[Landmark],
        frame_width: int,
        frame_height: int,
    ) -> typing.Optional[FingertipData]:
        """Extracts and maps coordinates for the index fingertip.

        Args:
            landmarks: A list of 21 tracked `Landmark` data points.
            frame_width: The physical width of the video frame in pixels.
            frame_height: The physical height of the video frame in pixels.

        Returns:
            A `FingertipData` object containing mapped coordinates,
            or None if the tracking data is empty or incomplete.
        """
        # Validate that the hand tracking contains the index fingertip node
        if len(landmarks) <= self.INDEX_FINGER_TIP_INDEX:
            logger.warning(
                f"Incomplete landmark tracking. Expected at least "
                f"{self.INDEX_FINGER_TIP_INDEX + 1} nodes, got {len(landmarks)}."
            )
            return None

        # Extract the index fingertip landmark
        index_tip = landmarks[self.INDEX_FINGER_TIP_INDEX]

        # Convert normalized coordinates to pixel coordinates
        pixel_x = int(index_tip.x * frame_width)
        pixel_y = int(index_tip.y * frame_height)

        # Clip pixel values to ensure coordinates fall within frame bounds
        pixel_x = max(0, min(pixel_x, frame_width - 1))
        pixel_y = max(0, min(pixel_y, frame_height - 1))

        # Return structured data
        return FingertipData(
            pixel_coords=(pixel_x, pixel_y),
            normalized_coords=(index_tip.x, index_tip.y),
            depth=index_tip.z,
        )
