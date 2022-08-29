"""This module contains utilities related to Database operations"""
from sqlalchemy import create_engine


def get_engine(db_config):
    """Connect to Database and get Engine"""
    db_type, db_driver, db_user = db_config['db_type'], db_config['db_driver'], db_config['db_user']
    db_pass, db_host, db_port = db_config['db_pass'], db_config['db_host'], int(db_config['db_port'])
    db_name, pool_size = db_config['db_name'], int(db_config['pool_size'])

    sqlalchemy_database_uri = f"{db_type}+{db_driver}://{db_user}:{db_pass}@{db_host}/{db_name}"
    # "postgresql+psycopg2://root:root@localhost:5432/sentiment_tweets"
    # sqlalchemy_database_uri = '%s+%s://%s:%s@%s:%s/%s' % (db_type, db_driver, db_user,
    #                                                       db_pass, db_host, db_port, db_name)
    engine = create_engine(sqlalchemy_database_uri, pool_size=pool_size, max_overflow=0)
    return engine


def setup(engine, db_config):
    """
    Creates the required tables
    :param engine: SQLALCHEMY Engine
    :param db_config: DB Configuration File
    :return:
    """

    # engine.execute("""DROP TABLE IF EXISTS "%s" """ % (bc3_tablename))
    # engine.execute("""DROP TABLE IF EXISTS "%s" """ % (bc2_tablename))
    users_table = db_config['users_table']
    tweets_table = db_config['tweets_table']
    statistics_table = db_config['statistics_table']
    engine.execute(f"""CREATE TABLE IF NOT EXISTS {users_table} 
    ( name VARCHAR(10) NOT NULL,
    email VARCHAR(255) PRIMARY KEY,
    password VARCHAR(20) NOT NULL
    )
    """)

    engine.execute(f"""CREATE TABLE IF NOT EXISTS {tweets_table}
    ( tweet_id BIGINT,
    text TEXT,
    clean_text TEXT,
    tweet_time VARCHAR(50),
    polarity FLOAT,
    keyword VARCHAR(200))
    """)

    engine.execute(f"""CREATE TABLE IF NOT EXISTS {statistics_table}
    ( polarity FLOAT,
    total_polarity VARCHAR(50),
    positive FLOAT,
    wpositive FLOAT,
    spositive FLOAT,
    negative FLOAT,
    wnegative FLOAT,
    snegative FLOAT,
    neutral FLOAT,
    keyword VARCHAR(200),
    n_tweets BIGINT)
    """)
