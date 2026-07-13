import typing
from src.keyboard.key import Key


class KeyboardLayout:
    """Manages virtual keyboard configurations and generates key geometries.

    Constructs a dynamic QWERTY grid layout scaled relative to screen canvas
    dimensions. Position computations are kept decoupled from visual drawing styles.
    """

    # QWERTY Key Rows definitions
    ROW_1 = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]
    ROW_2 = ["A", "S", "D", "F", "G", "H", "J", "K", "L"]
    ROW_3 = ["Z", "X", "C", "V", "B", "N", "M", "Back"]  # Back = Backspace

    def __init__(self, width: int = 640, height: int = 480) -> None:
        """Initializes and computes layouts for the virtual keyboard.

        Args:
            width: Total frame width in pixels.
            height: Total frame height in pixels.
        """
        self.width = width
        self.height = height
        self.keys: typing.List[Key] = []
        self._generate_qwerty_layout()

    def _generate_qwerty_layout(self) -> None:
        """Calculates grid coordinates and sizes mapping a QWERTY layout.

        Places keys in the lower 40% of the screen area, leaving the top portion
        clear for hand visual tracking indicator overlays.
        """
        # Keyboard bounding box constraints
        kb_y_start = int(self.height * 0.55)
        kb_height = int(self.height * 0.40)
        row_height = int(kb_height / 4)
        margin = 4  # Gap between adjacent key boxes

        # Base key width determined by 10 keys across in Row 1
        base_key_width = int((self.width - (margin * 11)) / 10)

        # Row 1 layout: 10 keys
        y1 = kb_y_start
        for i, char in enumerate(self.ROW_1):
            x = margin + i * (base_key_width + margin)
            self.keys.append(
                Key(
                    label=char,
                    x=x,
                    y=y1,
                    width=base_key_width,
                    height=row_height - margin,
                )
            )

        # Row 2 layout: 9 keys (horizontally centered)
        y2 = kb_y_start + row_height
        row2_width = 9 * base_key_width + 8 * margin
        row2_x_start = int((self.width - row2_width) / 2)
        for i, char in enumerate(self.ROW_2):
            x = row2_x_start + i * (base_key_width + margin)
            self.keys.append(
                Key(
                    label=char,
                    x=x,
                    y=y2,
                    width=base_key_width,
                    height=row_height - margin,
                )
            )

        # Row 3 layout: 7 letters + 1 double-width Backspace key
        y3 = kb_y_start + (2 * row_height)
        # 7 normal keys + 1 Backspace (2 * base_key_width) + margins
        row3_width = 9 * base_key_width + 8 * margin
        row3_x_start = int((self.width - row3_width) / 2)
        for i, char in enumerate(self.ROW_3):
            x = row3_x_start + i * (base_key_width + margin)
            w = base_key_width
            # Double-width assignment for Backspace
            if char == "Back":
                w = (base_key_width * 2) + margin
            self.keys.append(
                Key(label=char, x=x, y=y3, width=w, height=row_height - margin)
            )

        # Row 4 layout: 1 spacebar (centered, width equivalent to 6 base keys)
        y4 = kb_y_start + (3 * row_height)
        spacebar_width = (base_key_width * 6) + (margin * 5)
        space_x_start = int((self.width - spacebar_width) / 2)
        self.keys.append(
            Key(
                label="Space",
                x=space_x_start,
                y=y4,
                width=spacebar_width,
                height=row_height - margin,
            )
        )

    def get_keys(self) -> typing.List[Key]:
        """Returns the list of generated virtual keys.

        Returns:
            A list of active `Key` instances.
        """
        return self.keys
