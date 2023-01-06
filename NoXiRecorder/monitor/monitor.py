import cv2
import os
import numpy as np
import argparse
import time
import socket
from rich import print
import pyaudio
import json
import threading


class VideoAudioSend:
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


class AudioMonitor:
    def __init__(self, client, channels, sample_rate, frames_per_buffer, bufsize):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            output=True,
            frames_per_buffer=frames_per_buffer,
        )
        self.client = client
        self.bufsize = bufsize

    def monitor(self):
        while True:
            data = self.client.recv(self.bufsize)
            self.stream.write(data)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def start(self):
        thread = threading.Thread(target=self.monitor)
        thread.start()


class VideoMonitor:
    def __init__(self, client, frame_size, bufsize):
        cv2.namedWindow("screen", cv2.WINDOW_NORMAL)
        self.client = client
        self.buf = b""
        self.img = None
        self.frame_size = frame_size
        self.bufsize = bufsize

    def monitor(self):
        while True:
            data = self.client.recv(self.bufsize)
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
        self.monitor()
