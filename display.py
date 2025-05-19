"""
Display functionality for RoboEye library
"""

import os
import cv2
import threading
import time
from streaming import create_streaming_server, start_streaming_server
from utils import get_ip_addresses


class Display:
    """Display class for showing camera output"""

    def __init__(self, camera):
        """Initialize the display with a camera instance

        Args:
            camera: RoboEye Camera instance
        """
        self.camera = camera
        self.window_name = "RoboEye"

        # Display state
        self.local_display_enabled = False
        self.local_display_thread = None

        # Web streaming
        self.web_enabled = False
        self.web_server = None
        self.streaming_thread = None
        self.port = 9000

    def show_local(self, enable=True, window_name=None):
        """Enable or disable local display using OpenCV window

        Args:
            enable (bool): Whether to enable local display
            window_name (str): Name for the display window
        """
        if window_name:
            self.window_name = window_name

        # Check if display is available
        if enable and 'DISPLAY' not in os.environ:
            print("Local display failed: No display environment available")
            return False

        # Update state
        self.local_display_enabled = enable

        # Start display thread if needed
        if enable and (self.local_display_thread is None or not self.local_display_thread.is_alive()):
            self.local_display_thread = threading.Thread(target=self._local_display_loop, daemon=True)
            self.local_display_thread.start()
            print(f"Local display started: {self.window_name}")
        elif not enable:
            print("Local display disabled")

        return True

    def _local_display_loop(self):
        """Loop for showing frames in local window"""
        while self.local_display_enabled and self.camera.is_running:
            if self.camera.current_frame is not None:
                try:
                    cv2.imshow(self.window_name, self.camera.current_frame)
                    key = cv2.waitKey(1) & 0xFF

                    # Check if window was closed
                    if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                        self.local_display_enabled = False
                        break

                except Exception as e:
                    print(f"Display error: {e}")
                    self.local_display_enabled = False
                    break

            time.sleep(0.03)  # ~30fps

        # Cleanup
        cv2.destroyWindow(self.window_name)

    def show_web(self, enable=True, port=9000):
        """Enable or disable web streaming

        Args:
            enable (bool): Whether to enable web streaming
            port (int): Port to serve on
        """
        self.port = port

        if enable == self.web_enabled:
            return  # Already in desired state

        self.web_enabled = enable

        if enable:
            # Create web server if needed
            if self.web_server is None:
                self.web_server = create_streaming_server(self.camera)

            # Start streaming thread
            if self.streaming_thread is None or not self.streaming_thread.is_alive():
                self.streaming_thread = threading.Thread(
                    target=start_streaming_server,
                    args=(self.web_server, self.port),
                    daemon=True
                )
                self.streaming_thread.start()

                # Print access URLs
                wlan_ip, eth_ip = get_ip_addresses()
                print("\nWeb streaming enabled:")
                if wlan_ip:
                    print(f"  http://{wlan_ip}:{self.port}/")
                if eth_ip:
                    print(f"  http://{eth_ip}:{self.port}/")
                if not wlan_ip and not eth_ip:
                    print(f"  http://localhost:{self.port}/")
                print()
        else:
            print("Web streaming disabled")

        return True

    def show(self, local=True, web=True, port=9000):
        """Enable both local and web display

        Args:
            local (bool): Enable local display
            web (bool): Enable web streaming
            port (int): Port for web streaming
        """
        results = []

        if local:
            results.append(self.show_local(True))

        if web:
            results.append(self.show_web(True, port))

        return all(results)

    def close(self):
        """Close all displays"""
        # Disable local display
        self.local_display_enabled = False
        if self.local_display_thread and self.local_display_thread.is_alive():
            self.local_display_thread.join(timeout=1)

        # Cleanup OpenCV windows
        cv2.destroyAllWindows()

        # Disable web streaming
        self.web_enabled = False