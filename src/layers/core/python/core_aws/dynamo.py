# -*- coding: utf-8 -*-
import datetime
import logging
from core_aws.sts import get_session_sts, get_client_sts
from decimal import Decimal

import boto3
from boto3.dynamodb.types import (
    TypeSerializer,
)
from botocore.exceptions import (
    ClientError,
)
from core_utils.utils import get_logger
from core_utils.environment import ParametersApp

__all__ = [
    "get_table",
    "put_item",
    "update_item",
    "get_items_by_query",
    "get_item",
    "batch_write_item"
]

_SERIALIZER = TypeSerializer()
_DYNAMODB = boto3.client("dynamodb")
_LOGGER = get_logger("layer-dynamo")
_PARAMS = ParametersApp()


def put_item(table: str, item: dict, log_level=None, role=None, use_prefix=False):
    """Creates an item in the specified table from DynamoDB

    Parameters
    ----------
    table : str
        The name of the table where the item will be created.
    item : dict
        The item that will be created
    log_level : int | None
        The log level to use if an error occurs when creating the item

    """
    if use_prefix:
        prefix = f"{_PARAMS.environment}-{_PARAMS.app_name}"
        table = f"{prefix}-{table}"
    client = _DYNAMODB if not role else get_client_sts(role)
    item = {k: _SERIALIZER.serialize(v) for k, v in item.items()}
    try:
        response = client.put_item(
            TableName=table,
            Item=item,
        )
    except ClientError:
        _LOGGER.log(
            level=log_level or logging.ERROR,
            msg=f"An exception occurred when creating an item on table {table}.",
            exc_info=True,
            extra={"item": item},
        )
        return False

    if "ResponseMetadata" not in response and response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        _LOGGER.log(
            level=log_level or logging.ERROR,
            msg=f"DynamoDB responded with an error when creating an item on table {table}. ",
            extra={"item": item, "dynamodb_response": response},
        )
        return False
    return True


def get_table(table_name, role=None):
    """
    get a table from dynamo.
    Parameters
    ----------
    table_name : str
    role : str
    Returns
    -------
    dynamo table.
    Examples
    --------
    >>> from core_aws.dynamo import get_table
    >>> get_table('table_name_dynamo')
    """
    dynamodb = boto3.resource("dynamodb") if not role else get_session_sts(role).resource("dynamodb")
    table = dynamodb.Table(table_name)
    return table


def update_item(table_name, key, fields_to_update, update_date_field=None,role=None):
    """
    update a record table from dynamo.
    Parameters
    ----------
    table_name : str
    key: dict
    fields_to_update: dict
    update_date_field: str
    Returns
    -------
    (bool) -> Confirm if the record was updated or not
    Examples
    --------
    >>> from core_aws.dynamo import update_item
    >>> update_item('Client', {"id": 1}, {"name": "Joe", "lastName": "Doe"})
    """
    localtime = datetime.datetime.now()
    if update_date_field:
        fields_to_update.update(
            {update_date_field: str(localtime.isoformat(timespec="seconds"))}
        )

    (
        update_expression,
        values_expression,
        expression_attribute_names,
    ) = __define_parameters_update_table(fields_to_update)

    try:
        table = get_table(table_name,role)
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=values_expression,
            ExpressionAttributeNames=expression_attribute_names,
        )
        if (
                "ResponseMetadata" not in response
                or response["ResponseMetadata"]["HTTPStatusCode"] != 200
        ):
            return False
    except Exception as err:
        message = (
            "Exception founded when trying to update a record. Key: {key}, "
            "table: {table}, fields to update: {fields}, exception: {err}"
        )
        _LOGGER.error(
            message.format(key=key, table=table_name, fields=fields_to_update, err=err)
        )
        return False

    return True


def __define_parameters_update_table(fields_to_update: dict):
    """
    Build expressions to use in update_item from fields to update
    Parameters
    ----------
    fields_to_update: (dict) -> Fields to build expression to update

    Returns
    -------
    update_expression (str) -> String to contain fields to update
    values_expression (dict) -> Dict to contain values to save
    expression_attribute_names (dict) -> Expression to get values and fields to send and update method
    """
    update_expression = "set "
    values_expression = {}
    expression_attribute_names = {}
    index = 1
    for _field, _value in fields_to_update.items():
        if index == 1:
            update_expression += f"#{_field}= :{_field}"
        else:
            update_expression += f", #{_field}= :{_field}"

        if isinstance(_value, bool):
            _value = bool(_value)
        elif isinstance(_value, int):
            _value = int(_value)
        elif isinstance(_value, float):
            _value = Decimal(str(_value))
        expression_attribute_names.update({f"#{_field}": _field})
        values_expression.update({f":{_field}": _value})
        index += 1
    return update_expression, values_expression, expression_attribute_names


def get_items_by_query(table_name, index, key_condition, expr_attr_values=None, filter_expression=None, client=None,
                       use_prefix=False):
    prefix = f"{_PARAMS.environment}-{_PARAMS.app_name}"
    table_name = f"{prefix}-{table_name}" if use_prefix else table_name

    table = client or get_table(table_name)
    query = {"KeyConditionExpression": key_condition}

    if index:
        query.update({'IndexName': index})

    if client:
        query.update({'TableName': table_name})

    if filter_expression:
        query.update({'FilterExpression': filter_expression})

    if expr_attr_values:
        query.update({'ExpressionAttributeValues': expr_attr_values})

    response = table.query(**query)
    items = response.get('Items').copy()
    while 'LastEvaluatedKey' in response and items:
        response = table.query(**query)
        items.extend(response.get('Items'))
    response['Items'] = items
    return response


def get_item(*, table_name, key, role=None, use_prefix=True):
    """Gets an item from a table with the specified key

    Parameters
    ----------
    table_name : str
        The name of the table of the item
    key : dict
        The key of the item
    role : str
        The ARN of the role to assume to get the item
    use_prefix : bool
        True if the prefix should be used to construct the table name, false otherwise

    Returns
    -------
    dict
        The DyanmoDB item

    Examples
    --------
    >>> from core_aws.dynamo import get_item
    >>> get_item("Invoices", {"cdc": "123456"}, "arn:aws:iam::916865476601:role/role")
    """
    prefix = f"{_PARAMS.environment}-{_PARAMS.app_name}"
    table_name = f"{prefix}-{table_name}" if use_prefix else table_name

    table = get_table(table_name, role)
    response = table.get_item(Key=key)
    return response.get("Item")


def batch_write_item(table, items, role=None):
    """Puts multiple items in the table specified

    Parameters
    ----------
    table : str
        The name of the table where the items will be stored.
    items : list
        The items that will be stored in the table.
    role : str
        The arn of the role to use for the DynamoDB session.
    """
    table = get_table(table, role)
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
