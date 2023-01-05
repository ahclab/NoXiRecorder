import subprocess
import os
import wave
import ffmpeg
import logging
from logging import StreamHandler, FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET
from rich.logging import RichHandler


# Get file length
def get_file_length(path):
    _, ext = os.path.splitext(path)
    if ext == ".mp4":
        length = ffmpeg.probe(path)["format"]["duration"]
        return float(length)
    elif ext == ".wav":
        with wave.open(path, "rb") as wr:
            fr = wr.getframerate()
            fn = wr.getnframes()
            length = 1.0 * fn / fr
            return float(length)
    else:
        return None


def cut_to_same_length(path_video, path_audio_main, path_audio_sub, logger=None):
    if logger == None:
        rich_handler: RichHandler = RichHandler(rich_tracebacks=True)
        rich_handler.setLevel(INFO)
        rich_handler.setFormatter(Formatter("%(message)s"))

        logging.basicConfig(level=NOTSET, handlers=[rich_handler])
        logger = logging.getLogger(__name__)

    video_length = get_file_length(path_video)
    audio_main_length = get_file_length(path_audio_main)
    audio_sub_length = get_file_length(path_audio_sub)

    path_list = [path_video, path_audio_sub, path_audio_main]
    length_list = [video_length, audio_main_length, audio_sub_length]

    for path, length in zip(path_list, length_list):
        logger.debug(f"raw file length: [{path}] [{length}]")
        if length == None:
            logger.error(f"Error: {path} is not correct")
            exit(1)

    min_length = min(length_list)
    for path, length in zip(path_list, length_list):
        duration = length - min_length  # Time gap between audio and video files
        cmd = f"ffmpeg -y -ss {duration} -i {path} -c copy {path.replace('.raw', '')}"  # All formatted to the same file length
        logger.debug(cmd)
        subprocess.call(cmd.split())

    cmd = f"ffmpeg -ac 2 -y -channel_layout stereo -i {path_audio_main.replace('.raw', '')} -i {path_video.replace('.raw', '')} -pix_fmt yuv420p {path_video.replace('.raw', '.withAudio')}"  # Composite audio and video
    logger.debug(cmd)
    subprocess.call(cmd.split())
    cmd = f"ffmpeg -ac 2 -y -channel_layout stereo -i {path_audio_main.replace('.raw', '')} -i {path_video.replace('.raw', '')} -vf scale=320:-1 -pix_fmt yuv420p {path_video.replace('.raw', '.withAudio_low')}"  # Composite audio and video in low quality
    logger.debug(cmd)
    subprocess.call(cmd.split())

    for path in path_list:
        length = get_file_length(path.replace(".raw", ""))
        logger.debug(f"formatted file length: [{path.replace('.raw', '')}] [{length}]")


if __name__ == "__main__":
    cut_to_same_length(
        path_video="Nara/01_2022_12_30/01_expert.raw.mp4",
        path_audio_main="Nara/01_2022_12_30/01_expert_main.raw.wav",
        path_audio_sub="Nara/01_2022_12_30/01_expert_sub.raw.wav",
    )
