import logging

logger = logging.getLogger(__name__)


class TextBuffer:
    """A pure data store that maintains the typed string state.

    This class has no knowledge of keyboard layouts, visual UI rendering, or
    input gesture logic, serving as a clean receiver of text updates.
    """

    def __init__(self) -> None:
        """Initializes the TextBuffer with empty contents."""
        self._text = ""

    def insert_character(self, char: str) -> None:
        """Appends a character directly to the text buffer.

        Args:
            char: The character string to append.
        """
        self._text += char
        logger.debug(f"Buffer insert: '{char}' -> Current: '{self._text}'")

    def delete_back(self) -> None:
        """Deletes the trailing character from the buffer."""
        if len(self._text) > 0:
            self._text = self._text[:-1]
            logger.debug(f"Buffer delete. Current: '{self._text}'")

    def get_text(self) -> str:
        """Retrieves the current text stored in the buffer.

        Returns:
            The raw text string.
        """
        return self._text

    def clear(self) -> None:
        """Clears the text buffer contents."""
        self._text = ""
        logger.info("Buffer cleared.")
