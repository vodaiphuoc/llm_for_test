from llm.agent_tester import Agent
from databases.db import DB_handler
from databases.api_data_model import UploadFilesBody_Testing
from main import UploadFileDependencies, upload_files_router
import asyncio
import pathlib


# path2currFolder = pathlib.WindowsPath('D:\Projects\Test_coverage_LLM\llm_for_test')
# folder_name = 'codes'

# full_list_files = [
#     'codes/implements/leet_code.py', 
#      'codes/implements/leet_code2.py', 
#      'codes/implements/LLM.py', 
#      'codes/implements/model_llm.py', 
#      'codes/implements/my_function.py', 
#      'codes/implements_test_cases/test_my_function.py', 
#      'codes/requirements.txt'
# ]

# asyncio.run(upload_files_router(params= UploadFileDependencies(request_data = \
#                        UploadFilesBody_Testing(path2currDir = path2currFolder,
#                         list_files = full_list_files,
#                         selected_folder_name = folder_name,
#                         implement_db = DB_handler('db/implement.db'),
#                         test_cases_db = DB_handler('db/test_cases.db'),
#                         model = Agent())
#                     ))
# )


# list_files = ['D:\\Projects\\Test_coverage_LLM\\llm_for_test\\codes\\implements\\leet_code2.py',
#                  'D:\\Projects\\Test_coverage_LLM\\llm_for_test\\codes\\implements\\my_function.py'
#                  ]


# task_1_out = model.prepare_input(request_files, test_cases_db)
# task_2_out = model.create_testcases()
# task_3_out = model.check_dependencies()
# task_4_out = model.execute_pytest()


