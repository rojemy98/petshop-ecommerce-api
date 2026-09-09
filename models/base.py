from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


SCHEMA_NAME = "petshop_ecommerce"


class Base(DeclarativeBase):
    metadata = MetaData(schema=SCHEMA_NAME)