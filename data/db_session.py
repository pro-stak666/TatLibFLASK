import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(user_name, user_password, host, port, db_name):
    global __factory

    if __factory:
        return

    engine = sa.create_engine(f'postgresql+psycopg2://{user_name}:{user_password}@{host}:{port}/{db_name}', echo=False)
    __factory = orm.sessionmaker(bind=engine)

    if not database_exists(engine.url):
        create_database(engine.url)
        print('db is created')

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()