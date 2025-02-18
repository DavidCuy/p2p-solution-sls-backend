# -*- coding: utf-8 -*-
from core_db.base_model import BaseModel
from peewee import (SQL, AutoField, BigAutoField, BigIntegerField,
                    BooleanField, CharField, CompositeKey, DateField,
                    DateTimeField, DecimalField, DoubleField, ForeignKeyField,
                    IntegerField, TextField, UUIDField, SmallIntegerField)
from playhouse.postgres_ext import JSONField

UUID4 = "DEFAULT uuid_generate_v4()"
NOW = "DEFAULT now()"
DEFAULT_EMPTY = "DEFAULT ''::text"
SCHEMA = ""
UTC_NOW = "DEFAULT timezone('UTC'::text, now())"

__all__ = [
    "P2Ptransaction",
]


class P2Ptransaction(BaseModel):
    id = BigAutoField()
    source_id = BigIntegerField(null=False)
    dest_id = BigIntegerField(null=False)
    amount = DecimalField(null=False)
    status = TextField(null=False)
    created_at = DateTimeField()

    class Meta:
        table_name = "p2p_transaction"
        schema = "p2p_schema"

