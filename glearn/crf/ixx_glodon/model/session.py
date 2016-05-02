# coding=utf-8
import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.config import config, ENV

if ENV == 'development':
    engine = create_engine(
        config.CONNECT_STRING,
        echo=config.DB_DEBUG
    )
else:
    engine = create_engine(
        config.CONNECT_STRING,
        echo=config.DB_DEBUG,
        pool_recycle=3600,
        pool_size=15
    )

Session = sessionmaker(bind=engine)


@contextlib.contextmanager
def get_session():
    """
    session 的 contextmanager， 用在with语句
    """
    session = Session()
    try:
        yield session
    except Exception as e:
        session.rollback()
        print 'CANT GET SESSION, ERROR: '
        print e
        raise
    finally:
        session.close()