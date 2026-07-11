import logging
import sys
import cv2

from src.camera.camera_manager import CameraManager
from src.vision.hand_tracker import HandTracker
from src.vision.landmark_drawer import LandmarkDrawer
from src.vision.landmark_processor import LandmarkProcessor

# Initialize logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Orchestrates the AirType real-time camera tracking pipeline.

    Links the video capture flow from `CameraManager`, extracts hand landmarks
    via `HandTracker`, processes coordinate metrics and filters jitter using
    `LandmarkProcessor`, renders overlays via `LandmarkDrawer`, and displays the feed.
    """
    logger.info("Starting AirType Camera, Vision, & Coordinate Smoothing Pipeline...")

    # Display configurations
    window_name = "AirType - Coordinate Smoothing"
    exit_key = "q"

    # Hardware configs
    camera_id = 0
    target_width = 640
    target_height = 480

    # Instantiate visualizer and analytical processors
    drawer = LandmarkDrawer()
    processor = LandmarkProcessor()

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

                # 3. If a hand is detected, process fingertip coordinates and overlay visual guides
                if landmarks is not None:
                    height, width, _ = frame.shape
                    
                    # Extract the index fingertip coordinates mapped to pixel space and smoothed
                    fingertip_data = processor.extract_fingertip(
                        landmarks=landmarks,
                        frame_width=width,
                        frame_height=height,
                    )
                    
                    # Overlay skeleton joints and coordinate HUD labels onto the frame
                    frame = drawer.draw(
                        frame=frame,
                        landmarks=landmarks,
                        fingertip_data=fingertip_data,
                    )
                else:
                    # Reset internal filter state when tracking is lost
                    processor.reset_filters()

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
        logger.info("AirType Pipeline shut down cleanly.")


if __name__ == "__main__":
    main()
