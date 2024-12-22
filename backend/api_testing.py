from llm.agent import Agent
from databases.db import DB_handler
from databases.api_data_model import UploadFilesBody_Testing, GenerateTask_Testing

from main import UploadFileDependencies, upload_files_router
from main import GenerateTasksDependencies, generate_test_cases

import asyncio
import pathlib
import tabnanny


def upload_files_api(implement_db = None, 
                     test_cases_db = None, 
                     model = None):
    path2currFolder = pathlib.WindowsPath('D:\\Projects\\Test_coverage_LLM\\llm_for_test')
    folder_name = 'codes'

    full_list_files = [
        'codes/implements/leet_code.py', 
        'codes/implements/leet_code2.py', 
        'codes/implements/LLM.py', 
        'codes/implements/model_llm.py', 
        'codes/implements/my_function.py', 
        'codes/implements_test_cases/test_my_function.py', 
        'codes/requirements.txt'
    ]

    asyncio.run(upload_files_router(params= UploadFileDependencies(request_data = \
                        UploadFilesBody_Testing(path2currDir = path2currFolder,
                            list_files = full_list_files,
                            selected_folder_name = folder_name,
                            implement_db = DB_handler('db/implement.db') if implement_db is None else implement_db,
                            test_cases_db = DB_handler('db/test_cases.db') if test_cases_db is None else test_cases_db,
                            model = Agent() if model is None else model)
                        ))
    )


def gen_testcases_api():
    model = Agent()
    test_cases_db = DB_handler('db/test_cases.db')
    gen_params = {
        'model': model,
        'test_cases_db': test_cases_db,
        'request_file_dict': {'file_list': ['codesPATHSPLITimplementsPATHSPLITleet_code2.py']}
    }
    
    upload_files_api(implement_db = DB_handler('db/implement.db'), 
                     test_cases_db = test_cases_db, 
                     model = model)

    asyncio.run(generate_test_cases(params= \
            GenerateTasksDependencies(\
                task_id='task-1', request_data=GenerateTask_Testing(**gen_params))
    ))


    asyncio.run(generate_test_cases(params= \
            GenerateTasksDependencies(\
                task_id='task-2', request_data=GenerateTask_Testing(**gen_params))
    ))


    asyncio.run(generate_test_cases(params= \
            GenerateTasksDependencies(\
                task_id='task-3', request_data=GenerateTask_Testing(**gen_params))
    ))


    asyncio.run(generate_test_cases(params= \
            GenerateTasksDependencies(\
                task_id='task-4', request_data=GenerateTask_Testing(**gen_params))
    ))



if __name__ == '__main__':
    upload_files_api()



    # task_1_out = model.prepare_input(request_files, test_cases_db)
    # task_2_out = model.create_testcases()
    # task_3_out = model.check_dependencies()
    # task_4_out = model.execute_pytest()


