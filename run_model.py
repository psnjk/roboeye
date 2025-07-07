from picarx import Picarx
from camera import Camera
from display import Display
from pygame import time
from pygame import mixer
from robot_hat import PWM, Music, Buzzer, set_volume, enable_speaker, disable_speaker
import os
import numpy as np
import cv2
from ultralytics import YOLO

STEERING_MIN = -35
STEERING_MAX = 35




def detect_objects(model, frame):
    """
    Detect objects using YOLO model
    Returns: list of detections with coordinates and confidence
    """
    # Resize frame to model input size (416x416)
    resized_frame = cv2.resize(frame, (416, 416))
    
    # Run inference
    results = model(resized_frame, verbose=False, conf=0.7)
    
    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Get coordinates (in 416x416 space)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                
                # Map coordinates back to original 640x480 frame
                orig_x1 = int(x1 * 640 / 416)
                orig_y1 = int(y1 * 480 / 416)
                orig_x2 = int(x2 * 640 / 416)
                orig_y2 = int(y2 * 480 / 416)
                
                # Calculate center coordinates
                center_x = (orig_x1 + orig_x2) // 2
                center_y = (orig_y1 + orig_y2) // 2
                
                detections.append({
                    'bbox': (orig_x1, orig_y1, orig_x2, orig_y2),
                    'center': (center_x, center_y),
                    'confidence': confidence
                })
    
    return detections

def main():
    px = Picarx()
    clock = time.Clock()
    FPS = 30
    
    # Load YOLO model
    print("Loading YOLO model...")
    model = YOLO('yolov8n.pt')  # Your trained model file
    print("Model loaded successfully!")
    
    timer = 0

    try:
        # Initialize camera
        camera = Camera(
            size=(640, 480),
            vflip=True,
            hflip=True
        )

        print("Starting camera...")
        camera.start()
        camera.show_fps(True)
        camera.enable_detection_overlay(confidence=True)

        # Initialize display
        display = Display(camera)
        display.show(
            local=True,
            web=True,
            port=9000
        )

        px.set_cam_tilt_angle(0)
        px.set_cam_pan_angle(0)
        
        while True:
            if timer > 30:
                photo = camera.get_image()
                
                if photo is not None:
                    # Object detection
                    detections = detect_objects(model, photo)
                    camera_detections = []
                    # Print object coordinates if detected
                    if detections:
                        print(f"Objects detected: {len(detections)}")
                        for i, detection in enumerate(detections):
                            center_x, center_y = detection['center']
                            confidence = detection['confidence']
                            #camera_detections.append(detection['bbox'])
                            x1, y1, x2, y2 = detection['bbox']
                            camera_detections.append((x1, y1, x2, y2, detection['confidence']))



                            print(f"  Object {i+1}: Center=({center_x}, {center_y}), Confidence={confidence:.2f}")
                        camera.update_detections(camera_detections)
                timer = 0
                    
            else:
                timer += 1
            
            clock.tick(FPS)

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Cleaning up...")
        disable_speaker()
        display.close()
        camera.stop()

if __name__ == "__main__":
    main()