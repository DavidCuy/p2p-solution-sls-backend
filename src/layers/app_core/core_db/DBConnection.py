import json
import decimal
import datetime
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.session import Session as ORMSession

from .config import config, DB_DRIVER

## Database connection string
engine = None
session = None

DB_CONFIG = config[DB_DRIVER]

def get_session() -> ORMSession:
    """ Return a new database session from engine to data access

    Returns:
        ORMSession: Database session
    """
    global session
    if not session:
        session = sessionmaker(get_engine())
    return session(expire_on_commit=False)

def get_engine() -> Engine:
    """ Return the database engine

    Returns:
        Engine: Database Engines
    """
    global engine
    if not engine:
        engine = create_engine(**DB_CONFIG)
    return engine


class AlchemyEncoder(json.JSONEncoder):
    """ Based on: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json/41204271 """
    def default(self, obj):
        if issubclass(obj.__class__, DeclarativeBase):
            fields = {}
            prop_map_obj = obj.__class__.property_map()
            for field in [x for x in obj.attrs]:
                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, (datetime.datetime, datetime.date, datetime.time)):
                        data = data.isoformat()
                    else:
                        json.dumps(data)
                    fields[prop_map_obj[field] if field in prop_map_obj else field] = data
                except TypeError:
                    fields[field] = None
            return fields
        if isinstance(obj, decimal.Decimal):
            if obj % 1 > 0:
                return float(obj)
            else:
                return int(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class AlchemyRelationEncoder(json.JSONEncoder):
    def __init__(self, relationships: List[str], **kwargs) -> None:
        super().__init__(**kwargs)
        self.relationships = relationships
        
    """ Based on: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json/41204271 """
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeBase):
            fields = {}
            prop_map_obj = obj.__class__.property_map()
            
            relation_names = [attr for attr, relation in obj.__mapper__.relationships.items()]
            filters_model = list(set(self.relationships).intersection(relation_names))
            attributes = [x for x in obj.attrs]
            
            if type(filters_model) is list:
                attributes.extend(filters_model)
            
            for field in attributes:
                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, (datetime.datetime, datetime.date, datetime.time)):
                        data = data.isoformat()
                    else:
                        json.dumps(data, cls=self.__class__, check_circular=self.check_circular, relationships=self.relationships)
                    fields[prop_map_obj[field] if field in prop_map_obj else field] = data
                except TypeError as e:
                    fields[field] = None
            return fields
        if isinstance(obj, decimal.Decimal):
            if obj % 1 > 0:
                return float(obj)
            else:
                return int(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

