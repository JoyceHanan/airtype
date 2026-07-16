import logging

logger = logging.getLogger(__name__)


class TextBuffer:
    """Manages the state of the active text entry buffer.

    Encapsulates character insertion, special key operations (Backspace, Space,
    Enter), and capitalization logic. Operates independently of any visual
    drawing layers or tracking libraries.
    """

    def __init__(self) -> None:
        """Initializes the TextBuffer with empty contents."""
        self._text = ""
        self.shift_active = False

    def add_character(self, key_label: str) -> None:
        """Processes a keystroke label and updates the buffer state.

        Args:
            key_label: The logical label of the triggered key.
        """
        # 1. Handle special key Backspace
        if key_label == "Back":
            if len(self._text) > 0:
                self._text = self._text[:-1]
                logger.debug("Backspace triggered. Text buffer updated.")
            return

        # 2. Handle special key Space
        if key_label == "Space":
            self._text += " "
            logger.debug("Space triggered. Text buffer updated.")
            return

        # 3. Handle special key Shift
        if key_label == "Shift":
            self.shift_active = not self.shift_active
            logger.debug(f"Shift toggled: {self.shift_active}")
            return

        # 4. Handle special key Enter
        if key_label == "Enter":
            self._text += "\n"
            logger.debug("Enter triggered. Newline appended.")
            return

        # 5. Handle standard character typing
        # Layout characters are uppercase by default (e.g. 'A').
        # Type lowercase unless shift is active.
        if len(key_label) == 1:
            char = key_label.upper() if self.shift_active else key_label.lower()
            self._text += char
            logger.debug(f"Character '{char}' appended to text buffer.")

            # Auto-reset shift state after typing a single capital letter (mobile style)
            if self.shift_active:
                self.shift_active = False
                logger.debug("Shift state auto-released.")

    def get_text(self) -> str:
        """Retrieves the current text stored in the buffer.

        Returns:
            The raw text string.
        """
        return self._text

    def clear(self) -> None:
        """Clears the text buffer contents and resets states."""
        self._text = ""
        self.shift_active = False
        logger.info("Text buffer cleared.")
