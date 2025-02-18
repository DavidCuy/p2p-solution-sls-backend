"""
Helper functions for security.
"""

import jwt
import hashlib
import core_utils.environment
from core_aws.secret_manager import get_secret
from core_utils.utils import get_logger
from datetime import datetime, timedelta

__all__ = [
    "calculate_security_hash",
    "encode_token",
    "decode_token"
]


DEFAULT_SECRET_PATH = f"secret-agent-token"
LOGGER = get_logger('core_utils.security')


def calculate_security_hash(client_msisdn: str, agent_msisdn: str, otp: str):
    """Calculate hex hash based on client_msisdn. agent_msisdn and otp.

    Args:
        client_msisdn (str): Client msisdn,
        agent_msisdn (str): Agent msisdn,
        otp (str): valid OTP,

    Returns:
        str: hex hash.
    """
    complete_str = f'{client_msisdn}#{otp}#{agent_msisdn}'
    # encode the string
    complete_str = complete_str.encode()

    # create a sha1 hash object initialized with the encoded string
    hash_obj = hashlib.sha1(complete_str)

    # convert the hash object to a hexadecimal value
    hex_value = hash_obj.hexdigest()
    return hex_value


def encode_token(payload: dict, expiration_minutes=30, secret=None, algorithm='HS256'):
    """encode a token with a secret key.

    Args:
        payload (dict): payload to encode,
        expiration_minutes(int) expiration in minutes,
        secret (str): secret key,
        algorithm(str) algorithm to encode
    Returns:
        str: token encoded.
    """
    # Calculate the expiration time
    expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)

    # Add the expiration time to the payload
    payload['exp'] = expiration_time
    if not secret:
        secret = get_secret(DEFAULT_SECRET_PATH)
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_token(token, secret=None, algorithm='HS256'):
    """decode a token with a secret key.

    Args:
        token (str): encoded token,
        secret (str): secret key,
        algorithm(str) algorithm to decode
    Returns:
        dict: token decoded.
    """
    if not secret:
        secret = get_secret(DEFAULT_SECRET_PATH)
    try:
        # Decode and verify the token
        decoded_token = jwt.decode(token, secret, algorithms=[algorithm])

        # If decoding is successful, the token is valid
        return decoded_token
    except jwt.exceptions.ExpiredSignatureError:
        LOGGER.error("Token has expired.")
    except jwt.exceptions.InvalidTokenError:
        LOGGER.error("Invalid token.")
    except Exception as e:
        LOGGER.error(f"Error validating token: {e}")
    return None
