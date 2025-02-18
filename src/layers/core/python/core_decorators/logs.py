from functools import partial, wraps
from logging import Logger
from typing import Any, Callable, Dict


def lambda_logger(function: Callable[[Dict, Any], Any] = None, logger: Logger = None):
    if not logger:
        raise AttributeError("logger is required")
    if function is None:
        return partial(lambda_logger, logger=logger)

    @wraps(function)
    def decorator(event, context):
        try:
            logger.info({"Event": event})
        except Exception as e:
            logger.debug(str(e))
        try:
            response = function(event, context)
        except Exception as e:
            logger.error(e)
            raise e
        logger.info({"Response": response})
        return response

    return decorator
