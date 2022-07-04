from .YetiBorg import YetiBorg
from .stream_processor import StreamProcessor
from .image_capture import ImageCapture
import numpy as np
import cv2
import picamera
import time

from settings import Settings

class BaseAgent():
    def __init__(self) -> None:
        """A base class for Yetiborg agents.
        
        It contains a YetiBorg object for controlling the wheels, a PiCamera
        object for attached camera, and StreamProcessor and ImageCapture
        objects to process the camera's frames."""
        self.yeti = YetiBorg()
        self.image = None

        print('BA   : setting up the camera')
        self.camera = picamera.PiCamera(
            resolution= (Settings.IMAGE_WIDTH, Settings.IMAGE_HEIGHT),
            framerate= Settings.FRAMERATE,
        )
        time.sleep(2)

        self.processor = StreamProcessor(self.camera, self)
        self.capture_thread = ImageCapture(self.camera, self.processor)

    def close_threads(self):
        """Closes the ImageCapture and StreamProcessor threads."""
        self.capture_thread.terminate()
        self.capture_thread.join()
        print("BA   : killed the capture thread")
        self.processor.terminate()
        self.processor.join()
        print("BA   : killed the processor thread")

    def show_image(self, image=None, use_secondary=False):
        """Shows the latest image."""
        if image is None:
            image = self.image
        window = 'secondary' if use_secondary else 'image'
        cv2.imshow(window, image)
