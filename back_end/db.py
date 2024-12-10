import sqlite3
from data_model import File_List, Display_Content
from typing import List, Tuple, Literal, Union

class DB_handler(object):
    """
    Database for storage files content
    """
    def __init__(self, db_url: str) -> None:
        try:
            self.connection = sqlite3.connect(db_url)
        except sqlite3.Error as error:
            print(f"Cannot connect to {db_url} db, ", error)

    def insert_files(self, files: File_List):
        try:
            with self.connection:
                prompt = """
                CREATE TABLE IF NOT EXISTS user_files (id INT PRIMARY KEY, fileUrl TEXT, fileContent TEXT);
                """
                self.connection.execute(prompt)
            
            with self.connection:
                prompt = """
                    INSERT INTO user_files (FileUrl, FileContent) VALUES (?,?);
                """
                self.connection.executemany(prompt, [
                                            (ele.file_path, ele.file_content) 
                                            for ele in files.list_file
                                        ])
            
        except Exception as error:
            print(f"Cannot peform insert many files, ", error)

    def close(self):
        self.connection.close()

    def get_content_from_url(self, 
                             url:str,
                             purpose: Literal['process','display'] = 'display'
                             )->Union[str, Display_Content]:
        try:
            with self.connection:
                records = self.connection.execute(f"""SELECT fileContent FROM user_files WHERE fileUrl = "{url}";""").fetchall()
        except Exception as error:
            print(f"Cannot peform select file {url} error: ", error)

        if purpose == 'display':
            return Display_Content(file_content= records[0][0])
        elif purpose == 'process':
            return records[0][0]

    def show_table(self)->List[Tuple[str]]:
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM user_files;""")
        records = cursor.fetchall()

        return records