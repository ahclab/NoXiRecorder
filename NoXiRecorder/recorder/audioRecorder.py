import pyaudio
import wave
import os
import time
import argparse
import threading
import datetime
import NoXiRecorder.utils.utils as utils
from NoXiRecorder.utils.utils import file_manager, command

# Audio record


class AudioRecorder:

    # Audio class based on pyAudio and Wave
    def __init__(
        self,
        path="temp_audio.wav",
        audio_index=0,
        sample_rate=44100,
        frames_per_buffer=1024,
        channels=1,
    ):
        self.open = True
        self.rate = sample_rate
        self.frames_per_buffer = frames_per_buffer
        self.channels = channels
        self.format = pyaudio.paInt16
        self.audio_path = path
        self.audio = pyaudio.PyAudio()
        self.audio_index = audio_index
        self.audio_frames = []
        self.command = None
        self.start_time = None
        self.end_time = None
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            start=False,
            input_device_index=self.audio_index,
            frames_per_buffer=self.frames_per_buffer,
            stream_callback=self.callback,
        )

    def __del__(self):
        self.audio.terminate()

    def callback(self, in_data, frame_count, time_info, status_flags):
        self.audio_frames.append(in_data)
        if utils.command == "e":  # end
            self.end_time = datetime.datetime.now()
            return None, pyaudio.paComplete
        return None, pyaudio.paContinue

    # Audio starts being recorded
    def record(self):
        while True:
            if utils.command == "s":  # start
                break
        self.start_time = datetime.datetime.now()
        self.stream.start_stream()  # record

    # Finishes the audio recording therefore the thread too
    def stop(self):
        if self.open == True:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            waveFile = wave.open(self.audio_path, "wb")
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b"".join(self.audio_frames))
            waveFile.close()
        pass

    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()


if __name__ == "__main__":
    # Determination of file name
    now = datetime.datetime.now()
    dirname = os.path.join(
        "Nara", "test" + now.strftime("_%Y_%m_%d")
    )  # ex.) "Nara/01_2022_12_31"
    os.makedirs(dirname, exist_ok=True)  # make dir.
    path = os.path.join(dirname, "test.wav")

    file_manager(path)

    audio_device_id = 1

    print("------------------------------------")
    print("Audio Record Start...")
    audio_thread = AudioRecorder(
        path=path,
        audio_index=audio_device_id,
    )
    audio_thread.start()
    print('If you want to start the AV record, press the "s" key.')
    while utils.command != "s":
        utils.command = input(">>")
        time.sleep(0.01)
    print('If you want to stop the AV record, press the "e" key.')
    while utils.command != "e":
        utils.command = input(">>")
        time.sleep(0.03)
    audio_thread.stop()
    print("Audio Record End...")
    print("------------------------------------")
