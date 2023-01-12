import wave
import time
import os
import json
import numpy as np
import argparse
import datetime
import logging
from logging import StreamHandler, FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET
from rich.logging import RichHandler
from NoXiRecorder.utils.getDeviceID import get_audio_id, get_camera_id
from NoXiRecorder.utils.fileFormatting import cut_to_same_length
from NoXiRecorder.recorder.videoRecorder import VideoRecorder
from NoXiRecorder.recorder.audioRecorder import AudioRecorder
import NoXiRecorder.utils.utils as utils
from NoXiRecorder.utils.utils import file_manager

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2

# Displays information on recorded files


def results(logger, path_video, path_audio_main, path_audio_sub):
    logger.info(f"Recorded Video: {path_video}")
    cap = cv2.VideoCapture(path_video)
    logger.debug(f"width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    logger.debug(f"height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    logger.debug(f"fps: {cap.get(cv2.CAP_PROP_FPS)}")
    logger.debug(f"frame_count: {cap.get(cv2.CAP_PROP_FRAME_COUNT)}")
    logger.debug(
        f"length: {cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)} s"
    )
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC)).to_bytes(
        4, "little").decode("utf-8")
    logger.debug(f"fourcc: {fourcc}")
    cap.release()

    for path in [path_audio_main, path_audio_sub]:
        with wave.open(path, "rb") as wr:
            logger.info(f"Recorded Audio: {path}")
            ch = wr.getnchannels()
            width = wr.getsampwidth()
            fr = wr.getframerate()
            fn = wr.getnframes()
            logger.debug(f"channel: {ch}")
            logger.debug(f"sample size: {width}")
            logger.debug(f"fps: {fr}")
            logger.debug(f"frame_count: {fn}")
            logger.debug(f"length: {1.0 * fn / fr}")


def set_logger(path):
    # Stream Handler Settings
    rich_handler: RichHandler = RichHandler(rich_tracebacks=True)
    rich_handler.setLevel(INFO)
    rich_handler.setFormatter(Formatter("%(message)s"))

    # Stream File Settings
    file_handler = FileHandler(path)
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(
        Formatter(
            "%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s")
    )

    # Root Logger Settings
    logging.basicConfig(level=NOTSET, handlers=[rich_handler, file_handler])
    logger = logging.getLogger(__name__)
    return logger


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--num", default="01")
    parser.add_argument("--common_setting_path",
                        default="NoXiRecorder/setting/common_setting.json")
    parser.add_argument("--record_setting_path",
                        default="NoXiRecorder/setting/record_setting.json")
    args = parser.parse_args()

    # init
    with open(args.common_setting_path) as f:
        setting = json.load(f)
        user = setting["user"]

    with open(args.record_setting_path) as f:
        setting = json.load(f)

        location = setting["AVrecordeR"]["recording_location"]

        video_device = setting["AVrecordeR"]["video"]["device"]
        video_id = setting["AVrecordeR"]["video"]["id"]
        fps = setting["AVrecordeR"]["video"]["fps"]
        frame_size = setting["AVrecordeR"]["video"]["frame_size"]
        video_file_name = setting["AVrecordeR"]["video"]["file_name"]

        audio_device_main = setting["AVrecordeR"]["audio_main"]["device"]
        audio_id_main = setting["AVrecordeR"]["audio_main"]["id"]
        sample_rate_main = setting["AVrecordeR"]["audio_main"]["sample_rate"]
        channels_main = setting["AVrecordeR"]["audio_main"]["channels"]
        frames_per_buffer_main = setting["AVrecordeR"]["audio_main"][
            "frames_per_buffer"
        ]
        audio_file_name_main = setting["AVrecordeR"]["audio_main"]["file_name"]

        audio_device_sub = setting["AVrecordeR"]["audio_sub"]["device"]
        audio_id_sub = setting["AVrecordeR"]["audio_sub"]["id"]
        sample_rate_sub = setting["AVrecordeR"]["audio_sub"]["sample_rate"]
        channels_sub = setting["AVrecordeR"]["audio_sub"]["channels"]
        frames_per_buffer_sub = setting["AVrecordeR"]["audio_sub"]["frames_per_buffer"]
        audio_file_name_sub = setting["AVrecordeR"]["audio_sub"]["file_name"]

    # Determination of file name
    now = datetime.datetime.now()
    dirname = os.path.join(
        location, args.num + now.strftime("_%Y_%m_%d")
    )  # ex.) "Nara/01_2022_12_31"
    os.makedirs(dirname, exist_ok=True)  # make dir.

    if user == "expert":
        filename = args.num + "_expert"
    elif user == "novice":
        filename = args.num + "_novice"
    else:
        print(f'ERROR: The setting.json "user" must be "expert" or "novice"')
        exit(1)

    # ex.) "Nara/01_2022_12_31/01_expert"
    path = os.path.join(dirname, filename)
    # ex.) "Nara/01_2022_12_31/01_expert.raw.mp4"
    path_video = path + video_file_name
    path_audio_main = (
        path + audio_file_name_main
    )  # ex.) "Nara/01_2022_12_31/01_expert_close.raw.wav"
    path_audio_sub = (
        path + audio_file_name_sub
    )  # ex.) "Nara/01_2022_12_31/01_expert_kinect.raw.wav"
    path_log = path + ".log"  # ex.) "Nara/01_2022_12_31/01_expert.log"
    path_img = path + ".png"  # ex.) "Nara/01_2022_12_31/01_expert.png"

    file_manager(path_video)  # Delete when file already exists
    file_manager(path_audio_main)  # Delete when file already exists
    file_manager(path_audio_sub)  # Delete when file already exists
    file_manager(path_log)  # Delete when file already exists

    logger = set_logger(path_log)
    logger.info("Start logger")

    # Get device number
    logger.info("Get device number")
    video_device_id = get_camera_id(video_device)
    audio_device_id_main = get_audio_id(audio_device_main)
    audio_device_id_sub = get_audio_id(audio_device_sub)

    logger.info(f"Video Device: [{video_device_id}]{video_device}")
    logger.info(
        f"Audio Device (MAIN): [{audio_device_id_main}]{audio_device_main}")
    logger.info(
        f"Audio Device (SUB): [{audio_device_id_sub}]{audio_device_sub}")

    if video_device_id == None:
        video_device_id = video_id
        logger.error(f"ERROR: Device not found ({video_device})")
        # exit(1)
    if audio_device_id_main == None:
        audio_device_id_main = audio_id_main
        logger.error(f"ERROR: Device not found ({audio_device_main})")
        # exit(1)
    if audio_device_id_sub == None:
        audio_device_id_sub = audio_id_sub
        logger.error(f"ERROR: Device not found ({audio_device_sub})")
        # exit(1)
    logger.debug("Successfully obtained device number")

    # Device Verification
    cap = cv2.VideoCapture(video_device_id)
    ret, frame = cap.read()
    cv2.imwrite(path_img, frame)
    cap.release()
    cv2.destroyAllWindows()
    logger.debug(f"Saving Images: {path_img}")

    # Recording
    logger.info("AV Record Start...")
    audio_thread_main = AudioRecorder(
        path=path_audio_main,
        audio_index=audio_device_id_main,
        sample_rate=sample_rate_main,
        frames_per_buffer=frames_per_buffer_main,
        channels=channels_main,
    )  # audio kinect
    logger.debug("AudioRecorder (MAIN) is ready")
    audio_thread_sub = AudioRecorder(
        path=path_audio_sub,
        audio_index=audio_device_id_sub,
        sample_rate=sample_rate_sub,
        frames_per_buffer=frames_per_buffer_sub,
        channels=channels_sub,
    )  # audio mic
    logger.debug("AudioRecorder (SUB) is ready")
    video_thread = VideoRecorder(
        path=path_video,
        device=video_device_id,
        fps=fps,
        frame_size=frame_size,
    )  # video
    logger.debug("VideoRecorder is ready")
    audio_thread_main.start()
    audio_thread_sub.start()
    video_thread.start()
    logger.debug("Thread startup complete")
    logger.info('If you want to start the AV record, press the "s" key.')

    while utils.command != "s":
        utils.command = input(">>")
        time.sleep(0.01)

    logger.info('If you want to stop the AV record, press the "e" key.')

    while utils.command != "e":
        utils.command = input(">>")
        time.sleep(0.03)

    video_thread.stop()
    audio_thread_main.stop()
    audio_thread_sub.stop()
    logger.debug("Stopping Threads")
    logger.info("AV Record End...")

    # Results
    logger.info("Display of recording results")
    results(logger, path_video, path_audio_main, path_audio_sub)  # results
    logger.debug(f"Start time of video_thread: {video_thread.start_time}")
    logger.debug(f"Start time of video_thread: {video_thread.end_time}")
    logger.debug(
        f"Start time of audio_thread_mic: {audio_thread_main.start_time}")
    logger.debug(
        f"Start time of audio_thread_mic: {audio_thread_main.end_time}")
    logger.debug(
        f"Start time of audio_thread_kinect: {audio_thread_sub.start_time}")
    logger.debug(
        f"Start time of audio_thread_kinect: {audio_thread_sub.end_time}")

    # File Format
    logger.info("File Formatting...")
    cut_to_same_length(
        path_video=path_video,
        path_audio_main=path_audio_main,
        path_audio_sub=path_audio_sub,
        logger=logger,
    )  # Align and composite audio and video file lengths
    logger.info("End")
