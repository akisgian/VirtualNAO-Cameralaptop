import cv2
import time
from naoqi import ALProxy
import numpy as np

# NAOqi connection details (replace with your robot's IP and port)
NAO_IP = "akis.local"
NAO_PORT = 51724  # Or your ALBroker port

# Camera settings
CAMERA_INDEX = 0  # 0 for top camera, 1 for bottom camera
FRAME_RATE = 10  # Frames per second to send
WIDTH = 320       # Choose a supported width (1280, 640, 320, 160)
HEIGHT = 240      # Choose a supported height (960, 480, 240, 120)

class NaoVideoSender(object):
    def __init__(self, nao_ip, nao_port):
        self.nao_ip = nao_ip
        self.nao_port = nao_port
        self.video_device = None
        self.camera = None

    def connect_to_nao(self):
        try:
            self.video_device = ALProxy("ALVideoDevice", self.nao_ip, self.nao_port)
            print("Connected to NAOqi ALVideoDevice")
        except Exception as e:
            print("Error connecting to NAOqi ALVideoDevice:", e)
            return False
        return True

    def open_camera(self):
        self.camera = cv2.VideoCapture(CAMERA_INDEX)
        if not self.camera.isOpened():
            print("Error opening camera")
            return False
        return True

    def send_video(self):
        if not self.connect_to_nao() or not self.open_camera():
            return

        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    break

                # Resize the frame to the supported dimensions
                frame_resized = cv2.resize(frame, (WIDTH, HEIGHT))

                # Convert the frame to RGB (Bitmap format as required by putImage)
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

                # Convert the RGB frame to an ALValue (which is just a string in this case)
                image_data = "".join([chr(c) for c in frame_rgb.flatten()])
                alvalue = image_data

                # Send the image to NAOqi
                success = self.video_device.putImage(CAMERA_INDEX, WIDTH, HEIGHT, alvalue)
                if not success:
                    print("Error putting image to NAOqi.")

                time.sleep(1.0 / FRAME_RATE)  # Control frame rate

        except KeyboardInterrupt:
            print("Video sending stopped.")
        finally:
            self.camera.release()

if __name__ == "__main__":
    sender = NaoVideoSender(NAO_IP, NAO_PORT)
    sender.send_video()