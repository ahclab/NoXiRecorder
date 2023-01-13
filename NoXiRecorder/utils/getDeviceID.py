import subprocess
from typing import Optional
import json
import pyaudio
import platform
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import time
import re

OUTPUT_DIR =  "NoXiRecorder/utils/video_device_img"

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
    elif platform.system() == 'Windows': # Windows:
        device_list = get_device_list_for_windows()
        print(device_list)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
        for i in range(0, 20): 
            cap = cv2.VideoCapture(i)
            if cap.isOpened(): 
                ret, frame = cap.read()
                cv2.imwrite(os.path.join(OUTPUT_DIR, f"{i}.png"), frame)
            else:
                pass
            cap.release()
            cv2.destroyAllWindows()
        video_devce_dict = {}
        for device_name in device_list:
            device_name = "".join(device_name)
            device_id = input(f"Device Name [{device_name}]: Device ID >>")
            video_devce_dict[str(device_name)] = device_id
        print(video_devce_dict)
        with open('NoXiRecorder/setting/video_device.json', 'w') as f:
            json.dump(video_devce_dict, f, indent=1)
    else:
        pass

def get_device_list_for_windows():
    r = str(subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "nul"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        ))
    r_list = r.replace(r"\n", "\n").splitlines()

    device_name_list = []
    for line in r_list:
        if "(video)" in line:
            device_name_list.append(re.findall(r'\"(.*)\"', line))
    return device_name_list


# Returns the index number of the audio device of the argument 'name'
def get_audio_id(name: str) -> Optional[int]:
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        if name in pa.get_device_info_by_index(i)["name"]:
            return i
    return None


# Returns the index number of the camera device of the argument 'name'
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

    elif platform.system() == 'Windows': # Windows
        with open("NoXiRecorder/setting/video_device.json") as f:
            device_dict = json.load(f)
        for i, device in device_dict.items():
            if name in device:
                return i
        return None
    
    else:
        return None



if __name__ == "__main__":
    AV_info()
    # num = get_camera_id("Logitech StreamCam")
    # print(num)
    # num = get_audio_id("Yamaha AG03MK2")
    # print(num)
