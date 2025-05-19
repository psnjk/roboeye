"""
Core camera functionality for the RoboEye library
"""

import os
import time
import threading
import cv2
import numpy as np
from picamera2 import Picamera2
import libcamera


class Camera:
    """Camera class to handle camera operations"""

    def __init__(self, size=(640, 480), vflip=False, hflip=False):
        """Initialize the camera with given parameters

        Args:
            size (tuple): Camera resolution (width, height)
            vflip (bool): Flip camera vertically
            hflip (bool): Flip camera horizontally
        """
        self.camera_size = size
        self.camera_width = size[0]
        self.camera_height = size[1]
        self.camera_vflip = vflip
        self.camera_hflip = hflip

        # Camera state
        self.is_running = False
        self.camera_thread = None
        self.picam = None

        # Frame storage - accessible from outside the class
        self.current_frame = None

        # FPS calculation
        self.fps = 0
        self.draw_fps = False
        self.fps_origin = (self.camera_width - 105, 20)
        self.fps_size = 0.6
        self.fps_color = (255, 255, 255)

    def start(self):
        """Start the camera in a separate thread"""
        if self.is_running:
            print("Camera is already running")
            return

        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.camera_thread.start()

        # Wait for camera to start
        start_time = time.time()
        while not self.is_running and time.time() - start_time < 5:
            time.sleep(0.1)

        if not self.is_running:
            raise RuntimeError("Failed to start camera")

        return True

    def stop(self):
        """Stop the camera gracefully"""
        if not self.is_running:
            return

        self.is_running = False
        if self.camera_thread:
            self.camera_thread.join(timeout=3)
            self.camera_thread = None

    def _camera_loop(self):
        """Main camera loop running in separate thread"""
        try:
            # Initialize picamera2
            self.picam = Picamera2()

            # Configure preview
            preview_config = self.picam.preview_configuration
            preview_config.size = self.camera_size
            preview_config.format = 'RGB888'
            preview_config.transform = libcamera.Transform(
                hflip=self.camera_hflip,
                vflip=self.camera_vflip
            )
            preview_config.colour_space = libcamera.ColorSpace.Sycc()
            preview_config.buffer_count = 4
            preview_config.queue = True
            preview_config.controls = {'FrameRate': 30}

            # Start camera
            self.picam.configure(preview_config)
            self.picam.start()
            self.is_running = True

            # FPS tracking
            fps_counter = 0
            fps_timer = time.time()

            # Main capture loop
            while self.is_running:
                # Capture frame
                frame = self.picam.capture_array()

                # Calculate FPS
                fps_counter += 1
                elapsed_time = time.time() - fps_timer
                if elapsed_time > 1.0:
                    self.fps = round(fps_counter / elapsed_time, 1)
                    fps_counter = 0
                    fps_timer = time.time()

                # Draw FPS if enabled
                if self.draw_fps:
                    cv2.putText(
                        frame,
                        f"FPS: {self.fps}",
                        self.fps_origin,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        self.fps_size,
                        self.fps_color,
                        1,
                        cv2.LINE_AA
                    )

                # Update current frame
                self.current_frame = frame

        except Exception as e:
            print(f"Camera error: {e}")
            self.is_running = False
        finally:
            if self.picam:
                self.picam.stop()
                self.picam.close()
                self.picam = None

    def set_controls(self, controls):
        """Set camera controls

        Args:
            controls (dict): Camera control parameters
        """
        if self.is_running and self.picam:
            self.picam.set_controls(controls)

    def get_controls(self):
        """Get current camera controls"""
        if self.is_running and self.picam:
            return self.picam.capture_metadata()
        return None

    def show_fps(self, show=True, color=None, size=None, origin=None):
        """Configure FPS display

        Args:
            show (bool): Enable/disable FPS display
            color (tuple): RGB color for FPS text
            size (float): Font size for FPS text
            origin (tuple): Position for FPS text
        """
        self.draw_fps = show

        if color:
            self.fps_color = color
        if size:
            self.fps_size = size
        if origin:
            self.fps_origin = origin

    def take_photo(self, filename, path=None):
        """Take a photo and save it to disk

        Args:
            filename (str): Name for the saved photo (without extension)
            path (str): Directory to save the photo (created if doesn't exist)

        Returns:
            bool: Success or failure
        """
        if not self.is_running or self.current_frame is None:
            return False

        # Default path is user's home directory Pictures folder
        if path is None:
            user = os.popen("echo ${SUDO_USER:-$(who -m | awk '{ print $1 }')}").readline().strip()
            user_home = os.popen(f'getent passwd {user} | cut -d: -f 6').readline().strip()
            path = f'{user_home}/Pictures/roboeye'

        # Create directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path, mode=0o751, exist_ok=True)

        # Save photo
        full_path = f"{path}/{filename}.jpg"
        return cv2.imwrite(full_path, self.current_frame)