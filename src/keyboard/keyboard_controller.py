import logging
from src.input.text_buffer import TextBuffer

logger = logging.getLogger(__name__)


class KeyboardController:
    """Manages the behavioral logic and state variables of the virtual keyboard.

    Handles states like Shift (temporary capitalization) and Caps Lock (persistent
    capitalization), and maps physical/virtual keystroke signals into generic
    text operations forwarded to the TextBuffer.
    """

    def __init__(self, text_buffer: TextBuffer) -> None:
        """Initializes the KeyboardController.

        Args:
            text_buffer: The target `TextBuffer` memory model instance.
        """
        self.text_buffer = text_buffer
        self.shift_active = False
        self.caps_lock_active = False

    def handle_keypress(self, key_label: str) -> None:
        """Translates a virtual key press event and applies keyboard state rules.

        Args:
            key_label: The string label of the key that was pressed.
        """
        # 1. Handle special key Backspace
        if key_label == "Back":
            self.text_buffer.delete_back()
            logger.debug("Keystroke Back: Deleted trailing character.")
            return

        # 2. Handle special key Space
        if key_label == "Space":
            self.text_buffer.insert_character(" ")
            logger.debug("Keystroke Space: Inserted space character.")
            return

        # 3. Handle special key Enter
        if key_label == "Enter":
            self.text_buffer.insert_character("\n")
            logger.debug("Keystroke Enter: Inserted newline character.")
            return

        # 4. Handle Shift (Temporary capitalization toggle)
        if key_label == "Shift":
            self.shift_active = not self.shift_active
            if self.shift_active:
                self.caps_lock_active = False  # Shift releases Caps Lock
            logger.info(f"Shift state toggled: {self.shift_active}")
            return

        # 5. Handle Caps Lock (Persistent capitalization toggle)
        if key_label == "Caps":
            self.caps_lock_active = not self.caps_lock_active
            if self.caps_lock_active:
                self.shift_active = False  # Caps Lock releases Shift
            logger.info(f"Caps Lock state toggled: {self.caps_lock_active}")
            return

        # 6. Handle standard alphanumeric keys
        if len(key_label) == 1:
            # Shift or Caps Lock forces uppercase
            use_uppercase = self.shift_active or self.caps_lock_active
            char = key_label.upper() if use_uppercase else key_label.lower()

            self.text_buffer.insert_character(char)
            logger.debug(f"Keystroke printed: '{char}'")

            # Temporary Shift state auto-releases after one character input
            if self.shift_active:
                self.shift_active = False
                logger.debug("Shift state auto-released after keypress.")
