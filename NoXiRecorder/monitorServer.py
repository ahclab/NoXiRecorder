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
from NoXiRecorder.monitor.monitor import VideoAudioSend


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--common_setting_path",
                        default="NoXiRecorder/setting/common_setting.json")
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

        audio_device = setting["audio"]["device"]
        audio_id = setting["audio"]["id"]
        sample_rate = setting["audio"]["sample_rate"]
        channels = setting["audio"]["channels"]
        frames_per_buffer = setting["audio"]["frames_per_buffer"]

    with open(args.network_setting_path) as f:
        setting = json.load(f)
        IP_VIDEO = setting["monitor"][user]["video"]["ip"]
        PORT_VIDEO = setting["monitor"][user]["video"]["port"]
        IP_AUDIO = setting["monitor"][user]["audio"]["ip"]
        PORT_AUDIO = setting["monitor"][user]["audio"]["port"]

    # Server startup and standby
    server_video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_video.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # Address already in use error avoidance
    server_audio.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # Address already in use error avoidance
    server_video.bind((IP_VIDEO, PORT_VIDEO))  # Server start-up
    server_audio.bind((IP_AUDIO, PORT_AUDIO))  # Server start-up
    print("[bold magenta]waiting for a connection request...[/bold magenta]")
    server_video.listen()  # Waiting for client request
    server_audio.listen()  # Waiting for client request
    client_video, _ = server_video.accept()
    client_audio, _ = server_audio.accept()
    print(f"[white]{client_video}[/white]")
    print(f"[white]{client_audio}[/white]")

    if os.name == "nt":  # Windows
        video_device_id = video_id
        audio_device_id = audio_id
    else:
        video_device_id = get_camera_id(video_device)
        audio_device_id = get_audio_id(audio_device)

    if video_device_id == None:
        video_device_id = video_id
        print(f"ERROR: Device not found ({video_device})")
    if audio_device_id == None:
        audio_device_id = audio_id
        print(f"ERROR: Device not found ({audio_device})")

    print("------------------------------------")
    print("Monitor Start...")
    send = VideoAudioSend(
        video_device=video_device_id,
        fps=fps,
        frame_size=frame_size,
        audio_device=audio_device_id,
        sample_rate=sample_rate,
        channels=channels,
        frames_per_buffer=frames_per_buffer,
        client_video=client_video,
        client_audio=client_audio,
    )
    send.start()
    while send.stream.is_active():
        time.sleep(0.1)
    send.stop()
    print("Monitor End...")
    print("------------------------------------")
