import os
import numpy as np
import argparse
import time
import socket
from rich import print
import json
from NoXiRecorder.utils.getDeviceID import get_audio_id, get_camera_id
import NoXiRecorder.utils.utils as utils
from NoXiRecorder.monitor.monitor import AudioSend


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
    parser.add_argument(
        "--to_user", default="observer"
    )
    args = parser.parse_args()

    # init
    with open(args.common_setting_path) as f:
        setting = json.load(f)
        user = setting["user"]

    with open(args.monitor_setting_path) as f:
        setting = json.load(f)

        audio_device = setting["audio"]["device"]
        audio_id = setting["audio"]["id"]
        sample_rate = setting["audio"]["sample_rate"]
        channels = setting["audio"]["channels"]
        frames_per_buffer = setting["audio"]["frames_per_buffer"]

    with open(args.network_setting_path) as f:
        setting = json.load(f)
        if args.to_user == "observer":
            IP_AUDIO = setting["monitor"][user]["audio_to_observer"]["ip"]
            PORT_AUDIO = setting["monitor"][user]["audio_to_observer"]["port"]
        elif (user == "novice") & (args.to_user == "expert"):
            IP_AUDIO = setting["monitor"][user]["audio_to_expert"]["ip"]
            PORT_AUDIO = setting["monitor"][user]["audio_to_expert"]["port"]
        elif (user == "expert") & (args.to_user == "novice"):
            IP_AUDIO = setting["monitor"][user]["audio_to_novice"]["ip"]
            PORT_AUDIO = setting["monitor"][user]["audio_to_novice"]["port"]
        else:
            print(f"Error: Inconsistency between --to_user {args.to_user} and user {user}")
            exit(1)

    # Server startup and standby
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # Address already in use error avoidance
    print(f"IP: {IP_AUDIO}")
    print(f"PORT: {PORT_AUDIO}")
    server.bind((IP_AUDIO, PORT_AUDIO))  # Server start-up
    print("[bold magenta]waiting for a connection request...[/bold magenta]")
    try:
        server.listen()  # Waiting for client request
    except:
        exit(1)
    client, _ = server.accept()
    print(f"[white]{client}[/white]")

    audio_device_id = get_audio_id(audio_device)

    if audio_device_id == None:
        audio_device_id = audio_id
        print(f"ERROR: Device not found ({audio_device})")
    
    print(
        f"Audio Device: [{audio_device_id}]{audio_device}")

    print("------------------------------------")
    print("Monitor Start...")
    send = AudioSend(
        audio_device=audio_device_id,
        sample_rate=sample_rate,
        channels=channels,
        frames_per_buffer=frames_per_buffer,
        client=client,
    )
    send.start()
    while send.stream.is_active():
        time.sleep(0.1)

    send.stop()
    print("Monitor End...")
    print("------------------------------------")
