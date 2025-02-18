# -*- coding: utf-8 -*-

import logging
import os

import boto3
from botocore.exceptions import (
    ClientError,
)

__all__ = [
    "upload_file_to_bucket_s3",
    "get_object_key_from_trigger_s3",
    "get_bucket_name_from_trigger_s3",
    "generate_pre_signed_url",
    "get_metadata",
    "get_object",
    "upload_stream_object",
    "list_object_keys",
    "delete_object",
    "copy_object"
]

s3 = boto3.client("s3")


def upload_file_to_bucket_s3(file_name, bucket, object_name=None, is_pdf=False):
    """
    Upload a file to a bucket.

    Parameters
    ----------
    file_name : str
    bucket : str
    object_name : str
    is_pdf: bool

    Returns
    -------
    False if the file is not found or True else.

    Examples
    --------
    >>> from core_aws.s3 import upload_file_to_bucket_s3
    >>> upload_file_to_bucket_s3(file_name='my-file.txt', bucket='my-bucket')

    """
    if not object_name:
        object_name = os.path.basename(file_name)

    extra_args = {}

    if is_pdf:
        extra_args['ContentType'] = 'application/pdf'

    try:
        response = s3.upload_file(file_name, bucket, object_name, ExtraArgs=extra_args)
    except ClientError as e:
        logging.error(e)
        return False
    logging.debug(str(response))
    return True


def get_object_key_from_trigger_s3(event):
    """
    Gets object key from an event if this is sending by a trigger s3 event.

    Parameters
    ----------
    event : dict

    Returns
    -------
    Object key.

    Examples
    --------
    >>> from core_aws.s3 import get_object_key_from_trigger_s3
    >>> get_object_key_from_trigger_s3(event={'Records': [{'s3': {'object': {'key': 'my-key'}}}]})

    """

    try:
        name = event["Records"][0]["s3"]["object"]["key"]
    except KeyError:
        return None
    return name


def get_bucket_name_from_trigger_s3(event):
    """
    Gets bucket name from an event if this is sending by a trigger s3 event.

    Parameters
    ----------
    event : dict
        Event from trigger s3.

    Returns
    -------
    Bucket name.

    Examples
    --------
    >>> from core_aws.s3 import get_bucket_name_from_trigger_s3
    >>> get_bucket_name_from_trigger_s3(event={'Records': [{'s3': {'bucket': {'name': 'my-bucket'}}}]})

    """
    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
    except KeyError:
        return None
    return bucket


def generate_pre_signed_url(*, bucket, object_key, in_line=False, expiration=3600, client_action='get_object'):
    """
    Generate pre-signed url for an object in a bucket.

    Parameters
    ----------
    bucket : str
        Bucket name where the object is stored.
    object_key : str
        Key of the object.
    in_line: bool

    expiration : int
        Expiration time in seconds. Default is 1 hour.
    client_action: str
        Client action for the url. Default is get_object

    Returns
    -------
    A pre-signed url.

    Examples
    --------
    >>> from core_aws.s3 import generate_pre_signed_url
    >>> generate_pre_signed_url(bucket='my-bucket', object_key='my-key')

    """
    parameters = {"Bucket": bucket, "Key": object_key}
    if in_line:
        parameters.update({"ContentDisposition": "inline"})

    response = s3.generate_presigned_url(
        ClientMethod=client_action, Params=parameters, ExpiresIn=expiration
    )
    return response


def get_metadata(*, bucket: str, key: str, default=None):
    """Get metadata from an s3 object.

    Request an object from s3 and return get the metadata if it not found return default value.

    Parameters
    ----------
    bucket : str
        Bucket name where the object is stored.
    key : str
        Key of the object.
    default : any
        Default value to return if the object metadata is not found.

    Returns
    -------
    An object metadata or default value.

    Examples
    --------
    >>> from core_aws.s3 import get_metadata
    >>> get_metadata(bucket='my-bucket', key='my-key')

    """
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj.get("Metadata", default)


def get_object(bucket: str, key: str):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response.get("Body")
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") == "NoSuchKey":
            raise ValueError(f"The object {key} doesn't exist on the bucket {bucket}.")
        raise


def upload_stream_object(bucket: str, key: str, body, content_type='text/plain'):
    """Put a stream object in the specified bucket

    Parameters
    ----------
    bucket : str
        The name of the bucket which objects want to be saved
    key : str
        The name of file
    body : Any
        The properties file
    content_type : str
        the content type of file

    Returns
    -------
    Dict
        A Dict whit details response

    Examples
    --------
    >>> from core_aws.s3 import put_stream_object
    >>> put_stream_object(bucket='my-bucket', key='my-key', body="open(filename, 'rb')",
    >>> content_type='application/pdf')
    """

    return s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType=content_type)


def list_object_keys(bucket, prefix):
    """Lists the objects in the specified bucket that have certain prefix

    Parameters
    ----------
    bucket : str
        The name of the bucket which objects want to be listed
    prefix : str
        The prefix that will be used to search the objects on the bucket

    Returns
    -------
    list
        A list with the keys of the objects found on the bucket
    """
    response = s3.list_objects(Bucket=bucket, Prefix=prefix)
    return list(map(lambda o: o.get("Key"), response.get("Contents", [])))


def get_client(*, region="us-east-1", access_key_id=None, secret_access_key=None, session_token=None):
    """Gets a s3 client using the specified credentials, or default credentials if none specified

    Parameters
    ----------
    region : str
        The region of the client
    access_key_id : str
        The AWS access key id
    secret_access_key : str
        The AWS secret access key
    session_token : str
        The AWS session token

    Returns
    -------
    S3.Client
        A low-level client representing S3

    """
    if not access_key_id or not secret_access_key or not session_token:
        return s3
    else:
        return boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token
        )


def copy(copy_source, client_source, bucket, key):
    """Copies an object from one S3 location to another

    Parameters
    ----------
    copy_source : dict
        The name of the source bucket and key name of the source object
        {'Bucket': 'bucket', 'Key': 'key' }
    client_source : boto3 Client
        The client to be used for operation that may happen at the source object.
    bucket : str
        The name of the bucket to copy to
    key : str
        The name of the key to copy to
    """
    s3.copy(copy_source, bucket, key, SourceClient=client_source)


def copy_object(*, bucket, source_key, destination_key):
    """Copies an object from one bucket to another

    Parameters
    ----------
    bucket : str
        The destination bucket where the object will be copied to
    source_key : str
        The key of the object to copy, i.e. /sourcebucket/HappyFacejpg
    destination_key : str
        The key the object will have on the destination bucket

    Returns
    -------
    dict
        The response from s3
    """
    return s3.copy_object(Bucket=bucket, CopySource=source_key, Key=destination_key)


def delete_object(*, bucket, key):
    """Deletes an object

    Parameters
    ----------
    bucket : str
        The bucket where the object is stored
    key : str
        The key of the object to delete

    Returns
    -------
    dict
        The response from s3
    """
    return s3.delete_object(Bucket=bucket, Key=key)


def try_download_file(*, bucket, key, filename):
    """Downloads an S3 objet to a file

    Parameters
    ----------
    bucket : str
        The name of the bucket to download from
    key : str
        The name of the key to download from
    filename : str
        The path to the file to download to
    """
    s3.download_file(bucket, key, filename)
