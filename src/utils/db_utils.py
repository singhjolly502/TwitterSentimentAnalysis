"""This module contains utilities related to Database operations"""
import pandas as pd
from sqlalchemy import create_engine


def get_engine(db_config):
    """Connect to Database and get Engine"""
    db_type, db_driver, db_user = db_config['db_type'], db_config['db_driver'], db_config['db_user']
    db_pass, db_host, db_port = db_config['db_pass'], db_config['db_host'], int(db_config['db_port'])
    db_name, pool_size = db_config['db_name'], int(db_config['pool_size'])

    sqlalchemy_database_uri = f"{db_type}+{db_driver}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    # sqlalchemy_database_uri = '%s+%s://%s:%s@%s:%s/%s' % (db_type, db_driver, db_user,
    #                                                       db_pass, db_host, db_port, db_name)
    engine = create_engine(sqlalchemy_database_uri, pool_size=pool_size, max_overflow=0)
    return engine


def clean_df_db_dups(df, tablename, engine, dup_cols=[],
                     filter_continuous_col=None, filter_categorical_col=None):
    """
    Remove rows from a dataframe that already exist in a utils
    Required:
        df : dataframe to remove duplicate rows from
        engine: SQLAlchemy engine object
        tablename: tablename to check duplicates in
        dup_cols: list or tuple of column names to check for duplicate row values
    Optional:
        filter_continuous_col: the name of the continuous data column for
        BETWEEEN min/max filter can be either a datetime, int,
        or float data type useful for restricting the utils table size
        to check
        filter_categorical_col : the name of the categorical data column for
        Where = value check Creates an "IN ()" check on the unique values in
        this column
    Returns
        Unique list of values from dataframe compared to utils table
    """
    args = 'SELECT %s FROM %s' % (', '.join(['"{0}"'.format(col) for col in dup_cols]), tablename)
    args_contin_filter, args_cat_filter = None, None
    if filter_continuous_col is not None:
        if df[filter_continuous_col].dtype == 'datetime64[ns]':
            args_contin_filter = """ "%s" BETWEEN Convert(datetime, '%s')
            AND Convert(datetime, '%s')""" % (filter_continuous_col,
                                              df[filter_continuous_col].min(),
                                              df[filter_continuous_col].max())

    if filter_categorical_col is not None:
        args_cat_filter = ' "%s" in(%s)' % (filter_categorical_col, ', '.join(["'{0}'".format(value) for value in
                                                                               df[filter_categorical_col].unique()]))

    if args_contin_filter and args_cat_filter:
        args += ' Where ' + args_contin_filter + ' AND' + args_cat_filter
    elif args_contin_filter:
        args += ' Where ' + args_contin_filter
    elif args_cat_filter:
        args += ' Where ' + args_cat_filter

    df.drop_duplicates(dup_cols, keep='first', inplace=True)
    df_db = pd.read_sql(args, engine)
    print(f"Data Fetched from DB: {df_db.dtypes}")
    print(f"Original Data: {df.dtypes}")
    df = pd.merge(df, df_db, how='left', on=dup_cols, indicator=True)
    df = df[df['_merge'] == 'left_only']
    df.drop(['_merge'], axis=1, inplace=True)
    return df


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
    positive BIGINT,
    wpositive BIGINT,
    spositive BIGINT,
    negative BIGINT,
    wnegative BIGINT,
    snegative BIGINT,
    neutral BIGINT,
    keyword VARCHAR(200),
    n_tweets BIGINT)
    """)
