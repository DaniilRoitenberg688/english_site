import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Module(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Words'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    teacher = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    words = sqlalchemy.Column(sqlalchemy.String, nullable=True)
