# vim: tw=100 foldmethod=indent
import sqlite3

from addict import Dict

from alise.config import CONFIG
from alise.logsetup import logger


def dict_factory(cursor, row):
    """helper for json export from sqlite"""
    d = Dict()
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Base:
    SCHEMA = []
    site_name = ""

    def __init__(self):
        if not self.site_name:
            self.site_name = "root"
        self.dbfile = f"{CONFIG.database.db_name}_{self.get_site_name()}.db"
        self.initialise_db()

    def get_site_name(self):
        return self.site_name

    def initialise_db(self):
        try:
            con = sqlite3.connect(self.dbfile)
            cur = con.cursor()
            for s_entry in self.SCHEMA:
                cur.execute(s_entry)
                con.commit()
            cur.close()

        except sqlite3.OperationalError as e:
            logger.error("SQL Create error: %s", str(e))
            raise

    def _db_query(self, query, queryparams):
        try:
            con = sqlite3.connect(self.dbfile)
            con.row_factory = dict_factory
            cur = con.cursor()
            cur.execute(query, queryparams)
            rows = cur.fetchall()
            con.commit()
            cur.close()
            return rows

        except sqlite3.OperationalError as e:
            logger.error("SQL Create error: %s", str(e))
            raise


# # Never do this -- insecure!
# symbol = 'RHAT'
# c.execute("SELECT * FROM stocks WHERE symbol = '%s'" % symbol)
#
# # Do this instead
# t = ('RHAT',)
# c.execute('SELECT * FROM stocks WHERE symbol=?', t)
# print c.fetchone()
#
# # Larger example that inserts many records at a time
# purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
#              ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
#              ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
#             ]
# c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)
