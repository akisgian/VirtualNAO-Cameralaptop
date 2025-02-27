# -*- coding: utf-8 -*-

import cv2  # OpenCV for image processing
import numpy as np  # NumPy for array manipulation
from naoqi import ALProxy
import time

def send_image_to_nao(image_path, robot_ip, robot_port):
    """Sends an image to the NAO robot's display.

    Args:
        image_path: Path to the image file.
        robot_ip: IP address of the NAO robot.
        robot_port: Port of the NAOqi service.
    """

    try:
        # 1. Connect to ALVideoDevice
        video_device = ALProxy("ALVideoDevice", robot_ip, robot_port)

        # 2. Load and process the image
        img = cv2.imread(image_path)
        if img is None:
            print("Error: Could not open or find image:", image_path)
            return

        # Resize if necessary (NAO's display has limitations)
        desired_width = 320 # Example, adjust as needed. Try 640 or 1280 too.
        desired_height = 240 # Example, adjust as needed
        img = cv2.resize(img, (desired_width, desired_height))

        # Convert to the format NAO expects (YUV422 or RGB)
        # Check ALVideoDevice documentation for the correct color space.
        # This example uses RGB. You might need to experiment.
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # BGR to RGB
        # If the robot expects YUV422:
        # img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)

        # 3. Prepare the image data
        # ALImage format: [width, height, channels, colorSpace, timestamps, data]
        # Color space constants are in ALVideoDevice documentation.
        color_space = 0 # RGB. Check documentation for the correct value!
        # color_space = 13 # YUV422. If using YUV, change this!
        
        now = time.time()
        seconds = int(now)
        microseconds = int((now - seconds) * 1000000)
        timestamp = [seconds, microseconds]

        image_data = np.array(img_rgb).tostring() # Convert to string
        # If using YUV422:
        # image_data = np.array(img_yuv).tostring()

        al_image = [desired_width, desired_height, 3, color_space, timestamp[0], timestamp[1], image_data, 0] # 0 for camera ID

        # 4. Send the image to the robot (using putImage)
        # putImage2 is more general, but putImage is simpler for just displaying.
        result = video_device.putImage(0, desired_width, desired_height, image_data) # Use camera 0 (top camera)
        # result = video_device.putImage2(al_image) # Use putImage2


        if result:
            print("Image sent successfully!")
        else:
            print("Error sending image.")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    image_path = "C:\\Users\\akisg\\Downloads\\image.jpg"  # Replace with the actual path
    robot_ip = "akis.local"  # Replace with your robot's IP
    robot_port = 52002  # Default NAOqi port

    send_image_to_nao(image_path, robot_ip, robot_port)