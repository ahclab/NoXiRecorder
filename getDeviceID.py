import subprocess
from typing import Optional
import json
import pyaudio

# Lists index and name of connected devices
def AV_info():
    print("----- Audio Device -----")
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        print(f"Index[{i}], Device: {pa.get_device_info_by_index(i)['name']}")

    print("----- Camera Device -----")
    r = subprocess.run(
        ["system_profiler", "SPCameraDataType", "-json"],
        capture_output=True,
        text=True,
    )
    d = json.loads(r.stdout)
    for i, camera in enumerate(d.get("SPCameraDataType", [])):
        print(f"Index[{i}], Device: {camera['_name']}")


# Returns the index number of the audio device of the argument 'name'
def get_audio_id(name: str) -> Optional[int]:
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        if name == pa.get_device_info_by_index(i)["name"]:
            return i
    return None


# Returns the index number of the camera device of the argument 'name'
def get_camera_id(name: str) -> Optional[int]:
    r = subprocess.run(
        ["system_profiler", "SPCameraDataType", "-json"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return None
    d = json.loads(r.stdout)
    for i, camera in enumerate(d.get("SPCameraDataType", [])):
        if name == camera["_name"]:
            return i
    return None


if __name__ == "__main__":
    AV_info()
    # num = get_camera_id("Logitech StreamCam")
    # print(num)
    # num = get_audio_id("Yamaha AG03MK2")
    # print(num)
