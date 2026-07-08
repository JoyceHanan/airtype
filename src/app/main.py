import logging
import sys
import cv2

from src.camera.camera_manager import CameraManager

# Initialize logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Orchestrates the lifecycle of the AirType camera pipeline.

    Main entry point that opens the camera stream using `CameraManager`, runs
    the frame processing loop, renders the output, and listens for the escape
    sequence to exit the application cleanly.
    """
    logger.info("Starting AirType Camera Pipeline...")

    # Display configuration
    window_name = "AirType - Camera Feed"
    exit_key = "q"

    # Define camera configurations (e.g. target 640x480 resolution)
    camera_id = 0
    target_width = 640
    target_height = 480

    try:
        # Use the CameraManager context manager to ensure deterministic cleanup
        with CameraManager(
            camera_id=camera_id, width=target_width, height=target_height
        ) as camera:
            logger.info(f"Press '{exit_key}' in the video window to quit.")

            while True:
                # Retrieve the latest frame from the webcam
                success, frame = camera.read_frame()
                if not success or frame is None:
                    logger.error("Failed to capture frame. Exiting loop.")
                    break

                # Render the webcam feed frame to the screen
                cv2.imshow(window_name, frame)

                # Wait for 1 millisecond and check for the escape key ('q')
                # 0xFF mask isolates the keycode on various platform configurations
                key = cv2.waitKey(1) & 0xFF
                if key == ord(exit_key):
                    logger.info("Exit key pressed by user. Shutting down...")
                    break

    except RuntimeError as err:
        logger.critical(f"Camera Initialization Error: {err}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application interrupted via keyboard. Initiating exit...")
    except Exception as ex:
        logger.critical(f"Unexpected application failure: {ex}", exc_info=True)
        sys.exit(1)
    finally:
        # OpenCV window destruction is managed here in the application context
        cv2.destroyAllWindows()
        logger.info("AirType Camera Pipeline shut down cleanly.")


if __name__ == "__main__":
    main()
