import sqlalchemy
from .db_session import SqlAlchemyBase


class Contacts(SqlAlchemyBase):

    __tablename__ = 'contacts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String)
    subject = sqlalchemy.Column(sqlalchemy.String)
    message = sqlalchemy.Column(sqlalchemy.String)