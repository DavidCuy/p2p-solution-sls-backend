from http import HTTPStatus

from core_api.responses import api_response
from core_decorators import requester_patch
from core_utils.utils import get_logger
from core_decorators.logs import lambda_logger

requester_patch()
LOGGER = get_logger()


@lambda_logger(logger=LOGGER)
def lambda_handler(event: dict, _):
    return api_response('Notification was sent', HTTPStatus.OK)