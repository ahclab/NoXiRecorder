import cv2
import os
import numpy as np
import argparse
import getDeviceID
import time
import socket
from rich import print
import pyaudio
import json


class Monitor:
    def __init__(
        self,
        video_device,
        fps,
        frame_size,
        audio_device,
        sample_rate,
        channels,
        frames_per_buffer,
        client_video,
        client_audio,
    ):
        self.open = True

        self.video_cap = cv2.VideoCapture(video_device)
        self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
        self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])
        self.video_cap.set(cv2.CAP_PROP_FPS, fps)

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=audio_device,
            frames_per_buffer=frames_per_buffer,
            stream_callback=self.callback,
        )

        self.client_video = client_video
        self.client_audio = client_audio

    def callback(self, in_data, frame_count, time_info, status):
        try:
            self.client_audio.send(in_data)  # send
            return (None, pyaudio.paContinue)
        except:
            return (None, pyaudio.paComplete)

    # Monitor starts being captured
    def monitor(self):
        self.stream.start_stream()

        while self.open == True:
            ret, video_frame = self.video_cap.read()
            if ret == True:
                video_frame_byte = (
                    video_frame.tobytes()
                )  # Convert from numpy matrix to byte data
                self.client_video.sendall(b"s")  # send
                n = 10
                packet_size = int(frame_size[0] * frame_size[1] * 3 / n)
                for i in range(n):
                    self.client_video.sendall(
                        video_frame_byte[i *
                                         packet_size: (i + 1) * packet_size]
                    )  # send
                self.client_video.sendall(b"e")  # send
                time.sleep(0.2)  # fps5
            else:
                break

    # Finishes the monitor
    def stop(self):
        if self.open == True:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            self.video_cap.release()
            cv2.destroyAllWindows()
        else:
            pass

    # Launches the monitor function
    def start(self):
        self.monitor()


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
        video_device_id = getDeviceID.get_camera_id(video_device)
        audio_device_id = getDeviceID.get_audio_id(audio_device)

    if video_device_id == None:
        video_device_id = video_id
        print(f"ERROR: Device not found ({video_device})")
    if audio_device_id == None:
        audio_device_id = audio_id
        print(f"ERROR: Device not found ({audio_device})")

    print("------------------------------------")
    print("Monitor Start...")
    monitor = Monitor(
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
    monitor.start()
    while monitor.stream.is_active():
        time.sleep(0.1)
    monitor.stop()
    print("Monitor End...")
    print("------------------------------------")
