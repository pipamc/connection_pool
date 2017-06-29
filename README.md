Why need connection pool ?

Connection pool is a cache of database
connections maintained so that the connection
can be reused when future requests to the database
are required. Basically, any connection based on TCP
can be set into connection pool to reduce connection time.

How to use?
```
import pymysql
import pymysql.cursors

def get_connection(**kwargs):
    connection = pymysql.connect(
        host=kwargs["host"],
        user=kwargs["user"],
        password=kwargs["password"],
        db=kwargs["db"],
        charset=kwargs["charset"],
        cursorclass=pymysql.cursors.DictCursor)
    return connection

kwargs = dict()
kwargs["host"] = "127.0.0.1"
kwargs["user"] = "gaoxun"
kwargs["password"] = "gaoxun"
kwargs["db"] = "test"
kwargs["charset"] = "utf8"

connection_pool = ConnectionPool(get_connection, **kwargs)
with connection_pool.connection() as conn:
    cursor = conn.cursor()
    cursor.execute("select * from test")
    conn.commit()
```
