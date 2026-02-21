import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import os

pool = ThreadedConnectionPool(
    minconn=2, maxconn=10,
    host=os.environ["DB_HOST"],
    dbname=os.environ['DB_NAME'],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
)

def get_conn():
    return pool.getconn()

def release_conn(conn):
    pool.putconn(conn)