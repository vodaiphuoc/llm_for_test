from pydantic.dataclasses import dataclass
from pydantic import computed_field
from typing import List
from collections import namedtuple
import re

DISPLAY_PATTERNS = namedtuple("DISPLAY_PATTERNS", ['old', 'new'])

tab_pattern = DISPLAY_PATTERNS('^\s+', 
    '<p class="code-content" style="border-left: 2px solid red;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</p>')
code_pattern = DISPLAY_PATTERNS('','<p class="code-content" style="border-left: 2px solid red;">{code_content}</p>')

line_number_pattern = DISPLAY_PATTERNS('',
                    '<div class="line-number">{line_number}</div>')

line_pattern = DISPLAY_PATTERNS('',
                    '<div class="code-line">{line_number}{tab_content}{code_content}</div>')

@dataclass
class Display_Content:
    file_content:str

    @computed_field
    @property
    def display_content(self)->str:
        show_lines = ''
        for ith, line in enumerate(self.file_content.split('\n')):
            code_content = "".join(re.split(tab_pattern.old, line))
            code_content = code_pattern.new.format(code_content = code_content)

            tab_match = re.match(tab_pattern.old, line)
            tab_content = "" if tab_match is None else "".join([tab_pattern.new]*(tab_match.span()[-1]//4))
            
            line_number = line_number_pattern.new.format(line_number = ith+1)

            show_lines += line_pattern.new.format(
                line_number = line_number,
                tab_content = tab_content, 
                code_content = code_content
                )
            
        return show_lines

@dataclass
class Script_File:
    file_path: str

    @computed_field
    @property
    def save_file_path(self)->str:
        return re.sub(r'[\\,/]','PATHSPLIT', self.file_path)

    @computed_field
    @property
    def file_content(self)->str:
        with open(self.file_path, 'r') as f:
            return f.read()
        
@dataclass
class File_List:
    list_file: List[Script_File]