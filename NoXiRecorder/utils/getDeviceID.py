import subprocess
from typing import Optional
import json
import pyaudio
import platform
import cv2

# Lists index and name of connected devices


def AV_info():
    print("----- Audio Device -----")
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        print(f"Index[{i}], Device: {pa.get_device_info_by_index(i)['name']}")

    print("----- Camera Device -----")
    if platform.system() == 'Darwin':  # Mac
        r = subprocess.run(
            ["system_profiler", "SPCameraDataType", "-json"],
            capture_output=True,
            text=True,
        )
        d = json.loads(r.stdout)
        for i, camera in enumerate(d.get("SPCameraDataType", [])):
            print(f"Index[{i}], Device: {camera['_name']}")
    else:
        device_list = get_device_list_for_windows()
        for i, device in enumerate(device_list):
            print(f"[{i}] device")

def get_device_list_for_windows():
    r_list = str(subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "avfoundation", "-i", "dummy"],
            capture_output=True,
            text=True,
        )).replace(r"\n", "\n").splitlines()

    device_list = []
    for line in r_list:
        if "(video)" in line:
            device_list.append(line)
    return device_list


# Returns the index number of the audio device of the argument 'name'
def get_audio_id(name: str) -> Optional[int]:
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        if name in pa.get_device_info_by_index(i)["name"]:
            return i
    return None


# Returns the index number of the camera device of the argument 'name'
# Works only on Mac OS
def get_camera_id(name: str) -> Optional[int]:
    if platform.system() == 'Darwin':  # Mac
        r = subprocess.run(
            ["system_profiler", "SPCameraDataType", "-json"],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            return None
        d = json.loads(r.stdout)
        for i, camera in enumerate(d.get("SPCameraDataType", [])):
            if name in camera["_name"]:
                return i
        return None

    elif platform.system() == 'Windows':
        device_list = get_device_list_for_windows()
        for i, device in enumerate(device_list):
            if name in device:
                return i
        return None
    
    else:
        return None



if __name__ == "__main__":
    AV_info()
    num = get_camera_id("Logitech StreamCam")
    print(num)
    num = get_audio_id("Yamaha AG03MK2")
    print(num)
