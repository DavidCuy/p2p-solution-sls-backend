# -*- coding: utf-8 -*-
try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    load_dotenv()

__all__ = [
    "secret_manager",
    "ssm"
]
