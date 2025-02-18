# -*- coding: utf-8 -*-
import json
from typing import Dict, Any, List

__all__ = ["get_body", "get_status_code", "get_query_parameters", "get_path_parameters", "get_sqs_records"]

import uuid
from typing import Union


def get_body(event: dict) -> dict:
    """
    Get event body if lambda has proxy lambda integration in api_local gateway.
    Parameters
    ----------
    event : dict

    Returns
    -------
    dict
        dictionary with body information.

    Examples
    --------
    >>> from core_api.utils import get_body
    >>> get_body({"body": {"a": 1}})

    """
    if isinstance(event, str):
        event = json.loads(event)
    body = event.get("body")
    if isinstance(body, str):
        return json.loads(body)
    return body


def get_status_code(response):
    """
    Get a status code from the lambda response if you use the decorator LambdaResponseWebDefault.
    Parameters
    ----------
    response : dict
        lambda response in api format.

    Returns
    -------
    int
        Status code returned.

    Examples
    --------
    >>> from core_api.utils import get_status_code
    >>> get_status_code({"statusCode": 200})

    """
    status_code = response.get("statusCode")
    return status_code


def get_query_parameters(event: Union[str, dict]):
    """
    Get event query parameters if lambda has proxy lambda integration in api_local gateway.
    Parameters
    ----------
    event : dict

    Returns
    -------
    dict
        dictionary with query parameters if exists.

    Examples
    --------
    >>> from core_api.utils import get_query_parameters
    >>> get_query_parameters({"queryStringParameters": {"a": 1}})

    """
    if isinstance(event, str):
        events = json.loads(event)
        return events.get("queryStringParameters") or {}
    return event.get("queryStringParameters") or {}


def is_valid_uuid(value):
    """
    Validation uuid
    Args:
        value:

    Returns: bool

    """
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def get_path_parameters(event: Union[str, dict]):
    """
    Get event path parameters if lambda has proxy lambda integration in api_local gateway.
    Parameters
    ----------
    event : dict

    Returns
    -------
    dict
        dictionary with path parameters if exists.

    Examples
    --------
    >>> from core_api.utils import get_path_parameters
    >>> get_path_parameters({"pathParameters": {"a": 1}})

    """
    if isinstance(event, str):
        events = json.loads(event)
        return events.get("pathParameters") or {}
    return event.get("pathParameters") or {}


def get_sqs_records(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
        Take a event from lambda input and return only the data that will be used in the process.
        Parameters
        ----------
        event : Diccionario
        Returns
        -------
        str
            The value MessageId or SQS not executed.
        Examples
        --------
        >>> from core_api.utils import get_sqs_records
        >>> get_sqs_records({'Records': [{}]})
        """
    try:
        records = event['Records']
    except KeyError:
        raise ValueError('The event not contain the key "Records"')
    if not isinstance(records, list):
        raise TypeError(f"The records should be a list type object not a {type(records)}")
    return records
