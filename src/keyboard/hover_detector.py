import typing
from src.keyboard.key import Key


class HoverDetector:
    """Manages real-time hover calculations and coordinate collision checks.

    Utilizes 2D Point-in-Rectangle Axis-Aligned Bounding Box (AABB) checks
    to determine which key coordinates intersect the active fingertip.
    """

    def __init__(self) -> None:
        """Initializes the HoverDetector."""
        pass

    def check_hover(
        self,
        fingertip_coords: typing.Tuple[int, int],
        keys: typing.List[Key],
    ) -> typing.Optional[Key]:
        """Checks if fingertip coordinates reside inside the bounds of any key.

        Args:
            fingertip_coords: A tuple of (x, y) smoothed fingertip coordinates in pixel space.
            keys: A list of standard `Key` configurations to inspect.

        Returns:
            The intersected `Key` object if a collision occurs, otherwise None.
        """
        finger_x, finger_y = fingertip_coords

        for key in keys:
            # point-in-rectangle collision checks
            if (key.x <= finger_x < key.x + key.width) and (
                key.y <= finger_y < key.y + key.height
            ):
                return key

        return None
