# -*- coding: utf-8 -*-
import boto3
import json
from botocore.exceptions import (
    ClientError,
)
from core_utils.utils import (
    get_logger,
    cast_default
)
from datetime import datetime

__all__ = [
    "put_event"
]

LOGGER = get_logger("layer-eventbridge")

def put_event(*, event_name: str, event_input: dict, source: str = 'lambda', bus_name: str = 'default') -> True:
    """
    This function sends an event to AWS EventBridge.

    Parameters:
    - event_name (str): The name of the event.
    - event_input (dict): A dictionary containing the details of the event.
    - source (str): The source of the event. Defaults to 'lambda'.
    - bus_name (str): The name of the EventBridge bus. Defaults to 'default'.

    Returns:
    - bool: Returns True if the event was successfully sent, otherwise False.

    Raises:
    - ClientError: If an error occurs while creating the EventBridge client.

    Example:
    ```python
    from datetime import datetime

    # Define the event details
    event_name = 'sample_event'
    event_input = {'key': 'value'}

    # Send the event
    result = put_event(event_name, event_input)

    # Check if the event was successfully sent
    if result:
        print('Event sent successfully')
    else:
        print('Failed to send event')
    ```
    """
    try:
        eb = boto3.client('events')
    except Exception as details:
        LOGGER.error("Error create client ssm")
        LOGGER.error("Details: {}".format(details))
        raise ClientError
    eb_response = eb.put_events(
        Entries=[
            {
                'Time': datetime.now(),
                'Source': source,
                'DetailType': event_name,
                'Detail': json.dumps(event_input, default=cast_default, ensure_ascii=False),
                'EventBusName': bus_name
            },
        ]
    )

    return all(list(map(lambda entry: 'EventId' in entry, eb_response['Entries'])))
