import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .db_session import SqlAlchemyBase


# users_to_books = sqlalchemy.Table(
#     'users_to_books',
#     SqlAlchemyBase.metadata,
#     sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
#     sqlalchemy.Column('book_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('books.id'))
# )

# users_to_words = sqlalchemy.Table(
#     'users_to_words',
#     SqlAlchemyBase.metadata,
#     sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
#     sqlalchemy.Column('word_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('words.id')),
#     sqlalchemy.Column('word_level', sqlalchemy.Integer, nullable=False),
#     sqlalchemy.Column('next_date_training', sqlalchemy.DateTime, default=datetime.datetime.now)
# )


class Users_to_words(SqlAlchemyBase):
    __tablename__ = 'users_to_words'
    user_id = sqlalchemy.Column(sqlalchemy.ForeignKey('users.id'))
    word_id = sqlalchemy.Column(sqlalchemy.ForeignKey('words.id'))
    sqlalchemy.PrimaryKeyConstraint(user_id, word_id)
    word_level = sqlalchemy.Column('word_level', sqlalchemy.Integer, nullable=False, default=0)
    next_date_training = sqlalchemy.Column('next_date_training', sqlalchemy.DateTime, default=datetime.datetime.now)

    user = orm.relationship('Users', back_populates='words')
    word = orm.relationship('Words', back_populates='users')


class Users_to_books(SqlAlchemyBase):
    __tablename__ = 'users_to_books'
    user_id = sqlalchemy.Column(sqlalchemy.ForeignKey('users.id'))
    book_id = sqlalchemy.Column(sqlalchemy.ForeignKey('books.id'))
    sqlalchemy.PrimaryKeyConstraint(user_id, book_id)

    user = orm.relationship('Users', back_populates='books')
    book = orm.relationship('Books', back_populates='users')


class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False, unique=True)
    email = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False, unique=True)
    tg_username = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True, unique=True)
    tg_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    creation_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    books = orm.relationship('Users_to_books', back_populates='user')
    words = orm.relationship('Users_to_words', back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Books(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "books"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    difficult_level = sqlalchemy.Column(sqlalchemy.VARCHAR(6), nullable=False)

    users = orm.relationship('Users_to_books', back_populates='book')


class Words(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "words"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word_tat = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False, unique=True)
    word_ru = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False, unique=True)

    users = orm.relationship('Users_to_words', back_populates='word')


class Questions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "questions"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False, unique=True)


class Possible_answers(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "possibles_answers"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('questions.id'), nullable=False)
    answer = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    is_correct_answer = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)