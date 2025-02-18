import boto3
from aws_lambda_powertools.utilities.parameters.exceptions import GetParameterError
from core_utils.utils import get_logger

__all__ = [
    "assume_role",
    "get_client_sts",
    "get_session_sts",
    "generate_export"
]

LAYER_NAME = "sts"

LOGGER = get_logger(f"layer-{LAYER_NAME}")


def assume_role(role_arn, session_name):
    """Geta a set of temporary security credentials to access AWS resources

    Parameters
    ----------
    role_arn : str
        The ARN of the role to assume
    session_name : str
        An identifier for the assumed role session

    Returns
    -------
    dict
        Temporary credentials to make AWS requests
    """
    sts_client = boto3.client("sts")
    return sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name)


def get_client_sts(arn_account: str, region="us-east-1"):
    """
    Get session with arn account different
    Parameters
    ----------
    arn_account: "arn:aws:iam::0123456789:role/Test"

    Returns
    -------
    result: conexion
    """
    try:
        sts_session = assume_role(arn_account, "dynamodb-session")
        result = boto3.client('dynamodb',
                              region_name=region,
                              aws_access_key_id=sts_session['Credentials']['AccessKeyId'],
                              aws_secret_access_key=sts_session['Credentials']['SecretAccessKey'],
                              aws_session_token=sts_session['Credentials']['SessionToken'])

    except GetParameterError as error:
        LOGGER.exception(f"{error}")
        raise error
    else:
        return result


def get_session_sts(arn_account: str, region="us-east-1"):
    """Gets a boto3 session using the specified role

    Parameters
    ----------
    arn_account : str
        The ARN of the role to use for the session
    region : str
        The region where the session will be created

    Returns
    -------
    boto3.session.Session
        A session to create clients and resources
    """
    try:
        sts_session = assume_role(arn_account, "cross-account-session")
        result = boto3.Session(region_name=region,
                               aws_access_key_id=sts_session['Credentials']['AccessKeyId'],
                               aws_secret_access_key=sts_session['Credentials']['SecretAccessKey'],
                               aws_session_token=sts_session['Credentials']['SessionToken'])
    except GetParameterError as error:
        LOGGER.exception(f"Error getting session with role {arn_account}")
        raise error
    return result


def generate_export(cxndynamo: any, old_accountid: int, bucket_name: str, accountawsid: int, route: str,
                    table_name: str,
                    clienttoken: str,
                    region="us-east-1",
                    tpformat="DYNAMODB_JSON"):
    """
    Parameters
    ----------
    cxndynamo:cnx database
    accountid: aws account id
    bucket_name: s3 bucket name
    route: route to save the export
    table_name: table fromo dynamo to export
    region: us-east-1
    tpformat: can be DYNAMODB_JSON or ION

    Returns
    -------

    """
    try:
        if clienttoken != "":
            response = cxndynamo.export_table_to_point_in_time(
                TableArn='arn:aws:dynamodb:' + region + ':' + str(old_accountid) + ':table/' + table_name,
                ClientToken=clienttoken,
                S3Bucket=bucket_name,
                S3BucketOwner=accountawsid,
                S3Prefix=route,
                ExportFormat=tpformat)
        else:
            response = cxndynamo.export_table_to_point_in_time(
                TableArn='arn:aws:dynamodb:' + region + ':' + str(old_accountid) + ':table/' + table_name,
                S3Bucket=bucket_name,
                S3BucketOwner=accountawsid,
                S3Prefix=route,
                ExportFormat=tpformat)
    except GetParameterError as error:
        LOGGER.exception(f"{error}")
        raise error
    else:
        return response
