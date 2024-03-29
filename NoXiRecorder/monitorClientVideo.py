import socket
import sys
import time
import numpy as np
import os
import pyaudio
import argparse
import json
import threading
import NoXiRecorder.utils.utils as utils

from NoXiRecorder.monitor.monitor import VideoMonitor

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--network_setting_path", default="NoXiRecorder/setting/network_setting.json"
    )
    parser.add_argument(
        "--monitor_setting_path", default="NoXiRecorder/setting/monitor_setting.json"
    )
    parser.add_argument("--monitor_user", default="expert")
    args = parser.parse_args()

    # init
    with open(args.monitor_setting_path) as f:
        setting = json.load(f)
        frame_size = setting["video"]["frame_size"]
    with open(args.network_setting_path) as f:
        setting = json.load(f)
        BUFSIZE = setting["monitor"]["bufsize"]
        client_video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        IP = setting["monitor"][args.monitor_user]["video_to_observer"]["ip"]
        PORT = setting["monitor"][args.monitor_user]["video_to_observer"]["port"]
        print(f"IP: {IP}")
        print(f"PORT: {PORT}")
        try:
            client_video.connect(
                (
                    IP,
                    PORT,
                )
            )
        except:
            print(f"Unable to connect ({args.monitor_user})")
            exit(1)

    thread_video = VideoMonitor(
        client=client_video,
        frame_size=frame_size,
        bufsize=BUFSIZE,
    )
    thread_video.start()

    time.sleep(2)
    thread_video.stop()
    client_video.close()
