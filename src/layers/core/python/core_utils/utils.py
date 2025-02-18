# -*- coding: utf-8 -*-
"""
Helper functions for working with Python.
"""

import calendar
import hashlib
import datetime
import json
import random
import tempfile
from decimal import Decimal
from typing import Any, Union
from uuid import UUID

import core_utils.environment
import pytz
import requests

from aws_lambda_powertools import Logger
from core_api.utils import (
    get_body,
    get_status_code,
)
from dataclasses import dataclass

__all__ = [
    "get_logger",
    "get_mty_datetime",
    "cast_default",
    "cast_date",
    "cast_number",
    "compare_iterables",
    "dict_strip_nulls",
    "dict_keys_to_lower",
    "sort_dict_by_keys",
    "get_uniques_in_lists",
    "get_split_names",
    "cast_python_default",
    "bytes_to",
    "chunks",
    "get_timezone_datetime",
    "get_date_by_timezone",
    "get_validation_response",
    "validate_date_format",
    "generate_otp",
    "DecimalEncoder",
    "get_header",
    "get_body",
    "calculate_hash",
    "get_national_msisdn",
    "get_message_to_log",
    "divide_chunks",
    "download_file",
    "get_uddm_range_date",
    "get_range_date_by_change_month",
    "get_range_date_by_change_fortnight",
    "get_daily_penalty_rate",
    "get_penalties_by_installment",
    "calculate_iva", "calculate_administrative_expense", "calculate_interest", "calculate_last_date",
    "calculate_bullet", "calculate_installment", "validate_expire_date"
]

PARAMETERS_APP = core_utils.environment.ParametersApp()
FORMAT = '%Y-%m-%d %H:%M:%S'

@dataclass
class RoundOptions:
    precision: int
    round_dtype: callable
    round_method: str
    round_mask: str

def get_logger(name=None):
    """
    Returns a logger object.

    Parameters
    ----------
    name : str

    Returns
    -------
    logger : Logger

    Examples
    --------
    >>> from core_utils.utils import get_logger
    >>> logger = get_logger("my_logger")

    """
    properties: dict[str, Any] = dict(
        log_record_order=["level", "message"],
        sampling_rate=None,
    )
    if name:
        properties.setdefault("service", name)
    return Logger(**properties)


def get_mty_datetime():
    """
    Returns a datetime object with the current time in Mexico City "America/Monterrey" timezone

    Returns
    -------
    datetime.datetime object with the current time in Mexico City "America/Monterrey" timezone.

    Examples
    --------
    >>> from core_utils.utils import get_mty_datetime
    >>> mty_datetime = get_mty_datetime()

    """
    mty = pytz.timezone("America/Monterrey")
    return datetime.datetime.now(tz=mty)


def cast_default(o):
    """
    Cast data to default data for json serialization.

    Parameters
    ----------
    o : Any

    Returns
    -------
    Any object with the default data type for json serialization.

    Examples
    --------
    >>> from core_utils.utils import cast_default
    >>> cast_default(Decimal(1.1))

    """
    if isinstance(o, Decimal):
        o = cast_number(o)
    elif isinstance(o, UUID):
        o = str(o)
    else:
        o = cast_date(o)
    return o


def cast_date(element: Union[datetime.date, datetime.time]):
    """
    Cast a datetime.date or datetime.time object to iso-format string.

    Parameters
    ----------
    element: datetime.date or datetime.time object

    Returns
    -------
    str: iso-format string

    Examples
    --------
    >>> from core_utils.utils import cast_date
    >>> cast_date(datetime.date(2020, 1, 1))

    """
    if isinstance(element, (datetime.date, datetime.time)):
        element_ = element.isoformat()
        return element_


def cast_number(number: Union[str, Decimal]) -> Union[int, float]:
    """
    Cast a string or Decimal object to int or float.

    Parameters
    ----------
    number : str or Decimal

    Returns
    -------
    int or float

    Examples
    --------
    >>> from core_utils.utils import cast_number
    >>> cast_number(Decimal(1.1))

    """
    if isinstance(number, str):
        if number.isnumeric():
            return int(number)
        else:
            try:
                return float(number)
            except ValueError:
                try:
                    return float(number.replace(",", ""))
                except ValueError:
                    raise ValueError("The value not is int o float")
    elif isinstance(number, Decimal):
        return cast_number(str(number))
    elif isinstance(number, (float, int)):
        return number


def compare_iterables(keys, this):
    """
    Compare two iterables.
    Check that all the elements of the (list, tuple or dict) passed as keys exist in
    the (list, tuple or dict) passed as "this"

    Parameters
    ----------
    keys : list, tuple or dict
    this : list, tuple or dict

    Returns
    -------
    bool: True if all the elements of the (list, tuple or dict) passed as keys exist in
    the (list, tuple or dict) passed as "this"

    Examples
    --------
    >>> from core_utils.utils import compare_iterables
    >>> compare_iterables(["a", "b"], ["a", "b", "c"])
    """
    return (
        all([key in this for key in keys])
        if isinstance(keys, (list, dict)) and isinstance(this, (list, dict))
        else False
    )


def dict_strip_nulls(d):
    """
    Remove null values from a dictionary.

    Parameters
    ----------
    d : dict

    Returns
    -------
    dict: dict without null values

    Examples
    --------
    >>> from core_utils.utils import dict_strip_nulls
    >>> dict_strip_nulls({"a": 1, "b": None})

    """
    return {k: v for k, v in d.items() if v is not None} if type(d) == dict else None


def dict_keys_to_lower(d):
    """
    Convert all keys of a dictionary to lowercase.

    Parameters
    ----------
    d : dict

    Returns
    -------
    dict: dict with all keys in lowercase

    Examples
    --------
    >>> from core_utils.utils import dict_keys_to_lower
    >>> dict_keys_to_lower({"a": 1, "B": 2})

    """
    return {k.lower(): v for k, v in d.items()} if type(d) == dict else None


def bytes_to(bytes_, to=0, bsize=1024):
    """
    Convert bytes to MB, GB, TB, or PB.

    Parameters
    ----------
    bytes_  : int
        A number representing the size of a file in bytes
    to     : int
        index of the metric you want to use:
            1: 'Kb',
            2: 'Mb',
            3: 'Gb',
            4: 'Tb',
            5: 'Pb',
            6: 'Eb'
    bsize : int
        size of a block

    Returns
    -------
    int: bytes converted to MB, GB, TB, or PB
    the value converted to the desired units in case of not defining the value for the
        argument "to" will automatically be converted to the corresponding unit

    Examples
    --------
    >>> from core_utils.utils import bytes_to
    >>> bytes_to(1024)

    """
    a = {0: "", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P", 6: "E"}
    r = float(bytes_)
    for _ in range(to):
        r = r / bsize
    if r >= 1000:
        to += 1
        return bytes_to(bytes_, to)
    r = f"{str(r)[:str(r).index('.') + 2]}{a[to]}B"
    return r


def sort_dict_by_keys(data, keys, reverse=False):
    """
    Sort a dictionary by keys.

    Parameters
    ----------
    data : dict
    keys : list
    reverse : bool

    Returns
    -------
    dict: sorted dictionary by keys.

    Examples
    --------
    >>> from core_utils.utils import sort_dict_by_keys
    >>> sort_dict_by_keys({"a": 1, "b": 2}, ["a", "b"])

    """
    return sorted(data, key=lambda x: [x[k] for k in keys], reverse=reverse)


def cast_python_default(data):
    """
    Cast python default values.

    Parameters
    ----------
    data : dict

    Returns
    -------
    dict: casted python default values.

    Examples
    --------
    >>> from core_utils.utils import cast_python_default
    >>> cast_python_default({"a": 1, "b": Decimal(1)})

    """
    return json.loads(json.dumps(data, default=cast_default, ensure_ascii=False))


def get_uniques_in_lists(iter_a, iter_b):
    """
    Get uniques in two lists.

    Parameters
    ----------
    iter_a : list
    iter_b : list

    Returns
    -------
    list: uniques in two lists.

    Examples
    --------
    >>> from core_utils.utils import get_uniques_in_lists
    >>> get_uniques_in_lists([1, 2, 3], [2, 3, 4])

    """
    return list(filter(lambda x: x not in iter_a, iter_b)) + list(
        filter(lambda x: x not in iter_b, iter_a)
    )


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def get_date_by_timezone(timezone):
    """

    Parameters
    ----------

    Returns
    -------
    Example
    >>> from core_utils.utils import get_date_by_timezone
    >>> tz_datetime = get_date_by_timezone(timezone)
    """
    tz = pytz.timezone(timezone)
    return datetime.datetime.now(tz=tz)


def get_validation_response(*, method_name, response):
    if not response:
        raise TypeError(f"No data found in {method_name}")

    status_code = get_status_code(response)
    if 200 != status_code:
        raise TypeError(
            f"status_code != 200 in {method_name} [status_code: {status_code}, response: {response}]"
        )

    return get_body(response)


def validate_date_format(date_to_validate, date_format="%Y-%m-%d"):
    """
    Validate if a date can be converted a specific format
    Args:
        date_to_validate: (str) -> Date to convert
        date_format: (str) -> format to convert date

    Returns: (datetime) -> Date converted
    Raises: (ValueError) -> Date that not convert in date with the format passed

    """
    try:
        return datetime.datetime.strptime(date_to_validate, date_format)
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def get_header(event: Union[str, dict]):
    """
    Get headers if lambda has proxy lambda integration in api_local gateway.
    Parameters
    ----------
    event : dict
    Returns
    -------
    dict
        dictionary with path parameters if exists.
    Examples
    --------
    >>> from core_utils.utils import get_header
    >>> get_path_parameters({"headers": {"a": 1}})"""
    if isinstance(event, str):
        events = json.loads(event)
        return events.get("headers") or {}
    return event.get("headers") or {}


def calculate_hash(str):
    # encode the string
    encoded_str = str.encode()

    # create a sha1 hash object initialized with the encoded string
    hash_obj = hashlib.sha1(encoded_str)

    # convert the hash object to a hexadecimal value
    hex_value = hash_obj.hexdigest()
    return hex_value


class DecimalEncoder(json.JSONEncoder):
    """Encodes Decimal values as strings for JSON"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def divide_chunks(list, n):
    """Divide a list into size n chunks"""
    for i in range(0, len(list), n):
        yield list[i:i + n]


def download_file(url, file_name, headers=""):
    response = requests.get(url, headers=headers)
    f = tempfile.NamedTemporaryFile(suffix=file_name, delete=False)
    f.write(response.content)
    f.close()
    return f.name

