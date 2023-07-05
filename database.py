import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_ethnicities(conn):
    """ insert initial values into the Ethnicities table """
    try:
        c = conn.cursor()
        c.executemany('INSERT INTO Ethnicities (ethnicity) VALUES (?)', [('Black',), ('White',), ('Latino',)])
        conn.commit()
    except Error as e:
        print(e)

def insert_session_types(conn):
    """ insert initial values into the SessionTypes table """
    try:
        c = conn.cursor()
        c.executemany('INSERT INTO SessionTypes (session_type) VALUES (?)', [('Video',), ('AR',), ('VR',)])
        conn.commit()
    except Error as e:
        print(e)

def main():
    database = r"sqlite/training.db"

    sql_create_sessiontypes_table = """ CREATE TABLE IF NOT EXISTS SessionTypes (
                                        session_type_id INTEGER PRIMARY KEY,
                                        session_type TEXT
                                    ); """

    sql_create_ethnicities_table = """CREATE TABLE IF NOT EXISTS Ethnicities (
                                        ethnicity_id INTEGER PRIMARY KEY,
                                        ethnicity TEXT
                                    );"""

    sql_create_sessions_table = """CREATE TABLE IF NOT EXISTS Sessions (
                                    session_id INTEGER PRIMARY KEY,
                                    session_timestamp TIMESTAMP,
                                    session_type_id INTEGER,
                                    session_status TEXT CHECK(session_status IN ('active', 'inactive')),
                                    ethnicity_id INTEGER,
                                    FOREIGN KEY(session_type_id) REFERENCES SessionTypes(session_type_id),
                                    FOREIGN KEY(ethnicity_id) REFERENCES Ethnicities(ethnicity_id)
                                );"""

    sql_create_trainees_table = """CREATE TABLE IF NOT EXISTS Trainees (
                                    trainee_id TEXT PRIMARY KEY
                                );"""

    sql_create_session_trainees_table = """CREATE TABLE IF NOT EXISTS Session_Trainees (
                                                session_id INTEGER,
                                                trainee_id TEXT,
                                                intervention_t TIME,
                                                feedback TEXT,
                                                FOREIGN KEY(session_id) REFERENCES Sessions(session_id),
                                                FOREIGN KEY(trainee_id) REFERENCES Trainees(trainee_id)
                                            );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create sessiontypes table
        create_table(conn, sql_create_sessiontypes_table)

        # create ethnicities table
        create_table(conn, sql_create_ethnicities_table)

        # create sessions table
        create_table(conn, sql_create_sessions_table)

        # create trainees table
        create_table(conn, sql_create_trainees_table)

        # create session_trainees table
        create_table(conn, sql_create_session_trainees_table)

        # insert initial values into the Ethnicities table
        insert_ethnicities(conn)

        # insert initial values into the SessionTypes table
        insert_session_types(conn)

    else:
        print("Error! cannot create the database connection.")

    conn.close()

if __name__ == '__main__':
    main()
