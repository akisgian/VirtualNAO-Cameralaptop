import cv2
import time
from naoqi import ALProxy
import numpy as np

# NAOqi connection details (replace with your robot's IP and port)
NAO_IP = "akis.local"
NAO_PORT = 50396  # Or your ALBroker port

# Camera settings
CAMERA_INDEX = 0  # 0 for top camera, 1 for bottom camera
FRAME_RATE = 10  # Frames per second to send
WIDTH = 320      # Choose a supported width (1280, 640, 320, 160)
HEIGHT = 240     # Choose a supported height (960, 480, 240, 120)
SAVE_PATH = "/home/nao/recordings/cameras/video_feed1.avi"

class NaoVideoHandler:
    """Handles video capture, sending to NAOqi, and saving to file."""

    def __init__(self, nao_ip, nao_port, camera_index, frame_rate, width, height, save_path):
        self.nao_ip = nao_ip
        self.nao_port = nao_port
        self.camera_index = camera_index
        self.frame_rate = frame_rate
        self.width = width
        self.height = height
        self.save_path = save_path
        self.video_device = None
        self.camera = None
        self.video_writer = None

    def connect_to_nao(self):
        """Connects to the NAOqi ALVideoDevice."""
        try:
            self.video_device = ALProxy("ALVideoDevice", self.nao_ip, self.nao_port)
            print("Connected to NAOqi ALVideoDevice")
            return True
        except Exception as e:
            print("Error connecting to NAOqi ALVideoDevice:")
            return False

    def open_camera(self):
        """Opens the specified camera."""
        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            print("Error opening camera")
            return False
        return True

    def open_video_writer(self):
        """Opens the video writer for saving the video."""
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for video
        self.video_writer = cv2.VideoWriter(self.save_path, fourcc, self.frame_rate, (self.width, self.height))
        if not self.video_writer.isOpened():
            print("Error opening video writer")
            return False
        return True

    def process_frame(self, frame):
        """Processes a single frame for sending to NAOqi and saving."""
        frame_resized = cv2.resize(frame, (self.width, self.height))
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        image_data = "".join([chr(c) for c in frame_rgb.flatten()])
        alvalue = image_data
        success = self.video_device.putImage(self.camera_index, self.width, self.height, alvalue)
        if not success:
            print("Error putting image to NAOqi.")
        self.video_writer.write(frame_resized)

    def run(self):
        """Main loop for capturing, processing, and sending video."""
        if not (self.connect_to_nao() and self.open_camera() and self.open_video_writer()):
            return

        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    break
                self.process_frame(frame)
                time.sleep(1.0 / self.frame_rate)  # Control frame rate

        except KeyboardInterrupt:
            print("Video handling stopped.")
        finally:
            if self.camera:
                self.camera.release()
            if self.video_writer:
                self.video_writer.release()

if __name__ == "__main__":
    handler = NaoVideoHandler(NAO_IP, NAO_PORT, CAMERA_INDEX, FRAME_RATE, WIDTH, HEIGHT, SAVE_PATH)
    handler.run()
