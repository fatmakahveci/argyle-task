from datetime import datetime
import json
import logging
import sqlite3
import os
import user
from typing import List

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'

DATABASE_FILE = ROOT_DIR+'db.sqlite'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger("database_logger")


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()  # calls execute() to perform SQL commands
    logger.info("Connected to SQLite")
    # TODO index on username
    cur.execute('''CREATE TABLE IF NOT EXISTS User (
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username varchar(255) NOT NULL,
                        userId varchar(255) NOT NULL,
                        profile_creation_time INT,
                        profile_update_time INT,
                        profile TEXT
                        );
                 ''')
    conn.commit()  # saves the changes
    conn.close()


def get_all():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()  # calls execute() to perform SQL commands

    cur.execute("SELECT * FROM User")
    logger.info(f"Users are read from the database.")

    users = cur.fetchall()

    conn.commit()  # saves the changes
    conn.close()
    return users


def insert_users(users: List[user.User]):
    conn = sqlite3.connect(DATABASE_FILE)
    sql_params = [(user.username, user.id, user.creation_date,
                   user.updated_on, user.to_json()) for user in users]
    cur = conn.cursor()  # calls execute() to perform SQL commands
    cur.executemany("INSERT INTO User(username, userId, profile_creation_time, profile_update_time, profile) VALUES (?, ?, ?, ?, ?)",
                    sql_params)
    logger.info(f"{len(users)} are added to the database.")
    conn.commit()  # saves the changes
    conn.close()


def delete_user(username: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()  # calls execute() to perform SQL commands

    cur.execute("DELETE FROM user WHERE username=(?)", username)
    logger.info(f"{username} is deleted from the database.")

    conn.commit()  # saves the changes
    conn.close()
