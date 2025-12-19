from typing import Literal
import duckdb
from pathlib import Path

class DuckDBConnector:
    def __init__(self, extension: Literal["SQLITE", "postgres", "mysql"]):
        self.con = duckdb.connect()
        self.extension = extension
        self.install_extension(self.extension)
        print(f"Installed and loaded {self.extension} extension.")
        return None

    def install_extension(self, extension: Literal["SQLITE", "postgres", "mysql"]):
        self.con.execute(f"INSTALL {extension};")
        self.con.execute(f"LOAD {extension};")
        return None

    def attach_mysql_database(self, connection_string: str):
        self.con.execute(f"ATTACH '{connection_string}' AS mysqldb (TYPE mysql);")
        self.con.execute("USE mysqldb;")
        print("Attached MYSQL database")
        return self.con

    def attach_sqlite_database(self, db_path: str) -> duckdb.DuckDBPyConnection:
        self.con.execute(f"ATTACH '{db_path}' (TYPE sqlite);")
        db_fname = Path(db_path).stem
        print(f"Will attempt to connect to {db_fname}")
        self.con.execute(f"USE {db_fname};")
        print(f"Attached database {db_path}")
        return self.con
