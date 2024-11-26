from pathlib import Path


class PathsObject:
    base: Path
    index: Path
    images: Path
    audios: Path
    css: Path
    js: Path
    fonts: Path

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(self.__dict__)
