import cv2
import os
import numpy as np
import argparse
import time
import socket
from rich import print
import pyaudio
import json
from NoXiRecorder.utils.getDeviceID import get_audio_id, get_camera_id
from NoXiRecorder.monitor.monitor import VideoSend


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--common_setting_path", default="NoXiRecorder/setting/common_setting.json"
    )
    parser.add_argument(
        "--monitor_setting_path", default="NoXiRecorder/setting/monitor_setting.json"
    )
    parser.add_argument(
        "--network_setting_path", default="NoXiRecorder/setting/network_setting.json"
    )
    args = parser.parse_args()

    # init
    with open(args.common_setting_path) as f:
        setting = json.load(f)
        user = setting["user"]

    with open(args.monitor_setting_path) as f:
        setting = json.load(f)
        video_device = setting["video"]["device"]
        video_id = setting["video"]["id"]
        fps = setting["video"]["fps"]
        frame_size = setting["video"]["frame_size"]

    with open(args.network_setting_path) as f:
        setting = json.load(f)
        IP_VIDEO = setting["monitor"][user]["video"]["ip"]
        PORT_VIDEO = setting["monitor"][user]["video"]["port"]

    # Server startup and standby
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # Address already in use error avoidance
    print(f"IP: {IP_VIDEO}")
    print(f"PORT: {PORT_VIDEO}")
    server.bind((IP_VIDEO, PORT_VIDEO))  # Server start-up
    print("[bold magenta]waiting for a connection request...[/bold magenta]")
    server.listen()  # Waiting for client request
    client, _ = server.accept()
    print(f"[white]{client}[/white]")

    if os.name == "nt":  # Windows
        video_device_id = video_id
    else:
        video_device_id = get_camera_id(video_device)

    if video_device_id == None:
        video_device_id = video_id
        print(f"ERROR: Device not found ({video_device})")

    print("------------------------------------")
    print("Monitor Start...")
    send = VideoSend(
        video_device=video_device_id,
        fps=fps,
        frame_size=frame_size,
        client=client,
    )
    send.start()
    send.stop()
    print("Monitor End...")
    print("------------------------------------")
