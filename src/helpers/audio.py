from pathlib import Path

from moviepy import AudioFileClip as a_clip
from pydub import AudioSegment
from pydub.effects import normalize as pydub_normalize


def is_valid(path: Path):
    try:
        a_clip(path.resolve().as_posix())
        return True
    except Exception:
        return False


def normalize(path: Path):
    audio_path = path.resolve().as_posix()
    audio = AudioSegment.from_file(audio_path)

    normalized_audio = pydub_normalize(audio)

    if normalized_audio.max_dBFS > 0:
        normalized_audio = normalized_audio - normalized_audio.max_dBFS

    normalized_audio.export(audio_path, format="mp3")

    return path
