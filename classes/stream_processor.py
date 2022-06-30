import threading
from time import sleep
import picamera
import picamera.array
import cv2
import sys

from settings import Settings

class StreamProcessor(threading.Thread):
    def __init__(self, camera, agent):
        """Looks for camera frames using a stream and processes them.
        
        The StreamProcessor waits for the ImageCapture to fire events,
        which are caught in the 'run' function with 'self.event.wait'.
        On events, the processor will call fetch the latest frame array
        from the camera and send this to the 'ProcessImage' function.
        """
        super(StreamProcessor, self).__init__()
        
        self.stream = picamera.array.PiRGBArray(camera)
        self.event = threading.Event()
        self.agent = agent
        self.terminated = False 

    def run(self):
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream by ImageCapture
            if self.event.wait(1):
                try:
                    # Read the image and do some processing on it
                    self.stream.seek(0)
                    self.ProcessImage(self.stream.array)
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
            sleep(0.2)
        sys.exit()

    def ProcessImage(self, image):
        """Stores 'image' to 'agent.image'."""
        if self.agent.sleeping: return
        # The camera is upside down so the image needs to be flipped
        image = cv2.flip(image, -1)
        # Trim the image to make it faster to compute
        self.agent.image = image[
            int(Settings.IMAGE_HEIGHT * 0.35):
            int(Settings.IMAGE_HEIGHT * 0.7)
        ]
        print("SP   : saved an image")

    def terminate(self):
        self.terminated = True
