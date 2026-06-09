import mysql.connector
import json
import os


class DatabaseManager:

    def __init__(
        self,
        json_file="interlock.json",
        section="Traceability Server"
    ):

        self.json_file = json_file
        self.section = section

        self.host = ""
        self.database = ""
        self.user = ""
        self.password = ""
        self.ssl_mode = "REQUIRED"

        self.conn = None

        self.load_config()

    # =====================================================
    # LOAD CONFIG FROM JSON
    # =====================================================
    def load_config(self):

        try:

            json_path = os.path.join(
                os.path.dirname(__file__),
                self.json_file
            )

            with open(
                json_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            db = data.get(
                self.section,
                {}
            )

            self.host = db.get(
                "Database Server",
                "127.0.0.1"
            )

            self.database = db.get(
                "TraceabilityCatalog",
                ""
            )

            self.user = db.get(
                "TraceabilityUserId",
                "root"
            )

            self.password = db.get(
                "TraceabilityPassword",
                ""
            )

            self.ssl_mode = db.get(
                "TraceabilitySslMode",
                "REQUIRED"
            )

            print(
                f"Database Config Loaded : "
                f"{self.host} | "
                f"{self.database} | "
                f"{self.user}"
            )

        except Exception as e:

            print(
                "Database Config Error :",
                e
            )

    # =====================================================
    # CONNECT
    # =====================================================
    def connect(self):

        try:

            self.load_config()

            if (
                self.conn
                and
                self.conn.is_connected()
            ):
                return True

            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                connection_timeout=5
            )

            print(
                f"Database Connected : "
                f"{self.host}"
            )

            return True

        except Exception as e:

            print(
                "Database Connect Error :",
                e
            )

            self.conn = None

            return False

    # =====================================================
    # RELOAD CONFIG + RECONNECT
    # =====================================================
    def reload(self):

        try:

            self.disconnect()

            self.load_config()

            return self.connect()

        except Exception as e:

            print(
                "Database Reload Error :",
                e
            )

            return False

    # =====================================================
    # DISCONNECT
    # =====================================================
    def disconnect(self):

        try:

            if (
                self.conn
                and
                self.conn.is_connected()
            ):

                self.conn.close()

                print(
                    "Database Disconnected"
                )

        except:
            pass

    # =====================================================
    # STATUS
    # =====================================================
    def is_connected(self):

        try:

            return (
                self.conn is not None
                and
                self.conn.is_connected()
            )

        except:

            return False

    # =====================================================
    # EXECUTE
    # =====================================================
    def execute(
        self,
        sql,
        params=None
    ):

        try:

            if not self.is_connected():
                self.connect()

            cursor = self.conn.cursor()

            cursor.execute(
                sql,
                params or ()
            )

            self.conn.commit()

            affected_rows = cursor.rowcount

            cursor.close()

            return affected_rows

        except Exception as e:

            print(
                "Execute Error :",
                e
            )

            return 0

    # =====================================================
    # FETCH ONE
    # =====================================================
    def fetch_one(
        self,
        sql,
        params=None
    ):

        try:

            if not self.is_connected():
                self.connect()

            cursor = self.conn.cursor(
                dictionary=True
            )

            cursor.execute(
                sql,
                params or ()
            )

            result = cursor.fetchone()

            cursor.close()

            return result

        except Exception as e:

            print(
                "Fetch One Error :",
                e
            )

            return None

    # =====================================================
    # FETCH ALL
    # =====================================================
    def fetch_all(
        self,
        sql,
        params=None
    ):

        try:

            if not self.is_connected():
                self.connect()

            cursor = self.conn.cursor(
                dictionary=True
            )

            cursor.execute(
                sql,
                params or ()
            )

            result = cursor.fetchall()

            cursor.close()

            return result

        except Exception as e:

            print(
                "Fetch All Error :",
                e
            )

            return []

    # =====================================================
    # SCALAR
    # =====================================================
    def scalar(
        self,
        sql,
        params=None
    ):

        try:

            if not self.is_connected():
                self.connect()

            cursor = self.conn.cursor()

            cursor.execute(
                sql,
                params or ()
            )

            result = cursor.fetchone()

            cursor.close()

            if result:
                return result[0]

            return None

        except Exception as e:

            print(
                "Scalar Error :",
                e
            )

            return None

    # =====================================================
    # GET DATABASE NAME
    # =====================================================
    def get_database_name(self):

        return self.database

    # =====================================================
    # GET HOST
    # =====================================================
    def get_host(self):

        return self.host

    # =====================================================
    # TEST CONNECTION
    # =====================================================
    def test_connection(self):

        try:

            temp_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                connection_timeout=5
            )

            temp_conn.close()

            return True

        except:

            return False