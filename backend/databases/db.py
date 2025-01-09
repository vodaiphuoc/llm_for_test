from databases.api_data_model import File_List, Function_Metadata, Branch_Metadata
from databases.indent_checker import IndentChecker
from pydantic import TypeAdapter

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

        try:
            with self.connection:
                del_prompt = """DROP TABLE IF EXISTS user_files;"""
                self.connection.execute(del_prompt)

                if self.db_type == 'test_cases':
                    print('drop meta data')
                    self.connection.execute("""DROP TABLE IF EXISTS functions_metadata;""")
                    self.connection.execute("""DROP TABLE IF EXISTS branches_metadata;""")
        
        except sqlite3.Error as error:
            print('Cannot delete tables')


        try:
            with self.connection:
                if self.db_type == "implement":
                    create_prompt = """
CREATE TABLE user_files (id INT PRIMARY KEY, SearchFileUrl TEXT, RawContent TEXT, RenderContent TEXT);
""" 
                    self.connection.execute(create_prompt)
                else:
                    create_prompt = """
CREATE TABLE user_files (id INT PRIMARY KEY, SearchFileUrl TEXT, RepoFileURL TEXT, impl_RawContent TEXT, moduleImport TEXT, test_RawContent TEXT , RenderContent TEXT);
"""
                    self.connection.execute(create_prompt)

                    # create metadata table
                    self.connection.execute(DB_handler.get_metadata_table_prompt(get_prompt=True,
                                                                                 table='functions_metadata'))
                    self.connection.execute(DB_handler.get_metadata_table_prompt(get_prompt=True,
                                                                                 table='branches_metadata'))
        
        except sqlite3.Error as error:
            print('Cannot create table', error)

    @staticmethod
    def get_metadata_table_prompt(get_prompt:bool, 
                                  table: Literal['functions_metadata','branches_metadata']
                                  ):
        dtype_convert = {'string':'TEXT','integer':'TN'}  

        if table =='functions_metadata':
            _num_fields = len(TypeAdapter(Function_Metadata).json_schema()['properties'].items())
            subfields = ",".join([k +' '+dtype_convert.get(v['type']) 
                              for k, v in TypeAdapter(Function_Metadata).json_schema()['properties'].items()
                              ])
        else:
            _num_fields = len(TypeAdapter(Branch_Metadata).json_schema()['properties'].items())
            subfields = ",".join([k +' '+dtype_convert.get(v['type']) 
                              for k, v in TypeAdapter(Branch_Metadata).json_schema()['properties'].items()
                              ])

        if get_prompt:
            return f"CREATE TABLE {table} (id INT PRIMARY KEY, {subfields});"
        else:
            return (",".join([k for k, v in TypeAdapter(Function_Metadata).json_schema()['properties'].items()]), 
                    ",".join(['?']*_num_fields) )\
                    if table =='functions_metadata' else \
                    (",".join([k for k, v in TypeAdapter(Branch_Metadata).json_schema()['properties'].items()]), 
                     ",".join(['?']*_num_fields) )

    @staticmethod
    def prepare_input(files: File_List):
        all_file_error_count = 0
        
        unpack_data = []
        unpack_test_data = []
        funcs_meta_data = []
        branches_meta_data = []

        for ele in files.list_file:
            indent_result = IndentChecker.check(ele.file_path, ele.search_file_path)

            _search_path = ele.search_file_path
            _content = ele.file_content

            unpack_data.append((_search_path, 
                                _content,
                                render_content(indent_result['line_with_error'])
                                ))
            all_file_error_count += indent_result['total_error']
                
            unpack_test_data.append((_search_path,
                                    ele.relative_copied_file_path,
                                    _content,
                                    ele.import_module))
            
            if indent_result['total_error'] == 0:
                funcs_meta, branch_meta = indent_result['metadata']
                funcs_meta_data.extend(funcs_meta)
                branches_meta_data.extend(branch_meta)
        
        return (all_file_error_count, 
                unpack_data, 
                unpack_test_data,
                [ele.to_tuple for ele in funcs_meta_data], 
                [ele.to_tuple for ele in branches_meta_data]
        )

    def insert_files(self, 
                     unpack_data: List[tuple], 
                     functions_meta_data = None, 
                     branches_meta_data = None
                     )->None:
        """
        - Delete old files when user browse new folder
        - Create `user_files` table for new browse folder
            - fileContent: raw content for py files
            - RenderContent: render content for display
        """
        try:
            with self.connection:
                prompt = """
                    INSERT INTO user_files (SearchFileUrl, RawContent, RenderContent) VALUES (?,?,?);
                """ if self.db_type == "implement" else \
                """
                    INSERT INTO user_files (SearchFileUrl, RepoFileURL, impl_RawContent, moduleImport) VALUES (?,?,?,?);
                """
                self.connection.executemany(prompt, unpack_data)
                
                if self.db_type == 'test_cases':
                    assert functions_meta_data is not None and branches_meta_data is not None

                    _fields, _fields_inputs = DB_handler.get_metadata_table_prompt(get_prompt=False, table='functions_metadata')
                    
                    sql = "INSERT INTO functions_metadata " +\
                                f"({_fields})" +\
                                f"VALUES ({_fields_inputs});"
                    print(f'run insert functions_metadata, {self.db_type}, number of new data: {len(functions_meta_data)}')
                    
                    self.connection.executemany(sql,functions_meta_data)
                    
                    _fields, _fields_inputs = DB_handler.get_metadata_table_prompt(get_prompt=False, table='branches_metadata')
                    
                    sql = "INSERT INTO branches_metadata " +\
                                f"({_fields})" +\
                                f"VALUES ({_fields_inputs});"
                    
                    print(f'run insert branches_metadata, {self.db_type}, number of new data: {len(branches_meta_data)}')
                    self.connection.executemany(sql,branches_meta_data)

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

    def get_functions(self, url:str, lines: List[int], missing_branches: List[List[int]]):
        """Use to query a subset of code which is not executed"""

        # step 0: check db type, only use for testcase.db
        assert self.db_type == 'test_cases', "this method is used only for test_cases.db"

        # step 1: find original functions/methods which are not executed
        outputs = []
        for (start_branch, end_branch) in missing_branches:
            query_function_prompt = f"""SELECT SearchFileUrl, class_name, function_name, function_type, start_line, body_content 
FROM functions_metadata 
WHERE SearchFileUrl LIKE '%{url}'
AND ((start_line <= {start_branch} AND end_line >= {end_branch}));"""
                
            query_branch_prompt = f"""SELECT branch_type, branch_content
FROM branches_metadata
WHERE SearchFileUrl LIKE '%{url}'
AND ((branch_start_line <= {start_branch} AND branch_end_line >= {end_branch}));"""

            try:
                with self.connection:

                    (_SearchFileUrl, _class_name, _func_name, _type, _start_line, _body_content) = \
                        self.connection.execute(query_function_prompt).fetchall()[0]

                    (_branch_type, _branch_content) = \
                        self.connection.execute(query_branch_prompt).fetchall()[0]
                
                # step 2: crop a subset (aka branch) of original funtion/method
                outputs.append((_SearchFileUrl, _class_name, _func_name, _type, _body_content, _branch_type, _branch_content))

            except sqlite3.Error as error:
                print(f"Cannot peform select branch with file {url}, db type {self.db_type}, error: ", error)
                return None
    
            except IndexError as error:
                print(f"Index error with file {url}, db type {self.db_type}, error: ", error)
                return None
                
            return outputs
        
        

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
