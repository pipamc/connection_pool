# coding: utf-8

# system packages
import logging
import threading
from collections import deque
import contextlib

# third-party packages

# own packages


logger = logging.getLogger("connection_pool")


class PoolIsFullException(Exception):
    pass


class PoolIsEmptyException(Exception):
    pass


class ConnectionPool(object):
    """
    it's a pool manager with thread safe locks
    """

    def __init__(self, create_factory, initial_connections=1,
                 max_connections=10, **kwargs):
        self._pool_lock = threading.RLock()
        self._free_items = deque(max_connections)
        self._used_items = deque(max_connections)
        self._max_connections = max_connections
        self._create_factory = create_factory
        self._kwargs = kwargs
        self._initialize(initial_connections)

    def _initialize(self, initial_connections):
        with self._pool_lock:
            for i in range(initial_connections):
                self._free_items.append(self._create_factory(**self._kwargs))

    def __repr__(self):
        return '<{0.__class__.__name__}> {0.size}>'.format(self)

    def __iter__(self):
        with self._pool_lock:
            return iter(self._free_items)

    def __len__(self):
        with self._pool_lock:
            return len(self._free_items) + len(self._used_items)

    @contextlib.contextmanager
    def connection(self):
        conn = self._acquire()
        try:
            yield conn
        finally:
            self._release(conn)

    @property
    def size(self):
        return len(self)

    def _acquire(self):
        with self._pool_lock:
            if len(self._free_items):
                conn = self._free_items.popleft()
                self._used_items.append(conn)
                return conn
            else:
                if len(self) < self._max_connections:
                    conn = self._create_factory(**self._kwargs)
                    self._used_items.append(conn)
                    return conn
                else:
                    raise PoolIsFullException()

    def _release(self, conn):
        with self._pool_lock:
            self._used_items.remove(conn)
            self._free_items.append(conn)


if __name__ == "__main__":
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
