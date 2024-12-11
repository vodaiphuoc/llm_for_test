import os

def run_make_report(logs_file:str, 
                    test_cases_dir:str
                    ):
    
    if os.path.isdir(test_cases_dir):
        os.system(command= f'pytest {test_cases_dir}/ --junit-xml={logs_file}')
