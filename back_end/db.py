import sqlite3


class DB_handler(object):
    """
    Database for storage files content
    """
    def __init__(self, db_url: str) -> None:
        self.con = sqlite3.connect("tutorial.db")

    # def insert_files(self, file_containt):
