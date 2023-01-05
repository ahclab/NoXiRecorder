import cv2
import threading
import time
import os
import numpy as np
import ffmpeg
import datetime
from NoXiRecorder.utils.utils import file_manager, command

# Video record


class VideoRecorder:
    # Video class based on openCV
    def __init__(
        self, path="video.mp4", device: int = 0, fps: int = 30, frame_size=[1920, 1080]
    ):
        self.open = True
        self.device_index = device
        # fps should be the minimum constant rate at which the camera can
        self.fps = fps
        # video formats and sizes also depend and vary according to the camera used
        self.frameSize = frame_size
        self.video_path = path
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frameSize[0])
        self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frameSize[1])
        self.video_cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.process = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="bgr24",
                s="{}x{}".format(self.frameSize[0], self.frameSize[1]),
                use_wallclock_as_timestamps=1,
            )
            .output(self.video_path, vsync="vfr", r=self.fps, pix_fmt="yuv420p")
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )  # ndarray to mp4
        self.start_time = None
        self.end_time = None

    # Video starts being recorded
    def record(self):
        while True:
            if command == "s":  # start
                break
        self.start_time = datetime.datetime.now()
        while self.video_cap.isOpened():  # end
            if command == "e":
                self.end_time = datetime.datetime.now()
                break
            ret, video_frame = self.video_cap.read()  # read
            time.sleep(0.01)
            if ret == True:
                self.process.stdin.write(video_frame)  # write
                if os.name == "nt":  # Windows
                    cv2.imshow("screen", video_frame)
            else:
                break

    # Finishes the video recording therefore the thread too
    def stop(self):
        if self.open == True:
            self.open = False
            self.video_cap.release()
            cv2.destroyAllWindows()
            self.process.stdin.close()
            self.process.wait()
        else:
            pass

    # Launches the video recording function using a thread
    def start(self):
        video_thread = threading.Thread(target=self.record)
        video_thread.start()


if __name__ == "__main__":
    # Determination of file name
    now = datetime.datetime.now()
    dirname = os.path.join(
        "Nara", "test" + now.strftime("_%Y_%m_%d")
    )  # ex.) "Nara/01_2022_12_31"
    os.makedirs(dirname, exist_ok=True)  # make dir.
    path = os.path.join(dirname, "test.mp4")

    file_manager(path)

    video_device_id = 0

    print("------------------------------------")
    print("Video Record Start...")
    video_thread = VideoRecorder(
        path=path,
        device=video_device_id,
    )
    video_thread.start()
    print('If you want to start the AV record, press the "s" key.')
    while command != "s":
        command = input(">>")
        time.sleep(0.01)
    print('If you want to end the video record, press the "e" key.')
    while command != "e":
        command = input(">>")
        time.sleep(0.03)
    video_thread.stop()
    print("Video Record End...")
    print("------------------------------------")
