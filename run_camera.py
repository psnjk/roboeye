"""
Example usage of the RoboEye library
"""

import time

from picarx import Picarx
from camera import Camera
from display import Display

px = Picarx()

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
        i=0
        while i < 50:
            print("Taking a photo...")
            camera.take_photo(f"obstacle_photo_wall{i}")
            i+=1
            px.set_cam_pan_angle(30)
            time.sleep(2)
            px.set_cam_pan_angle(0)
            time.sleep(1)

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