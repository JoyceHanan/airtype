import logging
import sys
import cv2

from src.camera.camera_manager import CameraManager
from src.vision.hand_tracker import HandTracker
from src.vision.landmark_drawer import LandmarkDrawer
from src.vision.landmark_processor import LandmarkProcessor
from src.keyboard.keyboard_layout import KeyboardLayout
from src.keyboard.keyboard_renderer import KeyboardRenderer
from src.keyboard.hover_detector import HoverDetector
from src.input.tap_detector import TapDetector

# Initialize logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Orchestrates the AirType real-time camera, tracking, keyboard, and input pipeline.

    Links video capture from `CameraManager`, processes hand landmarks via `HandTracker`,
    extracts smoothed coordinates via `LandmarkProcessor`, checks key target overlaps
    via `HoverDetector`, tracks click gestures via `TapDetector`, renders UI layouts
    via `KeyboardRenderer`, visualizes hands via `LandmarkDrawer`, and displays the feed.
    """
    logger.info("Starting AirType Keyboard, Vision, Hover, & Tap Processing Pipeline...")

    # Display configurations
    window_name = "AirType - Tap Detection"
    exit_key = "q"

    # Hardware configs
    camera_id = 0
    target_width = 640
    target_height = 480

    # Instantiate keyboard, collision, and click detection components
    layout = KeyboardLayout(width=target_width, height=target_height)
    keyboard_renderer = KeyboardRenderer()
    hover_detector = HoverDetector()
    tap_detector = TapDetector()
    
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

                # 2. Extract hand joints from the frame
                landmarks = tracker.process_frame(frame)

                fingertip_data = None
                hovered_key = None

                # 3. If hand landmarks are visible, process coordinates and calculate hover/tap actions
                if landmarks is not None:
                    height, width, _ = frame.shape
                    
                    # Extract the index fingertip coordinates mapped to pixel space and smoothed
                    fingertip_data = processor.extract_fingertip(
                        landmarks=landmarks,
                        frame_width=width,
                        frame_height=height,
                    )
                    
                    if fingertip_data is not None:
                        # Determine which key the user is targeting
                        hovered_key = hover_detector.check_hover(
                            fingertip_coords=fingertip_data.pixel_coords,
                            keys=layout.get_keys(),
                        )
                        
                        # Process click detection on Z-depth coordinate
                        tap_triggered = tap_detector.update(fingertip_data.depth)
                        
                        # Emit a print statement only on the exact click transition event
                        if tap_triggered and hovered_key is not None:
                            print(
                                f"[KEYPRESS] Entered key: {hovered_key.label}",
                                flush=True,
                            )
                else:
                    # Reset internal filter and state machine history when tracking is lost
                    processor.reset_filters()
                    tap_detector.reset()

                # 4. Render virtual keyboard overlays (highlighting active hover states)
                frame = keyboard_renderer.render(
                    frame=frame,
                    keys=layout.get_keys(),
                    hovered_key=hovered_key,
                )

                # 5. Overlay skeleton joints and coordinate HUD labels on top of virtual keyboard
                if landmarks is not None:
                    frame = drawer.draw(
                        frame=frame,
                        landmarks=landmarks,
                        fingertip_data=fingertip_data,
                    )

                # 6. Render window display
                cv2.imshow(window_name, frame)

                # 7. Intercept exit signals
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
