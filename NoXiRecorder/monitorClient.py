import socket
import sys
import time
import numpy as np
import cv2
import pyaudio
import argparse
import json
import threading
import utils


class AudioMonitor:
    def __init__(self, client, channels, sample_rate, frames_per_buffer):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            output=True,
            frames_per_buffer=frames_per_buffer,
        )
        self.client = client

    def monitor(self):
        while True:
            data = self.client.recv(BUFSIZE)
            self.stream.write(data)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def start(self):
        thread = threading.Thread(target=self.monitor)
        thread.start()


class VideoMonitor:
    def __init__(self, client, frame_size):
        cv2.namedWindow("screen", cv2.WINDOW_NORMAL)
        self.client = client
        self.buf = b""
        self.img = None
        self.frame_size = frame_size

    def monitor(self):
        while True:
            data = self.client.recv(BUFSIZE)
            if data == b"s":
                self.buf = b""
            if data == b"e":
                if len(self.buf[1:]) == self.frame_size[1] * self.frame_size[0] * 3:
                    self.img = np.reshape(
                        np.frombuffer(self.buf[1:], dtype=np.uint8),
                        (self.frame_size[1], self.frame_size[0], 3),
                    )
                    cv2.imshow("screen", self.img)
            self.buf += data
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def stop(self):
        cv2.destroyAllWindows()

    def start(self):
        # from threading import main_thread
        # thread = main_thread()
        # print(f"name={thread.name}, daemon={thread.daemon}, id={thread.ident}")

        thread = threading.Thread(target=self.monitor)
        thread.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--network_setting_path", default="setting/network_setting.json"
    )
    parser.add_argument(
        "--monitor_setting_path", default="setting/monitor_setting.json"
    )
    parser.add_argument("--common_setting_path",
                        default="setting/common_setting.json")
    args = parser.parse_args()

    # init
    with open(args.common_setting_path) as f:
        setting = json.load(f)
        user = setting["user"]
        user = "novice"
    with open(args.monitor_setting_path) as f:
        setting = json.load(f)
        sample_rate = setting["audio"]["sample_rate"]
        channels = setting["audio"]["channels"]
        frames_per_buffer = setting["audio"]["frames_per_buffer"]
        frame_size = setting["video"]["frame_size"]
    with open(args.network_setting_path) as f:
        setting = json.load(f)
        BUFSIZE = setting["monitor"]["bufsize"]
        client_video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_audio_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_audio_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if user == "observer":
            try:
                client_audio_1.connect(
                    (
                        setting["monitor"]["expert"]["audio"]["ip"],
                        setting["monitor"]["expert"]["audio"]["port"],
                    )
                )
                client_audio_2.connect(
                    (
                        setting["monitor"]["novice"]["audio"]["ip"],
                        setting["monitor"]["novice"]["audio"]["port"],
                    )
                )
            except:
                print(f"Unable to connect (expert)")
        elif user == "expert":
            try:
                client_audio_1.connect(
                    (
                        setting["monitor"]["novice"]["audio"]["ip"],
                        setting["monitor"]["novice"]["audio"]["port"],
                    )
                )
            except:
                print(f"Unable to connect (novice)")
        elif user == "novice":
            try:
                client_audio_1.connect(
                    (
                        setting["monitor"]["expert"]["audio"]["ip"],
                        setting["monitor"]["expert"]["audio"]["port"],
                    )
                )
            except:
                print(f"Unable to connect (expert)")

    if user == "observer":
        thread_audio_2 = AudioMonitor(
            client=client_audio_2,
            channels=channels,
            sample_rate=sample_rate,
            frames_per_buffer=frames_per_buffer,
        )
        thread_audio_2.start()

    thread_audio_1 = AudioMonitor(
        client=client_audio_1,
        channels=channels,
        sample_rate=sample_rate,
        frames_per_buffer=frames_per_buffer,
    )
    # thread_video = VideoMonitor(
    #     client=client_video,
    #     frame_size=frame_size,
    # )
    thread_audio_1.start()
    # thread_video.start()

    while utils.command != "e":
        utils.command = input(">>")
        time.sleep(0.03)

    thread_audio_1.stop()

    if user == "observer":
        thread_audio_2.stop()
        client_audio_2.close()
    # thread_video.stop()

    time.sleep(2)
    # client_video.close()
    client_audio_1.close()
