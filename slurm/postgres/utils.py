from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import exc
from contextlib import contextmanager

Base = declarative_base()

def get_db_engine(pg_config):
    ''' Establishes connection '''
    s = open(pg_config, 'r').read()
    postgres_config = eval(s)

    DATABASE = {
        'drivername': 'postgres',
        'host' : 'pgreadwrite.osdc.io',
        'port' : '5432',
        'username': postgres_config['username'],
        'password' : postgres_config['password'],
        'database' : 'prod_bioinfo'
    }

    return __db_connect(DATABASE)

@contextmanager
def session_scope():
    """ Provide a transactional scope around a series of transactions """

    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def __db_connect(database):
    """performs database connection"""

    return create_engine(URL(**database))

def create_table(engine, tool):
    """ checks if a table for metrics exists and create one if it doesn't """

    inspector = Inspector.from_engine(engine)
    tables = set(inspector.get_table_names())
    if tool.__tablename__ not in tables:
        Base.metadata.create_all(engine)

def add_metrics(engine, met):
    """ add provided metrics to database """
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    #create table if not present
    create_table(engine, met)

    session.add(met)
    session.commit()
    session.expunge_all()
    session.close()
