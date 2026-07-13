import typing
import cv2
import numpy as np

from src.keyboard.key import Key


class KeyboardRenderer:
    """Renders virtual keys onto video frames using alpha-blending transparency.

    Maintains a premium glassmorphic overlay aesthetic (semi-transparent backgrounds
    with sharp, fully-opaque borders and centered text).
    """

    def __init__(self) -> None:
        """Initializes the KeyboardRenderer with custom styling variables."""
        # Key styling configuration variables (BGR format)
        self.key_bg_color = (45, 35, 35)         # Semi-transparent Dark Navy/Charcoal
        self.key_border_color = (230, 216, 173)  # Opaque Ice Blue
        self.text_color = (255, 255, 255)        # Opaque White
        
        self.border_thickness = 1
        self.alpha = 0.5                         # Background fill transparency (0.0 to 1.0)
        
        # Text font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.font_thickness = 1

    def render(self, frame: np.ndarray, keys: typing.List[Key]) -> np.ndarray:
        """Renders the list of virtual keys onto the provided image frame.

        Args:
            frame: A BGR OpenCV image matrix.
            keys: A list of `Key` instances representing active keys.

        Returns:
            The modified BGR image frame with virtual keyboard overlays drawn.
        """
        # Create a copy overlay frame to render transparency fills
        overlay = frame.copy()

        # Step 1: Draw filled key backgrounds on the overlay frame
        for key in keys:
            cv2.rectangle(
                overlay,
                (key.x, key.y),
                (key.x + key.width, key.y + key.height),
                self.key_bg_color,
                cv2.FILLED,
            )

        # Blend the transparent overlay onto the original base frame
        # alpha controls key fills transparency; borders and text are drawn opaque on top
        frame = cv2.addWeighted(
            overlay, self.alpha, frame, 1.0 - self.alpha, 0
        )

        # Step 2: Draw borders and centered labels directly on the blended frame
        for key in keys:
            # Draw crisp border
            cv2.rectangle(
                frame,
                (key.x, key.y),
                (key.x + key.width, key.y + key.height),
                self.key_border_color,
                self.border_thickness,
                lineType=cv2.LINE_AA,
            )

            # Center key label calculation
            # Get text bounding dimensions
            (text_width, text_height), baseline = cv2.getTextSize(
                key.label, self.font, self.font_scale, self.font_thickness
            )

            # Center coordinate shifts inside the key bounding box
            text_x = key.x + int((key.width - text_width) / 2)
            text_y = key.y + int((key.height + text_height) / 2)

            # Draw key label character
            cv2.putText(
                frame,
                key.label,
                (text_x, text_y),
                self.font,
                self.font_scale,
                self.text_color,
                self.font_thickness,
                lineType=cv2.LINE_AA,
            )

        return frame
