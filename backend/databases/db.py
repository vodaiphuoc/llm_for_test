from databases.api_data_model import File_List

import sqlite3
import json
from typing import List, Tuple, Literal, Union, Dict
from collections import namedtuple
import re

DISPLAY_PATTERNS = namedtuple("DISPLAY_PATTERNS", 
        ['detect_pattern', 'line_tab','non_line_tab','row_pattern','final_pattern'])

total_pattern = DISPLAY_PATTERNS('^\s+', 
    '<div class="tab-spacing">&nbsp;&nbsp;&nbsp;&nbsp;</div>',
    '<div>&nbsp;&nbsp;&nbsp;&nbsp;</div>',
"""
<tr>
<td><p class="line-number">{line_number}</p></td>
<td>
    {tab_content}
    <pre {stype_for_error}><code class="language-python">{code_content}</code>
    </pre>
</td>
</tr>
""",
'<div><table>{rows}</table></div>'
)
# <script>hljs.highlightAll();</script>

def render_content(line_with_errors: List[Dict[str,Union[str,int, bool]]])->str:
    rows_content = ""
    for line_dict in line_with_errors:
        line = line_dict['line']
        line_number = line_dict['line_number']
        error = line_dict['error']

        code_content = "".join(re.split(total_pattern.detect_pattern, line))

        tab_match = re.match(total_pattern.detect_pattern, line)
        tab_DOM_list = []
        
        tab_content = ""
        if tab_match is not None:
            tab_DOM_list.append(total_pattern.non_line_tab)
            
            number_line_tabs = tab_match.span()[-1]//4 - 1

            if number_line_tabs > 0:
                tab_DOM_list += [total_pattern.line_tab for _ in range(number_line_tabs)]
                tab_content =  "".join(tab_DOM_list)

            else:
                tab_content = ""
                code_content = line

        else:
            tab_content = "" 

        rows_content += total_pattern.row_pattern.format(line_number = line_number, 
                                                        tab_content = tab_content,
                                                        stype_for_error = 'style="background-color: red;"' if error else '',
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
                CREATE TABLE IF NOT EXISTS user_files (id INT PRIMARY KEY, SearchFileUrl TEXT, RawContent TEXT, RenderContent TEXT);
                """ if self.db_type == "implement" else \
                """
                CREATE TABLE IF NOT EXISTS user_files (id INT PRIMARY KEY, SearchFileUrl TEXT, RepoFileURL TEXT, impl_RawContent TEXT, moduleImport TEXT, test_RawContent TEXT , RenderContent TEXT);
                """

                self.connection.execute(create_prompt)
            
            with self.connection:
                prompt = """
                    INSERT INTO user_files (SearchFileUrl, RawContent, RenderContent) VALUES (?,?,?);
                """ if self.db_type == "implement" else \
                """
                    INSERT INTO user_files (SearchFileUrl, RepoFileURL, impl_RawContent, moduleImport) VALUES (?,?,?,?);
                """
                all_file_error_count = 0
                unpack_data = []
                for ele in files.list_file:
                    if self.db_type == "implement":
                        line_with_error,  total_errors = ele.file_content_with_error
                        unpack_data.append((ele.search_file_path, 
                                             ele.file_content,
                                             render_content(line_with_error)))
                        all_file_error_count += total_errors
                    else:
                        unpack_data.append((ele.search_file_path,
                                              ele.relative_copied_file_path,
                                              ele.file_content,
                                              ele.import_module))
                
                self.connection.executemany(prompt, unpack_data)

                if self.db_type == 'implement':
                    return all_file_error_count

                # self.connection.executemany(prompt, [
                #                             (ele.search_file_path, 
                #                              ele.file_content,
                #                              render_content(ele.file_content_with_error)) 
                #                              if self.db_type == "implement" else \
                #                              (ele.search_file_path,
                #                               ele.relative_copied_file_path,
                #                               ele.file_content,
                #                               ele.import_module)
                #                             for ele in files.list_file
                #                             ]
                #                         )
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
                target_col = content_type if self.db_type == 'implement' else 'RepoFileURL, impl_RawContent, moduleImport'
                query_prompt = f"""SELECT {target_col} FROM user_files WHERE SearchFileUrl LIKE '%{url}';"""
                records = self.connection.execute(query_prompt).fetchall()
                return records[0][0] if self.db_type == 'implement' else records[0]
        
        except Exception as error:
            print(f"Cannot peform select file {url} error: ", error)


    def show_table(self)->List[Tuple[str]]:
        cursor = self.connection.cursor()
        cursor.execute("""SELECT * FROM user_files;""")
        records = cursor.fetchall()

        return records
    

class Dependencies_DB_Handler(object):
    """
    Database for storage package name and PyPi package index
    Init only inside agent tester
    """
    def __init__(self, 
                 db_url:str = 'db/dependencies.db') -> List[str]:
        try:
            self.connection = sqlite3.connect(db_url)
        except sqlite3.Error as error:
            print(f"Cannot connect to {db_url} db, ", error)
        
        self._create_tables_on_start()

    def _create_tables_on_start(self):
        try:
            with self.connection:
                create_prompt = """
                CREATE TABLE IF NOT EXISTS packages (id INT PRIMARY KEY, import_pkg_name TEXT, PyPi_index TEXT, version TEXT);
                """
                self.connection.execute(create_prompt)
        except Exception as error:
            print(f"Cannot peform create table with error: ", error)

    def insert_files(self, new_pkgs_data: List[Dict[str,str]])->None:
        try:            
            with self.connection:
                prompt = """
                    INSERT INTO packages (import_pkg_name, PyPi_index, version) VALUES (?,?,?);
                """ 
                self.connection.executemany(prompt, [
                                            (ele['import_pkg_name'], 
                                             ele['PyPi_index'],
                                             ele['version']
                                             ) 
                                            for ele in new_pkgs_data
                                            ]
                                        )
        except Exception as error:
            print(f"Cannot peform insert packages: {new_pkgs_data},\n with error: ", error)

    def query_package(self, import_name:str)->Union[bool, Tuple[str]]:
        assert isinstance(import_name,str), f"Found type: {type(import_name)}"
        try:
            with self.connection:
                query_prompt = f"""SELECT PyPi_index, version FROM packages WHERE import_pkg_name = '{import_name}';"""
                records = self.connection.execute(query_prompt).fetchall()
                return records[0] if len(records) > 0 else False
        
        except Exception as error:
            print(f"Cannot peform search package {import_name} error: ", error)
