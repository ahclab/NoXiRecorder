import argparse
import json
import os

import numpy as np

from NoXiRecorder.utils.getDeviceID import get_camera_id

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2


class VideoShow:
    # Video class based on openCV
    def __init__(self, device: int = 0, fps: int = 30, frame_size=[1920, 1080]):
        self.open = True
        self.device_index = device
        self.fps = fps
        self.fourcc = "MJPG"
        self.frameSize = frame_size
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frameSize[0])
        self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frameSize[1])
        self.video_cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cv2.namedWindow("screen", cv2.WINDOW_NORMAL)

    # Video starts being captured
    def capture(self):
        h, w = 1080, 720
        # h, w = 720, 480
        output_frame_size_h, output_frame_size_w = h, int((h/self.frameSize[1])*self.frameSize[0])
        x, y = int((output_frame_size_w - w)/2), int((output_frame_size_h - h)/2)
        while self.open == True:
            ret, video_frame = self.video_cap.read()
            if ret == True:
                blank = np.zeros((output_frame_size_h, output_frame_size_w, 3), np.uint8)
                frame = video_frame[y: y + h, x: x + w]
                blank[y: y + h, x: x + w] = frame
                frame = cv2.flip(blank, 1)
                cv2.imshow("screen", frame)
                if cv2.waitKey(1) & 0xFF == ord("e"):
                    break
            else:
                break

    # Finishes the video capturing
    def stop(self):
        if self.open == True:
            self.open = False
            self.video_cap.release()
            cv2.destroyAllWindows()
        else:
            pass

    # Launches the video capturing function
    def start(self):
        self.capture()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--capture_setting_path", default="NoXiRecorder/setting/capture_setting.json"
    )
    args = parser.parse_args()

    # init
    with open(args.capture_setting_path) as f:
        setting = json.load(f)
        video_device = setting["capture"]["device"]
        device_id = setting["capture"]["id"]
        fps = setting["capture"]["fps"]
        frame_size = setting["capture"]["frame_size"]

    video_device_id = get_camera_id(video_device)

    if video_device_id == None:
        print(f"ERROR: Device not found ({video_device})")
        video_device_id = device_id
        # exit(1)

    print("------------------------------------")
    print("Capture Start...")
    print('If you want to end the capture, press the "e" key.')
    video_capture = VideoShow(device=video_device_id,
                              fps=fps, frame_size=frame_size)
    video_capture.start()
    video_capture.stop()
    print("Capture End...")
    print("------------------------------------")
