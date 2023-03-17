from contextlib import closing
import sqlite3
from main import DEFAULT_DB_PATH


DATABASE_FILE = DEFAULT_DB_PATH+'db.sqlite'

def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor() # calls execute() to perform SQL commands

    cur.execute('''CREATE TABLE IF NOT EXISTS User (
                        username varchar(255) NOT NULL,
                        PRIMARY KEY (username)
                        );
                 ''')
    conn.commit() # saves the changes
    conn.close()

def get_all():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor() # calls execute() to perform SQL commands

    cur.execute("SELECT * FROM User")
    users = cur.fetchall()

    conn.commit() # saves the changes
    conn.close()
    return users

def insert_user(user):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor() # calls execute() to perform SQL commands

    cur.execute("INSERT INTO user VALUES (?)", (user.username))

    conn.commit() # saves the changes
    conn.close()

def delete_user(user):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor() # calls execute() to perform SQL commands

    cur.execute("DELETE FROM user WHERE rowid=(?)", id)

    conn.commit() # saves the changes
    conn.close()


# user id auto increment row id primary key
# time stamp when is added
# email index kur
# diger bilgiler
# script calisacak credential okuyup kayit atacak
# database ayri fileda
# main den database e yazma fonksiyonu cagirilacak