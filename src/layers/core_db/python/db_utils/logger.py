# -*- coding: utf-8 -*-
"""
Helper functions for working with Python.
"""
from typing import Any
from aws_lambda_powertools import Logger

__all__ = [
    "get_logger"
]

FORMAT = '%Y-%m-%d %H:%M:%S'


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
    >>> from db_utils.utils import get_logger
    >>> logger = get_logger("my_logger")

    """
    properties: dict[str, Any] = dict(
        log_record_order=["level", "message"],
        sampling_rate=None,
    )
    if name:
        properties.setdefault("service", name)
    return Logger(**properties)

