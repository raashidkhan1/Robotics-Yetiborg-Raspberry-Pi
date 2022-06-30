import threading
import time
import sys

class ImageCapture(threading.Thread):
    def __init__(self, camera, processor):
        """Fires new frame events to the StreamProcessor 'processor'."""
        super(ImageCapture, self).__init__()
        self.camera = camera
        self.processor = processor
        self.terminated = False

    def run(self):
        print('IC   : start the stream using the video port')
        self.camera.capture_sequence(self.TriggerStream(), format='bgr', use_video_port=True)
        print('IC   : terminating camera processing...')
        self.processor.terminated = True
        self.processor.join()
        print('IC   : processing terminated.')
        sys.exit()

    # Stream delegation loop
    def TriggerStream(self):
        while not self.terminated:
            if self.processor.event.is_set():
                print("IC   : waiting for event release")
            else:
                yield self.processor.stream
                self.processor.event.set()
            time.sleep(0.2)

    def terminate(self):
        self.terminated = True