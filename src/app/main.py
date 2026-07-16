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
from src.input.text_buffer import TextBuffer

# Initialize logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Orchestrates the AirType real-time camera tracking and typing pipeline.

    Links video capture from `CameraManager`, processes hand tracking landmarks
    via `HandTracker`, tracks smoothed fingertip coordinates, checks key target overlaps
    via `HoverDetector`, tracks clicks via `TapDetector`, updates text values inside
    `TextBuffer`, renders overlays via `KeyboardRenderer`, visualizes hands via
    `LandmarkDrawer`, and displays the feed.
    """
    logger.info("Starting AirType Keyboard, Vision, Hover, Tap, & Text Pipeline...")

    # Display configurations
    window_name = "AirType - Virtual Keyboard Console"
    exit_key = "q"

    # Hardware configs
    camera_id = 0
    target_width = 640
    target_height = 480

    # Instantiate keyboard, collision, click, and text buffer layers
    layout = KeyboardLayout(width=target_width, height=target_height)
    keyboard_renderer = KeyboardRenderer()
    hover_detector = HoverDetector()
    tap_detector = TapDetector()
    text_buffer = TextBuffer()
    
    drawer = LandmarkDrawer()
    processor = LandmarkProcessor()

    # Frame loop counter (used to implement a blinking cursor)
    frame_counter = 0

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

                # Increment frame counter
                frame_counter += 1

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
                        
                        # Process keystroke entries into the text buffer on trigger events
                        if tap_triggered and hovered_key is not None:
                            text_buffer.add_character(hovered_key.label)
                            logger.info(f"Typed text state: '{text_buffer.get_text()}'")
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

                # 5. Render typing HUD displaying current text entries directly above the keyboard
                # Keyboard starts at Y coordinate 55% of frame height (264px on 480px screen)
                kb_y_start = int(target_height * 0.55)
                box_margin = 10
                box_x1 = box_margin
                box_x2 = target_width - box_margin
                box_y1 = kb_y_start - 55
                box_y2 = kb_y_start - 15
                box_height = box_y2 - box_y1
                
                # Blending Translucent background box
                hud_overlay = frame.copy()
                cv2.rectangle(
                    hud_overlay,
                    (box_x1, box_y1),
                    (box_x2, box_y2),
                    (45, 35, 35),  # Same dark navy background as keyboard
                    cv2.FILLED,
                )
                frame = cv2.addWeighted(
                    hud_overlay, 0.5, frame, 1.0 - 0.5, 0
                )

                # Drawing Opaque border outline
                cv2.rectangle(
                    frame,
                    (box_x1, box_y1),
                    (box_x2, box_y2),
                    (230, 216, 173),  # Ice Blue border
                    1,
                    lineType=cv2.LINE_AA,
                )

                # Generate blink cursor animation suffix (15 frames cycle)
                cursor = "|" if (frame_counter // 15) % 2 == 0 else " "
                display_str = text_buffer.get_text() + cursor

                # Prevent text overflow by dynamically cropping characters from left
                available_w = (box_x2 - box_x1) - 20
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_w = 1
                
                temp_str = display_str
                while len(temp_str) > 0:
                    (w, h), _ = cv2.getTextSize(temp_str, font, font_scale, font_w)
                    if w <= available_w:
                        break
                    temp_str = temp_str[1:]  # Crop left character

                # Compute baseline centered text coordinate
                text_x = box_x1 + 10
                text_y = box_y1 + int((box_height + h) / 2)

                # Render typed text
                cv2.putText(
                    frame,
                    temp_str,
                    (text_x, text_y),
                    font,
                    font_scale,
                    (255, 255, 255),
                    font_w,
                    lineType=cv2.LINE_AA,
                )

                # 6. Overlay skeleton joints and coordinate HUD labels on top of virtual keyboard
                if landmarks is not None:
                    frame = drawer.draw(
                        frame=frame,
                        landmarks=landmarks,
                        fingertip_data=fingertip_data,
                    )

                # 7. Render window display
                cv2.imshow(window_name, frame)

                # 8. Intercept exit signals
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
