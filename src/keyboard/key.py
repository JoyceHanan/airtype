from dataclasses import dataclass


@dataclass
class Key:
    """Represents the data model and boundaries of a single virtual key.

    This class stores only coordinate boundaries and state data, keeping it
    decoupled from rendering APIs (like OpenCV) and layout positioning calculations.
    """
    label: str
    x: int
    y: int
    width: int
    height: int
