# -*- coding: utf-8 -*-
import json

import boto3
from core_utils.utils import get_logger

__all__ = [
    "execute_sfn",
    "describe_execution",
    "list_executions"
]
LOGGER = get_logger("layer-sfn")


def execute_sfn(*, name, state_machine_arn, input_value, region_name="us-east-1"):
    """
    Starts a state machine execution.

    Args:
        name: (str) The executions name. This name must be unique. A recommendation is use an
            uuid to identify an execution
        state_machine_arn: (str) Arn of the state machine to execution.
        input_value: (dict) Input data for the execution.
        region_name : (str) Region where the cognito instance is located. us-east-1 by default.

    Returns: (dict)
        The result of the state machine execution.

    Raises:
        ValueError
            If the state machine arn is not valid.

    Examples
        from core_aws.sfn import execute_sfn
        get_parameter(stateMachineArn="arn:aws:state:my_arn", name="mi_execution_name", input={'key':value})
    """
    try:
        sfn = boto3.client("stepfunctions", region_name=region_name)
        return sfn.start_execution(
            stateMachineArn=state_machine_arn,
            name=name,
            input=json.dumps(input_value, default=str),
        )
    except Exception as details:
        LOGGER.warning(details)
        return None


def describe_execution(*, execution_arn, region_name="us-east-1"):
    """
        Describes an execution from SM.

        Args:
            execution_arn: (str) The Amazon Resource Name (ARN) that identifies the execution
            region_name : (str) Region where the cognito instance is located. us-east-1 by default.

        Returns: (dict)
            The result of the state machine execution.

        Examples
            from core_aws.sfn import describe_execution
            describe_execution(execution_arn="execution_arn")
        """
    try:
        sfn_client = boto3.client("stepfunctions", region_name=region_name)
        return sfn_client.describe_execution(
            executionArn=execution_arn)
    except Exception as details:
        LOGGER.error(details)
        return None


def list_executions(state_machine_arn, status=None, region_name="us-east-1"):
    """
    Lists the executions of a state machine.

    Args:
        state_machine_arn (str): The Amazon Resource Name (ARN) that identifies the state machine.
        status (str, optional): The status of the executions to list. If not specified, all executions are listed.
        region_name (str, optional): The AWS Region where the state machine is located. Defaults to 'us-east-1'.

    Returns:
        dict: A dictionary containing the list of executions.

    Raises:
        ValueError: If the state machine ARN is not valid.

    Examples:
        from core_aws.sfn import list_executions
        list_executions(state_machine_arn="arn:aws:state:my_arn")
    """
    sfn = boto3.client('stepfunctions', region_name=region_name)
    return sfn.list_executions(stateMachineArn=state_machine_arn, statusFilter=status)

def get_events_from_execution(*, execution_arn: str, region_name:str ="us-east-1", results_steps: int=1000) -> list:
    """
    Retrieves the events from a specific execution.

    Args:
        execution_arn (str): The Amazon Resource Name (ARN) that identifies the execution.
        region_name (str, optional): The AWS Region where the state machine is located. Defaults to 'us-east-1'.
        results_steps (int, optional): The maximum number of results to return. Defaults to 1000.

    Returns:
        list: A list of dictionaries containing the events from the specified execution.

    Raises:
        ValueError: If the execution ARN is not valid.

    Examples:
        from core_aws.sfn import get_events_from_execution
        events = get_events_from_execution(execution_arn="execution_arn", region_name="us-east-1")
    """
    try:
        sfn_client = boto3.client("stepfunctions", region_name=region_name)
        response = sfn_client.get_execution_history(
            executionArn=execution_arn,
            maxResults=results_steps
        )
        events: list = response["events"]

        while response.get("nextToken"):
            response = sfn_client.get_execution_history(
                executionArn=execution_arn,
                maxResults=results_steps,
                nextToken=response["nextToken"]
            )
            events.extend(response["events"])
        return events
    except Exception as details:
        LOGGER.error(details)
        return []

def get_failed_cause_details(*, execution_arn: str, event_type_filter: str = 'FailStateEntered',
                             region_name:str ="us-east-1", results_steps: int=1000) -> dict:
    """
    Retrieves the failed cause details from a specific execution.

    Args:
        execution_arn (str): The Amazon Resource Name (ARN) that identifies the execution.
        event_type_filter (str, optional): The type of event to filter for. Defaults to 'FailStateEntered'.
        region_name (str, optional): The AWS Region where the state machine is located. Defaults to 'us-east-1'.
        results_steps (int, optional): The maximum number of results to return. Defaults to 1000.

    Returns:
        dict: A dictionary containing the failed cause details.

    Raises:
        ValueError: If the execution ARN is not valid.

    Examples:
        from core_aws.sfn import get_failed_cause_details
        get_failed_cause_details(execution_arn="execution_arn", event_type_filter="FailStateEntered")
    """
    events = get_events_from_execution(
        execution_arn=execution_arn,
        region_name=region_name,
        results_steps=results_steps
    )

    if len(events) < 1:
        return None

    failed_causes = [e for e in events if e["type"] == event_type_filter]
    return failed_causes
