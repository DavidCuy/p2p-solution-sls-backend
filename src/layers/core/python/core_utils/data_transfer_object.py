# -*- coding: utf-8 -*-
import enum
import json

from aws_lambda_powertools.utilities.parser import (
    ValidationError,
    parse,
)
from core_api.utils import (
    get_body,
    get_path_parameters,
    get_query_parameters,
)


class DtoType(enum.Enum):
    Header = 1
    Body = 2
    Query = 3
    Path = 4


def model_validate(model, event, _type=None):
    try:
        if DtoType.Body == _type:
            payload = get_body(event) or {}
        elif DtoType.Query == _type:
            payload = get_query_parameters(event) or {}
        elif DtoType.Path == _type:
            payload = get_path_parameters(event) or {}
        else:
            payload = event

        return parse(event=payload, model=model)
    except ValidationError as e:
        raise ValueError(__get_message(e, _type))


def __get_message(error, _type):
    if DtoType.Header == _type:
        _type = "header"
    elif DtoType.Body == _type:
        _type = "body"
    elif DtoType.Query == _type:
        _type = "query"
    elif DtoType.Path == _type:
        _type = "path"
    else:
        _type = ""

    description = f"Missing {_type} parameters: "
    error = json.loads(error.json())

    for item in error:
        description += f"{item.get('loc')} {item.get('msg')}, "

    return " ".join(description[:-2].split())