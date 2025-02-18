import json
import unittest
from http import HTTPStatus
from unittest import TestCase, mock

from core_api.utils import (
    get_body,
    get_status_code,
)

from lambda_function import (
    lambda_handler,
)


def mock_exception_raised(*_, **__):
    """
    Mock that raises an error to simulate that an error is raised
    Raises: (RuntimeError)
        Custom error -> Mock error simulated

    """
    raise RuntimeError("Mock error raised")


mock_event_from_sqs = {
    "Records": [
        {
            "body": json.dumps({
                "status": "created",
                "source_id": 1,
                "dest_id": 2,
                "created_at": "2025-02-18T19:21:46.395003",
                "amount": 17.0,
                "id": 8
            })
        }
    ]
}

mock_get_ssm_parameter = "/my-parameter"


def call_lambda(mock_test):
    """
    Common method to call lambda to test


    Returns: dict, int
        response: dict -> A data response from lambda
        status_code: int -> status code from the lambda requested
    """
    response = lambda_handler(mock_test, None)
    status_code = get_status_code(response)
    body = get_body(response)
    return body, status_code


class TestP2PTrxReq(TestCase):
    """
    Test lambda to execute step function to notificate approved invoices
    """

    def setUp(self) -> None:
        """
        Prepare data to test
        """
        self.event_successfully = mock_event_from_sqs

    def __common_asserts(
            self, body, status_code, expected_status_code
    ):
        """
        Method to apply common asserts
        Args:
            status_code: (int) -> Response status to check
            expected_status_code: (int) -> Response status that will expect
        """
        self.assertEqual(expected_status_code, status_code)


    @mock.patch("core_aws.ssm.get_parameter", return_value=mock_get_ssm_parameter)
    def test_lambda_successfully(self, *_, **__):
        """
        Unit test when the step function was executed successfully

        """
        body, status_code = call_lambda(self.event_successfully)
        self.__common_asserts(
            body,
            status_code,
            HTTPStatus.OK.value
        )

    @mock.patch("core_aws.ssm.get_parameter", return_value=mock_get_ssm_parameter)
    def test_lambda_exception(self, *_, **__):
        """
        Unit test when found an exception when try to execute step function

        """
        body, status_code = call_lambda(self.event_successfully)
        self.__common_asserts(
            body,
            status_code,
            HTTPStatus.INTERNAL_SERVER_ERROR.value
        )


    @mock.patch("core_aws.ssm.get_parameter", return_value=mock_get_ssm_parameter)
    def test_lambda_failed(self, *_, **__):
        """
        Unit test when teh step function failed to be executed
        """
        body, status_code = call_lambda(self.event_successfully)
        self.__common_asserts(body, status_code, HTTPStatus.INTERNAL_SERVER_ERROR.value)

test_suites = unittest.TestSuite()
testLambda = TestP2PTrxReq()
testLambda.setUp()
test_suites.addTest(testLambda.test_lambda_successfully)
#test_suites.addTest(testLambda.test_signed_url_cycle_gcp)

runner = unittest.TextTestRunner()
runner.run(test_suites)