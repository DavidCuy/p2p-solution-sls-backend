from typing import Any

from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.parameters import GetParameterError
from db_utils.app_params import ParametersApp
from db_utils.logger import get_logger

LAYER_NAME = "secret_manager"

LOGGER = get_logger(f"layer-{LAYER_NAME}")

PARAMETERS_APP = ParametersApp()
SECRETS_PREFIX = f"{PARAMETERS_APP.environment}-{PARAMETERS_APP.app_name}"
GLOBAL_SECRETS_PREFIX = f"{PARAMETERS_APP.environment}-{PARAMETERS_APP.app_name}"


def get_secret(secret_name: str, transform: bool = False, default: Any = None, use_prefix: bool = True,
               is_global=False):
    extra_args = {"transform": "json"} if transform else {}
    prefix = GLOBAL_SECRETS_PREFIX if is_global else SECRETS_PREFIX
    secret_name = f"{prefix}-{secret_name}" if use_prefix else secret_name
    try:
        value = parameters.get_secret(secret_name, **extra_args)
    except GetParameterError as e:
        if default:
            return default
        raise e
    except Exception as e:
        LOGGER.warning(e)
        raise e
    return value
