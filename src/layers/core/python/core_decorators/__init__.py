import inspect
from typing import Dict, Any

import wrapt
from core_utils.utils import get_logger
from requests.exceptions import HTTPError

LOGGER = get_logger()


class SingletonPatchRequestMeta(type):
    _instances: Dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
            for e in inspect.getmembers(cls):
                if "__" in e[0]:
                    continue
                wrapt.wrap_function_wrapper("requests", "Session.request", getattr(cls, e[0]))
        return cls._instances[cls]


class PatcherRequests(metaclass=SingletonPatchRequestMeta):
    @classmethod
    def _save_on_db(cls, wrapped, _, args, kwargs):
        response = wrapped(*args, **kwargs)
        try:
            # Here logic to save in database
            ...
        except Exception as e:
            LOGGER.error(e)
            raise e
        return response

    @classmethod
    def _logger(cls, wrapped, _, args, kwargs):
        response = wrapped(*args, **kwargs)
        message = {"request": kwargs}
        message.update({"response": {
            "statusCode": response.status_code,
            "content": response.content
        }})
        try:
            response.raise_for_status()
        except HTTPError:
            LOGGER.exception(message)
        LOGGER.info(message)
        return response


def requester_patch():
    PatcherRequests()
