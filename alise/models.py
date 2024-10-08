# vim: tw=100 foldmethod=indent
# pylint: disable = logging-fstring-interpolation
import sqlite3
import json
import time
from addict import Dict

from alise import exceptions
from alise.database import Base
from alise.logsetup import logger


class LastPage(Base):
    SCHEMA = ["""create table if not exists lastpage (session TEXT, url TEXT)"""]

    def store(self, session, url):
        try:
            con = sqlite3.connect(self.dbfile)
            cur = con.cursor()

            cur.execute(
                "INSERT OR REPLACE into lastpage values(?, ?) ",
                # (session, url.__str__()),
                (session, str(url)),
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

            res = cur.execute("SELECT url FROM lastpage where session=? ", [session]).fetchall()
            con.commit()
            cur.close()
            return res

        except sqlite3.OperationalError as e:
            logger.error("SQL insert error: %s", str(e))
            raise


class DatabaseUser(Base):
    SCHEMA = [
        "CREATE table if not exists int_user (session_id TEXT, identity TEXT, provider TEXT, jsonstr JSON, last_seen INTEGER)",
        "CREATE table if not exists ext_user (session_id TEXT, identity TEXT, provider TEXT, jsonstr JSON, last_seen INTEGER)",
        "CREATE table if not exists sites (name TEXT, comment TEXT)",
        "CREATE table if not exists apikeys (ownername TEXT, owneremail TEXT, sub TEXT, iss TEXT, apikey TEXT)",
    ]

    # alter table ext_user add column last_seen INTEGER;

    def __init__(self, site_name):
        self.site_name = site_name
        super().__init__()

        # each identity consists of
        # - jsondata (= request.user)
        self.int_id = Dict()
        self.ext_ids = []
        self.session_id = ""

    def store_internal_user(self, jsondata, session_id):
        self.int_id = jsondata
        if not self._is_user_in_db(self.int_id.identity, "int"):
            self.store_user(self.int_id, "int", session_id)
        else:
            # FIXME: update the user!!
            logger.info("not storing user, UPDATING")
            self.update_user(self.int_id, "int")

    def store_external_user(self, jsondata, session_id):
        self.ext_ids.append(Dict())
        self.ext_ids[-1] = jsondata
        if not self._is_user_in_db(self.ext_ids[-1].identity, "ext"):
            self.store_user(self.ext_ids[-1], "ext", session_id)
        else:
            # FIXME: update the user!!
            logger.info("not storing user, UPDATING")
            self.update_user(self.ext_ids[-1], "ext")

    def store_user(self, jsondata, location, session_id):
        try:
            # identity = jsondata.identity.__str__()
            identity = str(jsondata.identity)
            jsonstr = json.dumps(jsondata, sort_keys=True, indent=4)
        except AttributeError as e:
            logger.error(f"cannot find attribute:   {e}")
            logger.error(json.dumps(jsondata, sort_keys=True, indent=4))
            raise

        logger.debug(f" ----------> provider: {jsondata.provider}")
        epoch_time_now = int(time.time())
        self._db_query(
            f"INSERT OR REPLACE into {location}_user values(?, ?, ?, ?, ?)",
            (
                session_id,
                identity,
                jsondata.provider,
                jsonstr,
                epoch_time_now,
            ),
        )

    def update_user(self, jsondata, location):
        try:
            # identity = jsondata.identity.__str__()
            identity = str(jsondata.identity)
            jsonstr = json.dumps(jsondata, sort_keys=True, indent=4)
        except AttributeError as e:
            logger.error(f"cannot find attribute:   {e}")
            logger.error(json.dumps(jsondata, sort_keys=True, indent=4))
            raise

        epoch_time_now = int(time.time())
        self._db_query(
            f"UPDATE {location}_user set jsonstr = ?, last_seen = ? WHERE identity=?",
            (jsonstr, epoch_time_now, identity),
        )

    def delete_external_user(self, identity, provider):
        logger.info(f"deleting linkage to {provider} for {identity}")
        location = "ext"
        self._db_query(
            f"DELETE FROM {location}_user WHERE identity=? AND provider=?",
            (identity, provider),
        )
        logger.info(
            f"delete by:    DELETE FROM {location}_user WHERE identity={identity} AND provider={provider}"
        )

    def get_identity_by_session_id(self, session_id, provider, location="ext"):
        short_location = location[0:3]
        # logger.debug(f"returning session_id for user {identity}")

        res = self._db_query(
            f"SELECT * from {short_location}_user WHERE session_id=? and provider=?",
            (session_id, provider),
        )

        if len(res) > 1:
            message = "found more than one result for query"
            logger.error(message)
            raise exceptions.InternalException(message)
        if len(res) == 0:
            message = "found no result for query"
            logger.error(message)
            raise exceptions.InternalException(message)
        # logger.debug(rv)
        return res[-1].identity

    def get_session_id_by_user_id(self, identity, location=""):
        if not location:
            rv = self.get_user(identity, db_key="identity", location="ext")
            if not rv:
                rv = self.get_user(identity, db_key="identity", location="int")
        else:
            short_location = location[0:3]
            rv = self.get_user(identity, db_key="identity", location=short_location)

        return rv.session_id

    # def get_session_id_by_internal_user_id(self, identity):
    #     logger.debug(f"returning session_id for user {identity}")
    #     rv = self.get_user(identity, db_key="identity", location="int")
    #     # logger.debug(rv)
    #     return  rv.sesion_id

    def load_all_identities(self, session_id):
        self.int_id = self.get_user(session_id, "session_id", "int")
        self.ext_ids = self.get_users(session_id, "session_id", "ext")
        # logger.debug(F"self.int_id: {self.int_id}")

    def get_internal_user(self, identity):
        return self.get_user(identity, db_key="identity", location="int")

    def get_external_user(self, identity):
        return self.get_users(identity, db_key="identity", location="ext")

    def get_user(self, value, db_key, location):
        rv = self.get_users(value, db_key, location)[-1]
        return rv

    def get_users(self, value, db_key, location):
        # logger.debug(f"db_key: {db_key}")
        keys = ["session_id", "identity", "jsonstr", "last_seen"]
        if db_key not in keys:
            message = "Key not found in internal database"
            logger.error(message)
            raise exceptions.InternalException(message)
        # logger.debug(f"DB QUERY: SELECT * from {location}_user WHERE {db_key}={value}")
        res = self._db_query(f"SELECT * from {location}_user WHERE {db_key}=?", [value])
        if len(res) == 0:
            return Dict()
        # logger.debug(f"length of results: {len(res)} - {location}")
        rv = []
        for r in res:
            rv.append(Dict())
            for k in keys:
                rv[-1][k] = r[k]
            rv[-1].jsondata = Dict(json.loads(rv[-1].jsonstr))
            del rv[-1].jsonstr
        return rv

    def _is_user_in_db(self, identity, location):
        rv = self.get_users(identity, db_key="identity", location=location)
        if len(rv) < 1:
            logger.debug(f"Could not find user {identity} in db")
            return False
        logger.debug(f"found user {identity} in db")
        return True

    def get_int_id(self):
        return self.int_id.identity

    ####### API KEY stuff ##########
    def store_apikey(
        self,
        user_name: str | None,
        user_email: str | None,
        sub: str | None,
        iss: str | None,
        apikey: str | None,
    ):
        self._db_query(
            "INSERT OR REPLACE into apikeys VALUES(?, ?, ?, ?, ?)",
            (
                user_name,
                user_email,
                sub,
                iss,
                apikey,
            ),
        )

    def apikey_valid(self, apikey: str) -> bool:
        res = self._db_query("SELECT * from apikeys WHERE apikey=?", [apikey])
        if len(res) < 1:
            return False
        return True
