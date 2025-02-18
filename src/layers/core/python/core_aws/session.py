# -*- coding: utf-8 -*-
__all__ = ["get_current_region", "get_current_account"]

import boto3

client = boto3.client("sts")
session = boto3.session.Session()


def get_current_region():
    """
    Obtain a current region using in AWS account
    Returns: (str)
        Region name associated to current user

    """
    return session.region_name


def get_current_account():
    """
    The Amazon Web Services account ID number of the account that owns or contains the calling entity
    Returns: (str)
        Account ID number
    """
    return client.get_caller_identity()["Account"]


def get_session_by_role(access_key_id: str, secret_access_key: str, session_token: str):
    """
    A session stores configuration state and allows you to create service clients and resources.
    Args:
        access_key_id: (str) AWS access key ID
        secret_access_key: (str) AWS secret access key
        session_token: (str) AWS temporary session token

    Returns: (botocore.session.Session)
        Service client instance

    """
    return boto3.session.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
    )
