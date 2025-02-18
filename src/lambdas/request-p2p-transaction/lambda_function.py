from http import HTTPStatus

from core_api.responses import api_response
from core_decorators import requester_patch
from core_utils.utils import get_logger, get_body
from core_decorators.logs import lambda_logger

requester_patch()
LOGGER = get_logger()


@lambda_logger(logger=LOGGER)
def lambda_handler(event: dict, _):
    records = event.get("Records")
    if records is None:
        LOGGER.info("No records founded")
        return {
            "error": True,
            "message": "No records founded"
        }

    for record in records:
        body = get_body(record)
        LOGGER.info(body)
        LOGGER.info('Processing banking request')
    return api_response('Hello world', HTTPStatus.OK)