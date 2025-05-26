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
    pop = mixer.Sound("pop.wav")
    mixer.music.load("californication.mp3")
    mixer.music.play()
    pop.play()
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
        while True:

            if timer == 30:
                print("Taking a photo #", image_idx)
                camera.take_photo(f"stop_dataset_photo{image_idx}")
                pop.play()
                image_idx += 1
                timer = 0
                #px.set_cam_tilt_angle(0)

            if image_idx == 100:
                break

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