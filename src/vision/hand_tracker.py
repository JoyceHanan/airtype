import logging
import typing
from dataclasses import dataclass
import cv2
import mediapipe as mp
import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Landmark:
    """Represents a normalized 3D hand landmark coordinate.

    Attributes:
        x: Horizontal coordinate normalized between 0.0 and 1.0 (relative to image width).
        y: Vertical coordinate normalized between 0.0 and 1.0 (relative to image height).
        z: Depth coordinate representing the distance of the landmark from the wrist.
           Calculated relative to hand size scale, with smaller values closer to the camera.
    """
    x: float
    y: float
    z: float


class HandTracker:
    """Encapsulates MediaPipe Hands pipeline for single hand landmark extraction.

    This class initializes the MediaPipe graph and transforms the raw tracking
    protobuf output into a list of clean, decoupled `Landmark` data objects.
    It supports the context manager protocol to clean up underlying C++ graph state.
    """

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 1,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.7,
    ) -> None:
        """Initializes the HandTracker service.

        Args:
            static_image_mode: If False, treats input images as a video stream
                to optimize landmark tracking over sequential frames.
            max_num_hands: Maximum number of hands to detect. AirType defaults to 1.
            min_detection_confidence: Minimum confidence value (0.0 to 1.0) for
                hand detection to be considered successful.
            min_tracking_confidence: Minimum confidence value (0.0 to 1.0) for
                landmark tracking to remain locked.
        """
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self._mp_hands = mp.solutions.hands
        self._hands: typing.Optional[mp.solutions.hands.Hands] = None

    def open(self) -> None:
        """Initializes the underlying MediaPipe Hands tracker graph."""
        if self._hands is not None:
            logger.warning("MediaPipe Hands tracker is already open.")
            return

        logger.info("Initializing MediaPipe Hands pipeline...")
        self._hands = self._mp_hands.Hands(
            static_image_mode=self.static_image_mode,
            max_num_hands=self.max_num_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )
        logger.info("MediaPipe Hands pipeline successfully initialized.")

    def process_frame(
        self, frame: np.ndarray
    ) -> typing.Optional[typing.List[Landmark]]:
        """Processes a single BGR image frame and extracts hand landmarks if present.

        Args:
            frame: A BGR OpenCV image matrix.

        Returns:
            A list of 21 `Landmark` instances corresponding to the tracked hand joints,
            or None if no hand is detected in the input frame.
        """
        if self._hands is None:
            raise RuntimeError(
                "Attempted to process frame, but HandTracker has not been opened. "
                "Ensure open() is called or run tracker inside a 'with' block."
            )

        # MediaPipe requires RGB frame configurations
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return None

        # AirType tracks only a single hand (first detected instance)
        hand_landmarks = results.multi_hand_landmarks[0]

        # Extract landmarks into clean dataclass objects
        extracted_landmarks = [
            Landmark(x=lm.x, y=lm.y, z=lm.z)
            for lm in hand_landmarks.landmark
        ]

        return extracted_landmarks

    def close(self) -> None:
        """Closes the MediaPipe Hands graph and releases C++ resources."""
        if self._hands is not None:
            logger.info("Closing MediaPipe Hands graph...")
            self._hands.close()
            self._hands = None
            logger.info("MediaPipe Hands resources freed successfully.")

    def __enter__(self) -> "HandTracker":
        """Context manager entry point. Instantiates MediaPipe Hands interface."""
        self.open()
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[typing.Any],
    ) -> None:
        """Context manager exit point. Automatically closes the MediaPipe Hands graph."""
        self.close()
