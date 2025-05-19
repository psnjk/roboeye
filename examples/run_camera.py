"""
Example usage of the RoboEye library
"""

import time
from roboeye import Camera, Display


def main():
    try:
        # Initialize camera (with optional parameters)
        camera = Camera(
            size=(640, 480),  # Resolution (width, height)
            vflip=False,  # Vertical flip
            hflip=False  # Horizontal flip
        )

        # Start the camera
        print("Starting camera...")
        camera.start()

        # Show FPS counter
        camera.show_fps(True)

        # Initialize display
        display = Display(camera)

        # Enable display options
        display.show(
            local=True,  # Show in local window
            web=True,  # Enable web streaming
            port=9000  # Port for web streaming
        )

        # Take a photo
        print("Taking a photo...")
        camera.take_photo("test_photo")

        # Run for 30 seconds
        print("Running for 30 seconds...")
        time.sleep(30)

        # Clean up
        print("Cleaning up...")
        display.close()
        camera.stop()

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ensure cleanup
        camera.stop()


if __name__ == "__main__":
    main()