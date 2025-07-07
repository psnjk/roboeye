"""
Example usage of the RoboEye library
"""

# import time

from picarx import Picarx
from camera import Camera
from display import Display
from pygame import time
from pygame import mixer
from robot_hat import PWM, Music, Buzzer, set_volume, enable_speaker, disable_speaker
import os
import numpy as np


STEERING_MIN = -35
STEERING_MAX = 35




def update_steering(controller, left_sensor, right_sensor, dt):
    # Positive error = line more to the right (so we need to steer left)
    error = left_sensor - right_sensor

    correction = controller.compute(error, dt)

    # Clamp correction to steering limits
    steering_angle = max(min(correction, STEERING_MAX), STEERING_MIN)

    return steering_angle


class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.prev_error = 0
        self.integral = 0

    def compute(self, error, dt):
        self.integral += error * dt
        # Optional: Clamp the integral to avoid wind-up
        self.integral = max(min(self.integral, 100), -100)

        derivative = (error - self.prev_error) / dt if dt > 0 else 0

        output = (
            self.kp * error +
            self.ki * self.integral +
            self.kd * derivative
        )

        self.prev_error = error
        return output
pid = PIDController(kp=0.5, ki=0.1, kd=0)


def main():

    px = Picarx()
    enable_speaker()
    music = Music()
    # set_volume(80)
    # music.tempo(60, 1/4)
    # music.play_tone_for(music.note("G4"), music.beat(1/8))

    # music.play('C4')  # Play middle C note
    # time.sleep(0.2)   # Duration of the beep
    # music.stop()

    mixer.init()
    # pop = mixer.Sound("pop.wav")
    # mixer.music.load("californication.mp3")
    # mixer.music.play()
    # pop.play()
    clock = time.Clock()
    FPS = 10




    timer = 0

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

        image_idx = 0
        px.set_cam_tilt_angle(0)
        px.set_cam_pan_angle(0)
        photo = []
        px.set_cam_tilt_angle(-30)
        px.forward(50)
        while True:
            
            if timer > 10:
                camera.take_photo(f"stop_dataset_photo{image_idx}")
                photo = camera.get_image()
                row = photo[240]
                left = round(np.average(row[:len(row)//2]))
                right = round(np.average(row[len(row)//2:]))
                dt = 1/FPS
                steering = update_steering(pid, left, right, dt)
                px.set_dir_servo_angle(steering)
                print(steering)
                pass
                
            else:
                timer += 1
                    

            
            
            clock.tick(FPS)

        print("Cleaning up...")
        disable_speaker()
        display.close()
        camera.stop()

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ensure cleanup
        camera.stop()
        disable_speaker()


if __name__ == "__main__":
    main()
