# vim: tw=100 foldmethod=indent
import sqlite3
import json
from addict import Dict

from alise.database import Base
from alise.logsetup import logger

# vega_db = VegaUsers()


class LastPage(Base):
    SCHEMA = ["""create table if not exists lastpage (session TEXT, url TEXT)"""]

    def store(self, session, url):
        try:
            con = sqlite3.connect(self.dbfile)
            cur = con.cursor()

            cur.execute(
                "INSERT OR REPLACE into lastpage values(?, ?) ",
                (session, url.__str__()),
            )
            con.commit()
            cur.close()
        except sqlite3.OperationalError as e:
            logger.error("SQL insert error: %s", str(e))
            raise

    def get(self, session):
        try:
            con = sqlite3.connect(self.dbfile)
            cur = con.cursor()

            res = cur.execute(
                "SELECT url FROM lastpage where session=? ", [session]
            ).fetchall()
            con.commit()
            cur.close()
            return res

        except sqlite3.OperationalError as e:
            logger.error("SQL insert error: %s", str(e))
            raise


class DatabaseUser(Base):
    SCHEMA = [
        "CREATE table if not exists int_user (identity TEXT, display_name TEXT, jsonstr JSON, site_name TEXT)",
        "CREATE table if not exists ext_user (identity TEXT, display_name TEXT, jsonstr JSON, site_name TEXT)",
        "CREATE table if not exists sites (name TEXT, comment TEXT)",
    ]

    def __init__(self, site_name):
        self.site_name = site_name
        super().__init__()

    def store_internal_user(self, jsondata):
        if not self._is_user_in_db(jsondata.identity, "int"):
            self.store_user(jsondata, "int")

    def store_external_user(self, jsondata):
        if not self._is_user_in_db(jsondata.identity, "ext"):
            self.store_user(jsondata, "ext")

    def store_user(self, jsondata, location):
        try:
            self.identity = jsondata.identity
            self.jsondata = jsondata
            self.jsonstr = json.dumps(self.jsondata, sort_keys=True, indent=4)
        except AttributeError as e:
            logger.error(f"cannot find attribute:   {e}")
            logger.error(json.dumps(jsondata, sort_keys=True, indent=4))

        try:
            display_name = json.loads(self.jsonstr)["display_name"]
        except KeyError:
            display_name = "None"

        self._db_query(
            f"INSERT OR REPLACE into {location}_user values(?, ?, ?, ?) ",
            (
                self.identity,
                display_name,
                self.jsonstr,
                self.site_name,
            ),
        )
    def get_internal_user(self, identity):
        return self.get_user(identity, "int")

    def get_external_user(self, identity):
        return self.get_user(identity, "ext")

    def get_user(self, identity, location):
        res = self._db_query(f"SELECT * from {location}_user WHERE identity=?", [identity])
        if len(res) == 0:
            return Dict()
        keys = ["identity", "display_name", "jsonstr", "site_name"]
        rv = Dict()
        for k in keys:
            # logger.debug(F"key: {k}: {res[0][k]}")
            setattr(self, k, res[-1][k])
            rv[k] = res[-1][k]
        self.jsondata = json.loads(self.jsonstr)
        rv.jsondata = json.loads(rv.jsonstr)
        return rv

    def _is_user_in_db(self, identity, location):
        rv = self.get_user(identity, location)
        if len(rv) != 0:
            return True
        return False
