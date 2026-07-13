import logging
import sys
import cv2

from src.camera.camera_manager import CameraManager
from src.vision.hand_tracker import HandTracker
from src.vision.landmark_drawer import LandmarkDrawer
from src.vision.landmark_processor import LandmarkProcessor
from src.keyboard.keyboard_layout import KeyboardLayout
from src.keyboard.keyboard_renderer import KeyboardRenderer

# Initialize logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Orchestrates the AirType real-time camera tracking and keyboard pipeline.

    Links video capture from `CameraManager`, renders a virtual keyboard overlay
    using `KeyboardLayout` and `KeyboardRenderer`, extracts hand tracking landmarks
    via `HandTracker`, processes smoothing via `LandmarkProcessor`, overlays sketches
    via `LandmarkDrawer`, and renders the feed.
    """
    logger.info("Starting AirType Keyboard & Vision Pipeline...")

    # Display configurations
    window_name = "AirType - Virtual Keyboard"
    exit_key = "q"

    # Hardware configs
    camera_id = 0
    target_width = 640
    target_height = 480

    # Instantiate keyboard configuration and visual drawing managers
    layout = KeyboardLayout(width=target_width, height=target_height)
    keyboard_renderer = KeyboardRenderer()
    
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

                # 2. Render virtual keyboard overlays onto raw frame (drawn first)
                frame = keyboard_renderer.render(frame, layout.get_keys())

                # 3. Extract hand joints from the frame
                landmarks = tracker.process_frame(frame)

                # 4. If hand landmarks are visible, process coordinates and draw tracking indicators on top
                if landmarks is not None:
                    height, width, _ = frame.shape
                    
                    # Extract the index fingertip coordinates mapped to pixel space and smoothed
                    fingertip_data = processor.extract_fingertip(
                        landmarks=landmarks,
                        frame_width=width,
                        frame_height=height,
                    )
                    
                    # Overlay skeleton joints and coordinate HUD labels on top of virtual keyboard
                    frame = drawer.draw(
                        frame=frame,
                        landmarks=landmarks,
                        fingertip_data=fingertip_data,
                    )
                else:
                    # Reset internal filter state when tracking is lost
                    processor.reset_filters()

                # 5. Render window display
                cv2.imshow(window_name, frame)

                # 6. Intercept exit signals
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
