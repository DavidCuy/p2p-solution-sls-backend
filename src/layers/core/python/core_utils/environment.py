# -*- coding: utf-8 -*-
"""
This module contains the Environment class.
"""
import os


class ParametersApp:
    def __init__(self):
        # Required environment variables
        self.__environment = os.environ["ENVIRONMENT"]
        self.__app_name = os.environ.get("APP_NAME")
        self.__log_level = os.environ.get("LOG_LEVEL")
        self.__region = os.environ.get("REGION")

        # Required environment variables in local
        self.__developer = os.environ.get("DEVELOPER")

        # AWS Lambda environment variables
        self.__lambda_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")

    @property
    def environment(self):
        return self.__environment

    @property
    def developer(self):
        return self.__developer

    @property
    def app_name(self):
        return self.__app_name

    @property
    def lambda_name(self):
        return self.__lambda_name

    @property
    def log_level(self):
        return self.__log_level

    @property
    def region(self):
        return self.__region

