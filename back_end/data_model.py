from pydantic.dataclasses import dataclass
from pydantic import computed_field
from typing import List
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


@dataclass
class Display_Content:
    file_content:str

    @computed_field
    @property
    def display_content(self)->str:

        rows_content = ""
        for ith, line in enumerate(self.file_content.split('\n')):
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