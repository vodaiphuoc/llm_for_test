import os
from typing import List

def run_make_report(logs_file:str, 
                    test_cases_file_path:str,
                    dependencies: List[str],
                    python_env_path = 'test_pytest\\testenv\\Scripts\\python.exe'
                    ):
    try:
        if len(dependencies) >0:
            str_dependencies = ' '.join(dependencies)
            os.system(command= f'{python_env_path} -m pip install {str_dependencies}')
        # execute pytest under artificial venv
        os.system(command= f'{python_env_path} -m pytest db/{test_cases_file_path} --junit-xml={logs_file}')
        return True
    
    except Exception as e:
        print(e)
        return False
