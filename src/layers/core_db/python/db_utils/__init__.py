# -*- coding: utf-8 -*-
import os

try:
    if not os.getenv("DEVELOPER"):
        print("patching...")
        from aws_xray_sdk.core import patch_all

        patch_all()
except Exception as e:
    print(str(e))


def load_environment_variables():
    try:
        from dotenv import load_dotenv
    except ImportError:
        pass
    else:
        if os.getenv("DEVELOPER") == "DeployUnittest":
            load_dotenv("./.env", override=False)
        load_dotenv()


load_environment_variables()
