"""
Flask streaming server for RoboEye library
"""

import cv2
import time
import logging
from flask import Flask, Response, render_template

# Suppress Flask debug messages
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def create_streaming_server(camera):
    """Create Flask app for streaming

    Args:
        camera: RoboEye Camera instance

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Video streaming home page"""
        return """
        <!DOCTYPE html>
        <html>
          <head>
            <title>RoboEye Camera Stream</title>
            <style>
              body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                text-align: center;
              }
              img { 
                max-width: 100%; 
                border: 1px solid #ddd; 
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
              }
              h1 { color: #333; }
            </style>
          </head>
          <body>
            <h1>RoboEye Camera Stream</h1>
            <img src="/video_feed" />
          </body>
        </html>
        """

    def generate_frames():
        """Generator function for video streaming"""
        while True:
            if camera.is_running and camera.current_frame is not None:
                # Encode frame to JPEG
                success, buffer = cv2.imencode('.jpg', camera.current_frame)
                if success:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            # Maintain reasonable frame rate
            time.sleep(0.03)  # ~30fps

    @app.route('/video_feed')
    def video_feed():
        """Video streaming route"""
        if camera.is_running:
            return Response(
                generate_frames(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        else:
            return Response(
                "<h1>Camera is not running</h1>",
                mimetype='text/html'
            )

    @app.route('/still.jpg')
    def still_image():
        """Single still image route"""
        if camera.is_running and camera.current_frame is not None:
            success, buffer = cv2.imencode('.jpg', camera.current_frame)
            if success:
                return Response(buffer.tobytes(), mimetype='image/jpeg')

        return Response("Camera not available", mimetype='text/plain')

    return app

def start_streaming_server(app, port=9000):
    """Start the Flask streaming server

    Args:
        app: Flask app instance
        port: Port to serve on
    """
    try:
        app.run(host='0.0.0.0', port=port, threaded=True, debug=False)
    except Exception as e:
        print(f"Streaming server error: {e}")