import typing
import cv2
import numpy as np

from src.keyboard.key import Key


class KeyboardRenderer:
    """Renders virtual keys onto video frames using alpha-blending transparency.

    Maintains a premium glassmorphic overlay aesthetic, with highlighted states
    rendered dynamically for the active hovered key.
    """

    def __init__(self) -> None:
        """Initializes the KeyboardRenderer with custom styling variables."""
        # Standard key styling variables (BGR format)
        self.key_bg_color = (45, 35, 35)             # Translucent Dark Navy/Charcoal
        self.key_border_color = (230, 216, 173)      # Opaque Ice Blue
        self.text_color = (255, 255, 255)            # Opaque White
        self.border_thickness = 1
        
        # Hovered key styling overrides (BGR format)
        self.key_hover_bg_color = (130, 95, 55)      # Brighter Translucent Ice Blue
        self.key_hover_border_color = (255, 255, 0)  # Neon Cyan border highlight
        self.key_hover_text_color = (255, 255, 255)  # Opaque White text
        self.border_hover_thickness = 2

        self.alpha = 0.5                             # Fill transparency (0.0 to 1.0)
        
        # Text font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.font_thickness = 1

    def render(
        self,
        frame: np.ndarray,
        keys: typing.List[Key],
        hovered_key: typing.Optional[Key] = None,
    ) -> np.ndarray:
        """Renders the list of virtual keys and highlights the hovered key if present.

        Args:
            frame: A BGR OpenCV image matrix.
            keys: A list of standard `Key` configurations to draw.
            hovered_key: The optional `Key` currently under the fingertip.

        Returns:
            The modified BGR image frame with virtual keyboard overlays drawn.
        """
        # Create a copy overlay frame to render transparency fills
        overlay = frame.copy()

        # Step 1: Draw filled key backgrounds on the overlay frame
        for key in keys:
            # Shift background fill color if the key is currently hovered
            bg_color = (
                self.key_hover_bg_color
                if hovered_key and key.label == hovered_key.label
                else self.key_bg_color
            )
            
            cv2.rectangle(
                overlay,
                (key.x, key.y),
                (key.x + key.width, key.y + key.height),
                bg_color,
                cv2.FILLED,
            )

        # Blend the transparent overlay onto the original base frame
        frame = cv2.addWeighted(
            overlay, self.alpha, frame, 1.0 - self.alpha, 0
        )

        # Step 2: Draw borders and centered labels directly on the blended frame
        for key in keys:
            is_hovered = hovered_key and key.label == hovered_key.label

            # Apply hover style overrides
            border_color = (
                self.key_hover_border_color if is_hovered else self.key_border_color
            )
            border_w = (
                self.border_hover_thickness if is_hovered else self.border_thickness
            )
            text_color = (
                self.key_hover_text_color if is_hovered else self.text_color
            )
            text_thickness = (
                self.font_thickness + 1 if is_hovered else self.font_thickness
            )

            # Draw key border
            cv2.rectangle(
                frame,
                (key.x, key.y),
                (key.x + key.width, key.y + key.height),
                border_color,
                border_w,
                lineType=cv2.LINE_AA,
            )

            # Center text calculations
            (text_width, text_height), baseline = cv2.getTextSize(
                key.label, self.font, self.font_scale, text_thickness
            )
            text_x = key.x + int((key.width - text_width) / 2)
            text_y = key.y + int((key.height + text_height) / 2)

            # Draw key label character
            cv2.putText(
                frame,
                key.label,
                (text_x, text_y),
                self.font,
                self.font_scale,
                text_color,
                text_thickness,
                lineType=cv2.LINE_AA,
            )

        return frame
