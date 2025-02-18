# -*- coding: utf-8 -*-
from typing import Any, Union, Dict

from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.parameters.exceptions import GetParameterError
from core_utils.environment import ParametersApp
from core_utils.utils import get_logger

__all__ = ["get_parameter"]

LAYER_NAME = "ssm"

LOGGER = get_logger(f"layer-{LAYER_NAME}")

PARAMETERS_APP = ParametersApp()
PARAMETERS_PREFIX = f"/{PARAMETERS_APP.environment}/{PARAMETERS_APP.app_name}"


def get_parameter(ssm_name, *,
                  default: Any = None, transform: bool = False, use_prefix: bool = True) -> Union[Dict[str, Any], str]:
    """
    Get a parameter from SSM service on aws.

    Parameters
    ----------
    use_prefix
    ssm_name : str
        The name of the parameter to get.
    default : str
        The default value to return if the parameter is not found.
    transform : bool
        If the parameter value is a json string you can pass this laike true and get the value like dict object.

    Returns
    -------
    str
        The value of the parameter.

    Raises
    ------
    ValueError
        If the parameter is not found and no default value is provided.

    Examples
    --------
    >>> from core_aws.ssm import get_parameter
    >>> get_parameter("/my/parameter")

    """
    extra_args = {"transform": "json"} if transform else {}
    ssm_name = f"{PARAMETERS_PREFIX}/{ssm_name}" if use_prefix else ssm_name
    try:
        value = parameters.get_parameter(ssm_name, **extra_args)
    except GetParameterError as e:
        if default:
            return default
        raise e
    except Exception as e:
        LOGGER.warning(e)
        raise e
    LOGGER.debug(f"Value for {ssm_name}: {value}")

    return value
