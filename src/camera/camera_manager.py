import logging
import typing
import cv2
import numpy as np

# Configure logging for the camera module
logger = logging.getLogger(__name__)


class CameraManager:
    """Manages the webcam lifecycle, frame acquisition, and cleanup.

    This class abstracts OpenCV's VideoCapture interface, providing safe
    resource management through context manager protocols (`__enter__` and
    `__exit__`). It ensures that camera resources are bound and released
    deterministically.
    """

    def __init__(
        self,
        camera_id: int = 0,
        width: typing.Optional[int] = None,
        height: typing.Optional[int] = None,
    ) -> None:
        """Initializes the CameraManager configuration.

        Args:
            camera_id: The index of the camera device to bind (default: 0).
            width: Optional target width resolution for the capture stream.
            height: Optional target height resolution for the capture stream.
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self._cap: typing.Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        """Initializes the webcam device.

        Raises:
            RuntimeError: If the webcam device fails to open.
        """
        if self._cap is not None and self._cap.isOpened():
            logger.warning("Camera is already open.")
            return

        logger.info(f"Initializing camera device index {self.camera_id}...")
        self._cap = cv2.VideoCapture(self.camera_id)

        if not self._cap.isOpened():
            self._cap = None
            raise RuntimeError(
                f"Failed to open webcam device with index {self.camera_id}. "
                "Verify camera connection and permissions."
            )

        # Apply custom resolution overrides if specified
        if self.width is not None:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height is not None:
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Log actual initialized resolution
        actual_w = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_h = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        logger.info(f"Camera opened successfully. Resolution: {actual_w}x{actual_h}")

    def read_frame(self) -> typing.Tuple[bool, typing.Optional[np.ndarray]]:
        """Reads the latest video frame from the webcam capture stream.

        Returns:
            A tuple containing:
                - bool: True if the frame was successfully read, False otherwise.
                - ndarray or None: The acquired frame matrix (BGR), or None if the
                  read failed or if the camera is not initialized.
        """
        if self._cap is None or not self._cap.isOpened():
            logger.error("Attempted to read frame while camera was closed.")
            return False, None

        success, frame = self._cap.read()
        if not success or frame is None:
            logger.warning("Failed to retrieve frame from video capture stream.")
            return False, None

        return True, frame

    def release(self) -> None:
        """Safely releases the webcam device and clears the internal capture handle."""
        if self._cap is not None:
            logger.info("Releasing camera device resources...")
            if self._cap.isOpened():
                self._cap.release()
            self._cap = None
            logger.info("Camera resources released successfully.")

    def __enter__(self) -> "CameraManager":
        """Context manager entry point. Automatically opens the camera connection.

        Returns:
            The initialized CameraManager instance.
        """
        self.open()
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[typing.Any],
    ) -> None:
        """Context manager exit point. Ensures resources are released on scope exit."""
        self.release()
