from typing import Any


class Is:
    @staticmethod
    def url(url: Any):
        return str(url).startswith(("http://", "https://"))


is_ = Is()

__all__ = ["is_"]
