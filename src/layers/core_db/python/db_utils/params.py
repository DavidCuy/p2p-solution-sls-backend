import os
from typing import Dict, Any

from db_aws.secret_manager import get_secret
from db_aws.ssm import get_parameter
from db_utils.logger import get_logger
from db_utils.app_params import ParametersAppB2C

LAYER_NAME = "params"
LOGGER = get_logger(f"layer-{LAYER_NAME}")


class ParametersDBB2C:
    def __init__(self):
        self.__db_name = os.environ.get("DB_NAME")
        self.__db_user = os.environ.get("DB_USER")
        self.__db_password = os.environ.get("DB_PASSWORD")
        self.__db_host = os.environ.get("DB_HOST")
        self.__db_port = os.environ.get("DB_PORT")
        self.__override_params()

    @property
    def name(self):
        return self.__db_name

    @property
    def user(self):
        return self.__db_user

    @property
    def password(self):
        return self.__db_password

    @property
    def host(self):
        return self.__db_host

    @property
    def port(self):
        return self.__db_port

    def __override_params(self):
        parameter_app = ParametersAppB2C()
        db_config: Dict[str, Any] = get_parameter(f"/config/infra/{parameter_app.environment}/db/credentials",
                                                  use_prefix=False, transform=True)
        if not self.__db_port and not self.__db_host and not self.__db_name:
            self.__db_name = db_config.get("db-name")
            self.__db_host = db_config.get("db-host")
            self.__db_port = db_config.get("db-port")
        self.__get_access_credentials(db_config.get("db-password"))

    def __get_access_credentials(self, secret_arn: str):
        if self.__db_user and self.__db_password:
            return
        credentials = get_secret(secret_arn, use_prefix=False, transform=True)
        try:
            self.__db_user = credentials["username"]
            self.__db_password = credentials["password"]
        except KeyError:
            LOGGER.exception("Not found key in the secret.")


