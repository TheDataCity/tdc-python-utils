from pathlib import Path
from typing import Literal

import duckdb

# DuckDB cannot bind parameters in INSTALL, LOAD, ATTACH or USE, so these statements put the
# caller's value into the SQL text. Each one turns off only the two semgrep rules that ask for
# a parameterized query.


class DuckDBConnector:
    def __init__(self, extension: Literal["SQLITE", "postgres", "mysql"]):
        self.con = duckdb.connect()
        self.extension = extension
        self.install_extension(self.extension)
        print(f"Installed and loaded {self.extension} extension.")

    def install_extension(self, extension: Literal["SQLITE", "postgres", "mysql"]):
        # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query, python.lang.security.audit.formatted-sql-query.formatted-sql-query
        self.con.execute(f"INSTALL {extension};")
        # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query, python.lang.security.audit.formatted-sql-query.formatted-sql-query
        self.con.execute(f"LOAD {extension};")

    def attach_mysql_database(self, connection_string: str):
        # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query, python.lang.security.audit.formatted-sql-query.formatted-sql-query
        self.con.execute(f"ATTACH '{connection_string}' AS mysqldb (TYPE mysql);")
        self.con.execute("USE mysqldb;")
        print("Attached MYSQL database")
        return self.con

    def attach_sqlite_database(self, db_path: str) -> duckdb.DuckDBPyConnection:
        # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query, python.lang.security.audit.formatted-sql-query.formatted-sql-query
        self.con.execute(f"ATTACH '{db_path}' (TYPE sqlite);")
        db_fname = Path(db_path).stem
        print(f"Will attempt to connect to {db_fname}")
        # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query, python.lang.security.audit.formatted-sql-query.formatted-sql-query
        self.con.execute(f"USE {db_fname};")
        print(f"Attached database {db_path}")
        return self.con
