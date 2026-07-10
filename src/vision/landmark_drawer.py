import typing
import cv2
import numpy as np

from src.vision.hand_tracker import Landmark
from src.vision.landmark_processor import FingertipData


class LandmarkDrawer:
    """Renders hand landmarks and skeletal structures onto OpenCV image frames.

    Provides a clean visualization utility separating rendering details from
    core image processing and hand tracking algorithms. Uses a custom premium
    color palette instead of generic RGB overlays.
    """

    # Hand joint connectivity layout mapping indices 0 to 20
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
        self.connection_color = (230, 216, 173)      # Premium Ice Blue (BGR)
        self.connection_thickness = 2

        self.joint_color = (95, 145, 255)            # Soft Peach/Coral (BGR)
        self.fingertip_color = (147, 20, 255)        # Vivid Coral Pink (BGR)
        self.wrist_color = (255, 255, 255)           # White (BGR)

        self.joint_radius = 5
        self.fingertip_radius = 7
        self.wrist_radius = 8

        # Target pointer visual styles
        self.target_outer_color = (0, 255, 255)      # Bright Neon Yellow/Green (BGR)
        self.target_outer_radius = 16
        self.target_outer_thickness = 2

        # Text overlay configurations
        self.text_color = (255, 255, 255)            # White text
        self.text_shadow_color = (0, 0, 0)           # Black shadow
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.font_thickness = 1

    def draw(
        self,
        frame: np.ndarray,
        landmarks: typing.List[Landmark],
        fingertip_data: typing.Optional[FingertipData] = None,
    ) -> np.ndarray:
        """Draws the tracking skeleton and joints onto the provided frame.

        Args:
            frame: A BGR OpenCV image matrix.
            landmarks: A list of 21 tracked `Landmark` data points.
            fingertip_data: Optional processed fingertip coordinates to overlay.

        Returns:
            The modified BGR image frame with overlays rendered.
        """
        height, width, _ = frame.shape

        # Step 1: Convert normalized landmark float coordinates to pixel coordinates
        pixel_coordinates: typing.List[typing.Tuple[int, int]] = []
        for lm in landmarks:
            px_x = int(lm.x * width)
            px_y = int(lm.y * height)
            px_x = max(0, min(px_x, width - 1))
            px_y = max(0, min(px_y, height - 1))
            pixel_coordinates.append((px_x, px_y))

        # Step 2: Render connection lines first
        for start_idx, end_idx in self.SKELETAL_CONNECTIONS:
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

        # Step 3: Draw circles over joints
        for i, pt in enumerate(pixel_coordinates):
            if i == 0:
                color = self.wrist_color
                radius = self.wrist_radius
            elif i in (4, 8, 12, 16, 20):
                color = self.fingertip_color
                radius = self.fingertip_radius
            else:
                color = self.joint_color
                radius = self.joint_radius

            cv2.circle(frame, pt, radius, color, cv2.FILLED, lineType=cv2.LINE_AA)

        # Step 4: Draw custom tracker pointer and coordinates overlay if fingertip data exists
        if fingertip_data is not None:
            px_x, px_y = fingertip_data.pixel_coords

            # Draw a distinct concentric ring around the target fingertip (landmark 8)
            cv2.circle(
                frame,
                (px_x, px_y),
                self.target_outer_radius,
                self.target_outer_color,
                self.target_outer_thickness,
                lineType=cv2.LINE_AA,
            )

            # Define coordinate label text
            coord_text = f"Pointer: ({px_x}, {px_y}) Z: {fingertip_data.depth:.2f}"
            
            # Place label slightly offset above and to the right of the fingertip
            text_x = px_x + 20
            text_y = px_y - 20

            # Prevent text drawing off-screen
            if text_x + 180 > width:
                text_x = px_x - 200
            if text_y - 15 < 0:
                text_y = px_y + 30

            # Render text drop shadow (for high contrast readability against bright feeds)
            cv2.putText(
                frame,
                coord_text,
                (text_x + 1, text_y + 1),
                self.font,
                self.font_scale,
                self.text_shadow_color,
                self.font_thickness + 1,
                lineType=cv2.LINE_AA,
            )
            # Render foreground text
            cv2.putText(
                frame,
                coord_text,
                (text_x, text_y),
                self.font,
                self.font_scale,
                self.text_color,
                self.font_thickness,
                lineType=cv2.LINE_AA,
            )

        return frame
