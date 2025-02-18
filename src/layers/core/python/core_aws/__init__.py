# -*- coding: utf-8 -*-
try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    load_dotenv()

__all__ = [
    "cognito",
    "dynamo",
    "lambdas",
    "s3",
    "secret_manager",
    "sqs",
    "ssm",
    "session",
    "sts"
]
