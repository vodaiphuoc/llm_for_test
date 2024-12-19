from databases.data_model import File_List

import sqlite3
from typing import List, Tuple, Literal, Union
from collections import namedtuple
import re

DISPLAY_PATTERNS = namedtuple("DISPLAY_PATTERNS", 
        ['detect_pattern', 'line_tab','non_line_tab','row_pattern','final_pattern'])

total_pattern = DISPLAY_PATTERNS('^\s+', 
    '<div class="tab-spacing">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div>',
    '<div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div>',
"""
<tr>
<td><p class="line-number">{line_number}</p></td>
<td>
    {tab_content}
    <pre><code class="language-python">{code_content}</code>
    </pre>
</td>
</tr>
""",
'<div><table>{rows}</table></div><script>hljs.highlightAll();</script>'
)

def render_content(file_content:str)->str:
    rows_content = ""
    for ith, line in enumerate(file_content.split('\n')):
        code_content = "".join(re.split(total_pattern.detect_pattern, line))

        tab_match = re.match(total_pattern.detect_pattern, line)
        tab_DOM_list = []
        
        tab_content = ""
        if tab_match is not None:
            tab_DOM_list.append(total_pattern.non_line_tab)
            
            number_line_tabs = tab_match.span()[-1]//4 - 1

            if number_line_tabs >0:
                tab_DOM_list += [total_pattern.line_tab for _ in range(number_line_tabs)]
                tab_content =  "".join(tab_DOM_list)

            else:
                tab_content = ""
                code_content = line

        else:
            tab_content = "" 

        rows_content += total_pattern.row_pattern.format(line_number = ith+1, 
                                                        tab_content = tab_content,
                                                        code_content = code_content)
    return total_pattern.final_pattern.format(rows = rows_content)    

class DB_handler(object):
    """
    Database for storage files content
    """
    def __init__(self, db_url: Literal['db/implement.db', 'db/test_cases.db']) -> None:
        try:
            self.connection = sqlite3.connect(db_url)
            self.db_type = "implement" if db_url == 'db/implement.db' else "test_cases"
        except sqlite3.Error as error:
            print(f"Cannot connect to {db_url} db, ", error)

    def insert_files(self, files: File_List)->None:
        """
        - Delete old files when user browse new folder
        - Create `user_files` table for new browse folder
            - fileContent: raw content for py files
            - RenderContent: render content for display
        """
        try:
            with self.connection:
                del_prompt = """DROP TABLE IF EXISTS user_files;"""
                self.connection.execute(del_prompt)

                create_prompt = """
                CREATE TABLE IF NOT EXISTS user_files (id INT PRIMARY KEY, FileUrl TEXT, RawContent TEXT, RenderContent TEXT);
                """ if self.db_type == "implement" else \
                """
                CREATE TABLE IF NOT EXISTS user_files (id INT PRIMARY KEY, FileUrl TEXT, impl_RawContent TEXT, test_RawContent TEXT , RenderContent TEXT);
                """

                self.connection.execute(create_prompt)
            
            with self.connection:
                prompt = """
                    INSERT INTO user_files (FileUrl, RawContent, RenderContent) VALUES (?,?,?);
                """ if self.db_type == "implement" else \
                """
                    INSERT INTO user_files (FileUrl, impl_RawContent) VALUES (?,?);
                """

                self.connection.executemany(prompt, [
                                            (ele.save_file_path, 
                                             ele.file_content,
                                             render_content(ele.file_content)) 
                                             if self.db_type == "implement" else \
                                             (ele.save_file_path,
                                             ele.file_content) 
                                            for ele in files.list_file
                                            ]
                                        )
        except Exception as error:
            print(f"Cannot peform insert many files, db type: {self.db_type}, ", error)

    def close(self):
        self.connection.close()

    def get_content_from_url(self, 
                             url:str,
                             content_type: Literal['RawContent','RenderContent']
                             )->str:
        try:
            with self.connection:
                target_col = content_type if self.db_type == 'implement' else 'impl_RawContent'
                query_prompt = f"""SELECT {target_col} FROM user_files WHERE FileUrl LIKE '%{url}';"""
                records = self.connection.execute(query_prompt).fetchall()
                return records[0][0]
        
        except Exception as error:
            print(f"Cannot peform select file {url} error: ", error)


    def show_table(self)->List[Tuple[str]]:
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM user_files;""")
        records = cursor.fetchall()

        return records