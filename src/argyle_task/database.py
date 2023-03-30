import json
import logging
import sqlite3
import user
from typing import List


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


def create_table(db_path:str) -> None:
    """This creates a table for the user data, if not exists.

    Args:
        db_path (str): path for the database
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()  # calls execute() to perform SQL commands
    logger.info("Connected to SQLite")
    cur.execute('''CREATE TABLE IF NOT EXISTS User (
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username varchar(255) NOT NULL,
                        user_id varchar(255) NOT NULL,
                        profile TEXT
                        );
                 ''')
    conn.commit()  # saves the changes
    conn.close()


def get_all(db_path:str) -> List[user.User]:
    """This returns all the users in the database.

    Args:
        db_path (str): path for the database

    Returns:
        List[user.User]: All the users' profile information
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()  # calls execute() to perform SQL commands

    cur.execute("SELECT * FROM User")
    logger.info(f"Users are read from the database.")

    users = cur.fetchall()

    conn.commit()  # saves the changes
    conn.close()
    return users


def insert_users(db_path:str, users: List[user.User]) -> None:
    """This inserts given users as user list.

    Args:
        db_path (str): path for the database
        users (List[user.User]): Users' profile information
    """
    conn = sqlite3.connect(db_path)
    sql_params = [(user.username, user.user_id, user.to_json())
                  for user in users]
    cur = conn.cursor()  # calls execute() to perform SQL commands
    cur.executemany(
        "INSERT INTO User(username, user_id, profile) VALUES (?, ?, ?)", sql_params)
    logger.info(f"{len(users)} are added to the database.")
    conn.commit()  # saves the changes
    conn.close()


def delete_user(db_path:str, username: str) -> None:
    """This deletes the specified user's information from the database.

    Args:
        db_path (str): path for the database
        username (str): uniq username is taken for deletion
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()  # calls execute() to perform SQL commands

    cur.execute("DELETE FROM user WHERE username=(?)", username)
    logger.info(f"{username} is deleted from the database.")

    conn.commit()  # saves the changes
    conn.close()
