from dataclasses import dataclass
from typing import List
import re

@dataclass
class SingleTargetTestCases:
    target: str
    test_cases_codes: str

FORMAT_SINGLE_TEST = f"""# target function: {{target}}
{{test_cases_codes}}

"""

@dataclass
class Single_LLM_Output: # <-- per single module .py
    original_file_path:str
    import_module_command:str
    intall_dependencies: str
    built_in_import:str
    test_cases: List[SingleTargetTestCases]

    def test_cases2string(self)->str:
        return "".join([ FORMAT_SINGLE_TEST.format(**single_out) for single_out in self.test_cases])

    def tostring(self)->str:
        return f"""
# target module: {self.original_file_path}
# import functions from modules
{self.import_module_command}
# dependencies to install
{self.intall_dependencies}
# built-in 
{self.built_in_import}
# test cases codes
{self.test_cases2string()}
"""

    def get_dependencies(self)->List[str]:
        outputs = re.findall(r'import (.+?) as|import (.+?)\n|from (.+?) import', self.intall_dependencies)
        dependencies = []
        for _result in outputs:
            dependencies.extend([ele for ele in _result if ele != ''])
        return list(set(dependencies))

@dataclass
class LLM_Output:
    total_reponse: List[Single_LLM_Output]
