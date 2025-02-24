
'''
attitude_bh
attitude_pit
pcs_fixed, elevation, azimuth
'''

import sqlite3

TABLE_ROWS = {
    "attitude_bh":  ["seconds", "microseconds", "quaternion_x", "quaternion_y", "quaternion_z", "quaternion_s"],
    "attitude_pit": ["seconds", "microseconds", "quaternion_x", "quaternion_y", "quaternion_z", "quaternion_s"],
    "pcs_fixed":   ["seconds", "microseconds", "elevation", "azimuth"]
}

def create_db(db_file):

    # Database to connect to
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attitude_bh (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seconds      INTEGER NOT NULL,
            microseconds INTEGER NOT NULL,
            quaternion_x FLOAT   NOT NULL,
            quaternion_y FLOAT   NOT NULL,
            quaternion_z FLOAT   NOT NULL,
            quaternion_s FLOAT   NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attitude_pit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seconds      INTEGER NOT NULL,
            microseconds INTEGER NOT NULL,
            quaternion_x FLOAT   NOT NULL,
            quaternion_y FLOAT   NOT NULL,
            quaternion_z FLOAT   NOT NULL,
            quaternion_s FLOAT   NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pcs_fixed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seconds      INTEGER NOT NULL,
            microseconds INTEGER NOT NULL,
            elevation    FLOAT   NOT NULL,
            azimuth      FLOAT   NOT NULL
            
        )
    ''')


    conn.commit()
    conn.close()


def get_last_time(cursor, table_name):

    cursor.execute(f"SELECT seconds, microseconds FROM {table_name} ORDER BY id DESC LIMIT 1")
    last_time = cursor.fetchone()

    return last_time

def get_rows_after_time(db_file, table_name, time_tuple):
    
    seconds = 0
    microseconds = 0
    if time_tuple:
        seconds, microseconds = time_tuple

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    select_cols = ",".join(TABLE_ROWS[table_name])

    cursor.execute(f"""SELECT {select_cols} FROM {table_name}
        WHERE seconds > ? OR (seconds = ? AND microseconds > ?)""", 
        (seconds, seconds, microseconds))
    
    rows = cursor.fetchall()

    conn.close()

    return rows


def update_db(db_file, external_db):

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    for table_name in TABLE_ROWS:
        print("Table: {}".format(table_name))

        last_time = get_last_time(cursor, table_name)
        if last_time:
            print("Last Seconds: {}, Microseconds: {}".format(last_time[0], last_time[1]))

        select_cols = ",".join(TABLE_ROWS[table_name])
        placeholder_values = ",".join("?"*len(TABLE_ROWS[table_name]))

        rows = get_rows_after_time(external_db, table_name, last_time)

        if not rows:
            print("Up-to-date")
            continue

        cursor.executemany(f"""INSERT INTO {table_name} 
            ({select_cols}) VALUES ({placeholder_values})""", rows)
        
        print("New: {}, Seconds: {}, Microseconds: {}".format(len(rows), rows[-1][0], rows[-1][1]))


    conn.commit()
    conn.close()