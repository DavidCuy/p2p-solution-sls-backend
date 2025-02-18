from core_utils.environment import env
from core_aws.secret_manager import get_secret
from aws_lambda_powertools import Logger

LOGGER = Logger('core_db.config')

def get_db_from_secrets():
    global DB_DRIVER, DB_NAME, DB_CONNECTION_STRING, DB_SCHEMA
    
    credentials = get_secret('DBPassword', is_dict=True, use_prefix=True)
    LOGGER.info(f"Credentials: {credentials}")
    DB_ENGINE = credentials.get('engine', 'postgresql')
    DB_DRIVER = credentials.get('driver', 'psycopg2')
    DB_USER_NAME = credentials.get('username', 'root')
    DB_PASSWORD = credentials.get('password', 'root')
    DB_HOST = credentials.get('host', 'localhost')
    DB_PORT = credentials.get('port', '3306')
    DB_NAME = credentials.get('dbname', 'test')
    DB_SCHEMA = credentials.get('schema', 'test')

    DB_CONNECTION_STRING = f"{DB_ENGINE}+{DB_DRIVER}://{DB_USER_NAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DB_DRIVER               = env("DB_DRIVER", None)
DB_NAME                 = env("DB_NAME", None)
DB_SCHEMA               = env("DB_SCHEMA", None)
DB_CONNECTION_STRING    = env("DB_CONNECTION_STRING", None)
DB_DEBUG_MODE           = env("DB_DEBUG_MODE", True)
DB_POOL_SIZE            = env("DB_POOL_SIZE", 20)
DB_MAX_OVERFLOW         = env("DB_MAX_OVERFLOW", 5)
DB_POOL_RECYCLE         = env("DB_POOL_RECYCLE", 3600)
DB_POOL_PRE_PING        = env("DB_POOL_PRE_PING", True)
DB_POOL_USE_LIFO        = env("DB_POOL_USE_LIFO", True)

if DB_CONNECTION_STRING is None:
    get_db_from_secrets()

config = {
    DB_DRIVER: {
        'url': DB_CONNECTION_STRING,
        'echo': DB_DEBUG_MODE,
        'pool_size': DB_POOL_SIZE,
        'max_overflow': DB_MAX_OVERFLOW,
        'pool_recycle': DB_POOL_RECYCLE,
        'pool_pre_ping': DB_POOL_PRE_PING,
        'pool_use_lifo': DB_POOL_USE_LIFO
    }
}