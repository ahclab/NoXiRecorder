import socket
import sys
import time
import numpy as np
import cv2
import pyaudio
import argparse
import json
import threading
import NoXiRecorder.utils.utils as utils

from NoXiRecorder.monitor.monitor import AudioMonitor


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--network_setting_path", default="NoXiRecorder/setting/network_setting.json"
    )
    parser.add_argument(
        "--monitor_setting_path", default="NoXiRecorder/setting/monitor_setting.json"
    )
    parser.add_argument("--monitor_user",
                        default="expert")
    args = parser.parse_args()

    # init
    with open(args.monitor_setting_path) as f:
        setting = json.load(f)
        sample_rate = setting["audio"]["sample_rate"]
        channels = setting["audio"]["channels"]
        frames_per_buffer = setting["audio"]["frames_per_buffer"]
    with open(args.network_setting_path) as f:
        setting = json.load(f)
        BUFSIZE = setting["monitor"]["bufsize"]
        client_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_audio.connect(
                (
                    setting["monitor"][args.monitor_user]["audio"]["ip"],
                    setting["monitor"][args.monitor_user]["audio"]["port"],
                )
            )
        except:
            print(f"Unable to connect ({args.monitor_user})")
            exit(1)

    thread_audio = AudioMonitor(
        client=client_audio,
        channels=channels,
        sample_rate=sample_rate,
        frames_per_buffer=frames_per_buffer,
        bufsize=BUFSIZE,
    )

    thread_audio.start()

    while utils.command != "e":
        utils.command = input(">>")
        time.sleep(0.03)

    thread_audio.stop()

    time.sleep(2)
    client_audio.close()
