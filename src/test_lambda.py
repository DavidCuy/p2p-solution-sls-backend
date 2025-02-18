# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path
from unittest import TestCase


class Test(TestCase):
    files_configs = None

    def get_configs(self):
        if not self.files_configs:
            self.files_config = Path(".").glob("**/configuration.json")
        return self.files_config

    def get_lambda_name(self, file):
        return file.parent.name

    def test_no_more_enviroment_variables(self):
        files = self.get_configs()
        error = {}
        for file in files:
            validations = json.loads(Path(file).read_text())
            variables = validations.get("cfn")["Properties"]["Environment"]["Variables"]

            validations = list(
                filter(
                    lambda r: r not in ["ENVIRONMENT", "APP_NAME", "LOG_LEVEL", "POWERTOOLS_SERVICE_NAME",
                                        "UNIVERSAL_BUTTON"],
                    list(variables.keys()),
                )
            )

            if len(validations):
                error[str(file)] = validations

        msj = (
                "Envioroments Variables just cant have ENVIRONMENT, APPNAME\n "
                + str(len(error.keys()))
                + " lambdas wrongs"
        )
        self.assertFalse(len(error.keys()), msj)

    def test_no_api_verbs(self):
        files = self.get_configs()
        error = {}
        except_lambdas = ['get_agent_information', 'get_client_information', 'get_otp', 'get_validation_dpi',
                          'update_status_process_status']
        no_words = [
            "GET",
            "post",
            "patch",
            "add",
            "Delete",
            "Head",
            "Put",
            "remove",
            "create",
            "update",
        ]

        for file in files:
            lambda_name = self.get_lambda_name(file)
            if lambda_name in except_lambdas:
                print(lambda_name)
                continue
            validations = json.loads(Path(file).read_text())
            endpoints = list(
                filter(lambda x: x != "Parent", list(validations.get("swagger").keys()))
            )

            validations = list(
                filter(
                    lambda r: re.search(f"({'|'.join(no_words)})", r, re.IGNORECASE),
                    endpoints,
                )
            )

            if len(validations):
                error[str(file)] = validations

        msj = (
                "No verbs\n "
                + str(len(error.keys()))
                + " lambdas wrongs2"
                + str(list(error.keys()))
        )
        self.assertFalse(len(error.keys()), msj)

    def test_Summary_and_Security(self):
        files = self.get_configs()
        no_summary = []
        no_sec = []
        for file in files:
            validations = json.loads(Path(file).read_text())
            swagger = validations.get("swagger")
            lambda_name = self.get_lambda_name(file)
            keys = [cl for cl in swagger.keys() if cl != 'Parent']

            for k in keys:
                s = swagger.get(k)
                verbs = [cl for cl in s.keys() if cl.lower() not in ['parent', 'options']]
                for v in verbs:
                    vv = s[v]
                    ss = vv.get('summary')
                    sec = [x for x in vv.get('security')[0].keys() if x != 'api_key']
                    if not ss:
                        no_summary.append(str(lambda_name))
                    if not sec:
                        no_sec.append(str(lambda_name))
        print(f'{len(no_summary)} lambdas without summary -  {no_summary}')
        print(f'{len(no_sec)} lambdas without security -  {no_sec}')
