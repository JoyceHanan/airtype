import typing
import cv2
import numpy as np

from src.vision.hand_tracker import Landmark


class LandmarkDrawer:
    """Renders hand landmarks and skeletal structures onto OpenCV image frames.

    Provides a clean visualization utility separating rendering details from
    core image processing and hand tracking algorithms. Uses a custom premium
    color palette instead of generic RGB overlays.
    """

    # Hand joint connectivity layout mapping indices 0 to 20
    # Defined explicitly to eliminate dependencies on MediaPipe drawing utilities
    SKELETAL_CONNECTIONS = (
        # Thumb
        (0, 1), (1, 2), (2, 3), (3, 4),
        # Index Finger
        (0, 5), (5, 6), (6, 7), (7, 8),
        # Middle Finger
        (9, 10), (10, 11), (11, 12),
        # Ring Finger
        (13, 14), (14, 15), (15, 16),
        # Pinky Finger
        (0, 17), (17, 18), (18, 19), (19, 20),
        # Knuckle Connections (Carpal arc connection)
        (5, 9), (9, 13), (13, 17)
    )

    def __init__(self) -> None:
        """Initializes the drawer with custom design-themed visual aesthetics."""
        # Visual styling settings (using BGR color layouts)
        self.connection_color = (230, 216, 173)  # Premium Ice Blue (BGR)
        self.connection_thickness = 2

        self.joint_color = (95, 145, 255)       # Soft Peach/Coral (BGR)
        self.fingertip_color = (147, 20, 255)   # Vivid Coral Pink (BGR)
        self.wrist_color = (255, 255, 255)      # White (BGR)

        self.joint_radius = 5
        self.fingertip_radius = 7
        self.wrist_radius = 8

    def draw(
        self, frame: np.ndarray, landmarks: typing.List[Landmark]
    ) -> np.ndarray:
        """Draws the tracking skeleton and joints onto the provided frame.

        Args:
            frame: A BGR OpenCV image matrix.
            landmarks: A list of 21 tracked `Landmark` data points.

        Returns:
            The modified BGR image frame with overlays rendered.
        """
        height, width, _ = frame.shape

        # Step 1: Convert normalized landmark float coordinates to pixel coordinates
        pixel_coordinates: typing.List[typing.Tuple[int, int]] = []
        for lm in landmarks:
            px_x = int(lm.x * width)
            px_y = int(lm.y * height)
            # Clip pixel coordinates to frame boundaries to prevent off-screen draw errors
            px_x = max(0, min(px_x, width - 1))
            px_y = max(0, min(px_y, height - 1))
            pixel_coordinates.append((px_x, px_y))

        # Step 2: Render connection lines first (ensures dots render on top of line endpoints)
        for start_idx, end_idx in self.SKELETAL_CONNECTIONS:
            # Safeguard index out of bounds in case of incomplete/corrupted input data
            if start_idx < len(pixel_coordinates) and end_idx < len(pixel_coordinates):
                start_pt = pixel_coordinates[start_idx]
                end_pt = pixel_coordinates[end_idx]
                cv2.line(
                    frame,
                    start_pt,
                    end_pt,
                    self.connection_color,
                    self.connection_thickness,
                    lineType=cv2.LINE_AA,
                )

        # Step 3: Draw circles over joints, applying custom sizes and colors based on importance
        for i, pt in enumerate(pixel_coordinates):
            if i == 0:
                # Wrist node (anchor)
                color = self.wrist_color
                radius = self.wrist_radius
            elif i in (4, 8, 12, 16, 20):
                # Fingertips (critical tracking points for virtual typing)
                color = self.fingertip_color
                radius = self.fingertip_radius
            else:
                # Normal joints
                color = self.joint_color
                radius = self.joint_radius

            cv2.circle(frame, pt, radius, color, cv2.FILLED, lineType=cv2.LINE_AA)

        return frame
