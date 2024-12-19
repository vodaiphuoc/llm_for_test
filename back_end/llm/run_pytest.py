import os

def run_make_report(logs_file:str, 
                    test_cases_file_path:str
                    ):
    try:
        os.system(command= f'pytest db/{test_cases_file_path} --junit-xml={logs_file}')
        return True
    except Exception as e:
        print(e)
        return False
