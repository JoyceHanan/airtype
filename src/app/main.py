import logging
import sys
import cv2

from src.camera.camera_manager import CameraManager
from src.vision.hand_tracker import HandTracker
from src.vision.landmark_drawer import LandmarkDrawer

# Initialize logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Orchestrates the AirType real-time camera tracking pipeline.

    Links the video capture flow from `CameraManager`, extracts hand features
    via `HandTracker`, passes tracking coordinates to `LandmarkDrawer` for
    visualization overlays, and renders the feed.
    """
    logger.info("Starting AirType Camera & Vision Tracking Pipeline...")

    # Display configurations
    window_name = "AirType - Hand Tracking"
    exit_key = "q"

    # Hardware configs
    camera_id = 0
    target_width = 640
    target_height = 480

    # Instantiate the drawer helper
    drawer = LandmarkDrawer()

    try:
        # Context managers guarantee correct cleanup on unexpected execution failure
        with CameraManager(
            camera_id=camera_id, width=target_width, height=target_height
        ) as camera, HandTracker(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        ) as tracker:

            logger.info(f"Press '{exit_key}' in the video window to quit.")

            while True:
                # 1. Capture the latest camera image frame
                success, frame = camera.read_frame()
                if not success or frame is None:
                    logger.error("Failed to capture frame. Exiting loop.")
                    break

                # 2. Extract hand joints from the image
                landmarks = tracker.process_frame(frame)

                # 3. Draw overlay if a hand is visible in the frame
                if landmarks is not None:
                    frame = drawer.draw(frame, landmarks)

                # 4. Render window display
                cv2.imshow(window_name, frame)

                # 5. Intercept exit signals
                key = cv2.waitKey(1) & 0xFF
                if key == ord(exit_key):
                    logger.info("Exit key pressed by user. Shutting down...")
                    break

    except RuntimeError as err:
        logger.critical(f"Pipeline Initialization Failure: {err}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application interrupted via keyboard. Initiating exit...")
    except Exception as ex:
        logger.critical(f"Unexpected pipeline failure: {ex}", exc_info=True)
        sys.exit(1)
    finally:
        # Ensure window cleanups are covered under all scopes
        cv2.destroyAllWindows()
        logger.info("AirType Tracking Pipeline shut down cleanly.")


if __name__ == "__main__":
    main()
