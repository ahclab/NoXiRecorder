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
        "--common_setting_path", default="NoXiRecorder/setting/common_setting.json"
    )
    parser.add_argument(
        "--network_setting_path", default="NoXiRecorder/setting/network_setting.json"
    )
    parser.add_argument(
        "--monitor_setting_path", default="NoXiRecorder/setting/monitor_setting.json"
    )
    parser.add_argument("--monitor_user", default="expert")
    args = parser.parse_args()

    # init
    with open(args.common_setting_path) as f:
        setting = json.load(f)
        user = setting["user"]
    with open(args.monitor_setting_path) as f:
        setting = json.load(f)
        sample_rate = setting["audio"]["sample_rate"]
        channels = setting["audio"]["channels"]
        frames_per_buffer = setting["audio"]["frames_per_buffer"]
    with open(args.network_setting_path) as f:
        setting = json.load(f)
        BUFSIZE = setting["monitor"]["bufsize"]
        client_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if user == "observer":
            IP = setting["monitor"][args.monitor_user]["audio_to_observer"]["ip"]
            PORT = setting["monitor"][args.monitor_user]["audio_to_observer"]["port"]
        elif user == "expert" && args.monitor_user == "novice":
            IP = setting["monitor"][args.monitor_user]["audio_to_expert"]["ip"]
            PORT = setting["monitor"][args.monitor_user]["audio_to_expert"]["port"]
        elif user == "novice" && args.monitor_user == "expert":
            IP = setting["monitor"][args.monitor_user]["audio_to_novice"]["ip"]
            PORT = setting["monitor"][args.monitor_user]["audio_to_novice"]["port"]
        else:
            print(f"Error: Inconsistency between --monitor_user {args.monitor_user} and user {user}")
            exit(1)
            
        print(f"IP: {IP}")
        print(f"PORT: {PORT}")
        try:
            client_audio.connect(
                (
                    IP,
                    PORT,
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

    while thread_audio.stream.is_active():
        utils.command = input(">>")
        if utils.command == "e":
            break
        time.sleep(0.1)

    time.sleep(1)
    thread_audio.stop()
    client_audio.close()
