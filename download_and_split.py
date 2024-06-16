from spleeter.separator import Separator
import argparse
import re
import os
import subprocess
from pytube import YouTube

parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, nargs="+", help="file paths or youtube links")
parser.add_argument(
    "--wav",
    type=str,
    default="C:\\Users\\jgaom\\Downloads\\WAV",
    help="output directory for youtube downloads",
)
parser.add_argument(
    "--spleeter",
    type=str,
    default="C:\\Users\\jgaom\\Downloads\\Spleeter",
    help="output directory for spleeter stems",
)
parser.add_argument(
    "-s",
    "--split",
    action="store_true",
    default=False,
    help="whether to split the audio if it's a youtube link",
)

args = parser.parse_args()
sources = args.input

youtube_pattern = r"youtu.?be"

for source in sources:
    is_youtube = re.search(youtube_pattern, source)

    if is_youtube:
        yt = YouTube(source)
        # Get highest average bit rate stream
        audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
        source = audio_stream.download(output_path=args.wav)

        # Convert to WAV and then delete the original audio file
        output_path = os.path.join(
            args.wav, os.path.basename(source).split(".")[0] + ".wav"
        )
    else:
        # Convert normal file to wav
        output_path = os.path.join(os.path.basename(source).split(".")[0] + ".wav")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        source,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "44100",
        "-ac",
        "2",
        output_path,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL)
    os.remove(source)

    source = output_path

    if args.split:
        # Replace all the non alphanumeric characters with a compatible symbol
        # Add song title prefix to "vocals" and "accompaniment" file name automatically
        cmd = [
            "spleeter",
            "separate",
            "-p",
            "spleeter:2stems",
            "-o",
            args.spleeter,
            source,
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL)
