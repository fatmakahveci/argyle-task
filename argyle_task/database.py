from datetime import datetime
import json
import logging, sqlite3
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'

DATABASE_FILE = ROOT_DIR+'db.sqlite'

logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
        )
logger = logging.getLogger("database_logger")


class User:
    def __init__(self, username):
        self.id = ""
        self.name = ""
        self.username = username # (unique) email or username
        self.title = ""
        self.description = ""
        self.country = ""
        self.city = ""
        self.time_zone = ""
        self.skills = []
        self.hourly_rate = ""
        self.languages = []
        self.certificates = []
        self.employment_history = []
        self.education = []
        self.job_categories = []
        self.creation_date = ""
        self.updated_on = ""
        self.profile = ""

    def __str__(self):
        user = f"""
        id: {self.id}
        name: {self.name}
        title: {self.title}
        description: {self.description}
        country: {self.country}
        city: {self.city}
        time_zone: {self.time_zone}
        skills: {self.skills}
        hourly_rate: {self.hourly_rate}
        languages: {self.languages}
        certificates: {self.certificates}
        employment history: {self.employment_history}
        education: {self.education}
        job categories: {self.job_categories}
        creation date: {self.creation_date}
        updated on: {self.updated_on}
        """
        return user


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor() # calls execute() to perform SQL commands
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
    conn.commit() # saves the changes
    conn.close()

def get_all():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor() # calls execute() to perform SQL commands

    cur.execute("SELECT * FROM User")
    logger.info(f"Users are read from the database.")

    users = cur.fetchall()

    conn.commit() # saves the changes
    conn.close()
    return users

def insert_user(user):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor() # calls execute() to perform SQL commands
    user_profile = json.dumps(user.__dict__, cls=DatetimeEncoder)
    cur.execute("INSERT INTO User(username, userId, profile_creation_time, profile_update_time, profile) VALUES (?, ?, ?, ?, ?)", (user.username, user.id, user.creation_date, user.updated_on, user_profile))
    logger.info(f"{user.username} is added to the database.")
    conn.commit() # saves the changes
    conn.close()

def delete_user(username: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor() # calls execute() to perform SQL commands

    cur.execute("DELETE FROM user WHERE username=(?)", username)
    logger.info(f"{username} is deleted from the database.")
    
    conn.commit() # saves the changes
    conn.close()
