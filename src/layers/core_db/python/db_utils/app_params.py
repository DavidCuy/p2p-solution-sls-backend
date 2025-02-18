import os
from db_utils.logger import get_logger

LAYER_NAME = "params"
LOGGER = get_logger(f"layer-{LAYER_NAME}")


class ParametersApp:
    def __init__(self):
        # Required environment variables in local
        self.__developer = os.environ.get("DEVELOPER")
        self.__environment = os.environ.get('ENVIRONMENT')
        self.__app_name = os.environ.get("APP_NAME")

        # AWS Lambda environment variables
        self.__lambda_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")

    @property
    def developer(self):
        return self.__developer

    @property
    def lambda_name(self):
        return self.__lambda_name

    @property
    def environment(self):
        return self.__environment
    
    @property
    def app_name(self):
        return self.__app_name
