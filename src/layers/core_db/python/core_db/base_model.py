# -*- coding: utf-8 -*-
import uuid
from collections import namedtuple
from typing import Union

from db_utils.params import ParametersDBB2C
from db_utils.app_params import ParametersAppB2C

from peewee import (
    Model,
    PostgresqlDatabase,
    SelectBase,
    _ModelWriteQueryHelper,
    _WriteQuery,
    database_required,
    fn,
)
from psycopg2 import extensions

__all__ = ["BaseModel", "database"]

PARAMETER_DB = ParametersDBB2C()
PARAMETER_APP = ParametersAppB2C()

if not PARAMETER_APP.developer and not PARAMETER_APP.lambda_name:
    raise KeyError('Please define the environment variable "DEVELOPER" with your name.')

NAME_CONNECTION = f"{PARAMETER_APP.developer or PARAMETER_APP.lambda_name}"

DB_NAME = PARAMETER_DB.name
DB_USER = PARAMETER_DB.user
DB_HOST = PARAMETER_DB.host
DB_PORT = PARAMETER_DB.port
DB_PASSWORD = PARAMETER_DB.password

if PARAMETER_APP.developer == "DeployUnittest":
    database = PostgresqlDatabase(
        DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        isolation_level=extensions.ISOLATION_LEVEL_READ_UNCOMMITTED,
        autorollback=True,
        application_name=NAME_CONNECTION
    )
else:
    database = PostgresqlDatabase(
        DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, application_name=NAME_CONNECTION
    )

DEFAULT_FALSE = "DEFAULT false"
DEFAULT_NULL = "DEFAULT NULL::numeric"
DEFAULT_DATE = "DEFAULT ('now'::text)::date"
DEFAULT_TIMEZONE = "DEFAULT timezone('America/Los_angeles'::text, (now())::timestamp(0) without time zone)"


class UnknownField(object):
    def __init__(self, *_, **__):
        # Not used
        pass


@database_required
def get_all(self, database):
    self._cursor_wrapper = None
    try:
        return self.execute(database)[:None]
    except IndexError:
        pass


@database_required
def single_object(self, database):
    self._cursor_wrapper = None
    try:
        result = self.execute(database)[0]
        return namedtuple(f"single_object{uuid.uuid4().hex}", result.keys())(
            *result.values()
        )
    except IndexError:
        raise self.DoesNotExist()


setattr(SelectBase, "get_all", get_all)
setattr(SelectBase, "single_object", single_object)


class BaseModel(Model):
    @classmethod
    def exclude_fields(cls, fields: Union[list, tuple]):
        return [f for f in cls._meta.sorted_fields if f.name not in fields]

    @classmethod
    def only_this_fields(cls, fields: Union[list, tuple]):
        return [f for f in cls._meta.sorted_fields if f.name in fields]

    @classmethod
    def model_to_Sql_Json(cls, fields: Union[list, tuple], alias="", aditionals=None):
        columns = [[f.name, f] for f in cls._meta.sorted_fields if f.name not in fields]

        if aditionals:
            for a in aditionals:
                columns.append(a)

        column = fn.jsonb_build_object(*[num for elem in columns for num in elem])
        if alias:
            column = column.alias(alias)
        return column

    @classmethod
    def table_import_from_s3(cls, bucket_from_event, s3_key, region, fields):
        if not fields:
            fields = cls._meta.sorted_fields
        return ModelTableImport(cls, bucket_from_event, s3_key, region, fields)

    @classmethod
    def next_val(cls, sequence: str):
        return next(
            database.execute_sql("SELECT (nextval( %s ));", params=(sequence,))
        )[0]

    class Meta:
        database = database


class TableImport(_WriteQuery):
    class DefaultValuesException(Exception):
        pass

    def __init__(self, table, columns=None, **kwargs):
        self._columns = columns
        super(TableImport, self).__init__(table, **kwargs)

    def __sql__(self, ctx):
        fields = " , ".join([f for f in self.fields])
        super(TableImport, self).__sql__(ctx)
        ctx.literal("select aws_s3.table_import_from_s3")
        ctx.literal(f"('{self.model._meta.schema}.{self.model._meta.table_name}',")
        ctx.literal(f"'{fields}',")
        ctx.literal("'(format csv , HEADER true)',")
        ctx.literal(
            f"aws_commons.create_s3_uri('{self.bucket}', '{self.s3_key}', '{self.region}'))"
        )

        return ctx

    def _execute(self, database):
        try:
            return super(TableImport, self)._execute(database)
        except self.DefaultValuesException:
            pass


class ModelTableImport(_ModelWriteQueryHelper, TableImport):
    def __init__(self, model, bucket, s3_key, region, fields, *args, **kwargs):
        self.bucket = bucket
        self.s3_key = s3_key
        self.region = region
        self.fields = fields

        super(ModelTableImport, self).__init__(model, *args, **kwargs)
