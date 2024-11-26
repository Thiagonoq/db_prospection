import logging
import time
from typing import Any

import requests


class Requests:
    def __init__(
        self, max_retries: int = 3, parser: str = "json", return_default: Any = None
    ):
        self.max_retries = max_retries
        self.parser = parser
        self.return_default = return_default

    def _retry(self, callback, url: str, **kwargs):
        retries = 0
        wait_time = 1

        kwargs["timeout"] = kwargs.get("timeout", 10)

        while retries < self.max_retries:
            try:
                response = callback(url, **kwargs)

                if response.status_code == 200:
                    if self.parser == "json":
                        response = response.json()

                        if response is None:
                            return self.return_default

                    if response is None:
                        return self.return_default

                    return response
                elif response.status_code == 404:
                    logging.error(f"Failed to request {url} with status code 404")
                    return None
                else:
                    raise Exception(
                        f"Failed to request {url} with status code {response.status_code}"
                    )
            except Exception as e:
                retries += 1
                logging.error(f"Failed to request {url} with error: {e}")
                logging.exception(e)
                time.sleep(wait_time)
                wait_time *= 2

        return None

    def get(self, url: str, **kwargs):
        return self._retry(requests.get, url, **kwargs)

    def post(self, url: str, **kwargs):
        return self._retry(requests.post, url, **kwargs)

    def put(self, url: str, **kwargs):
        return self._retry(requests.put, url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self._retry(requests.delete, url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self._retry(requests.patch, url, **kwargs)

    def head(self, url: str, **kwargs):
        return self._retry(requests.head, url, **kwargs)

    def options(self, url: str, **kwargs):
        return self._retry(requests.options, url, **kwargs)

    def request(self, method: str, url: str, **kwargs):
        return self._retry(requests.request, url, method=method, **kwargs)
