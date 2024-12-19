from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import uvicorn
import os
import time
from typing import List
from loguru import logger

from databases.data_model import Script_File, File_List
from databases.db import DB_handler
from llm.agent_tester import Agent




@asynccontextmanager
async def lifespan(app: FastAPI):
    # init engine here
    app.implement_db = DB_handler('db/implement.db')
    app.test_cases_db = DB_handler('db/test_cases.db')
    app.model = Agent()
    
    yield
    app.implement_db.close()
    app.implement_db = None

    app.test_cases_db.close()
    app.test_cases_db = None

    app.model = None

app = FastAPI(lifespan= lifespan)

origins = [
    "http://localhost",
    "http://localhost:5000/",
    "http://127.0.0.1:5000/open",
    "http://localhost:8080/",
    "http://localhost:8000/",
    "http://127.0.0.1:8000/",
    "http://127.0.0.1:8000"
]
app.add_middleware(CORSMiddleware, 
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"]
                   )
# app.mount(path = '/statics', 
#           app = StaticFiles(directory='./statics', html = False), 
#           name='statics')

# for testing on web browser only
# templates = Jinja2Templates(directory='./templates')
# @app.get("/", response_class=HTMLResponse)
# async def index_router(request: Request):
# 	return templates.TemplateResponse(
# 		request = request,
# 		name = "index.html"
# 		)

def flatten_tree(tree_dict: dict, parent:str = ''):
    dir_list = []
    for k, v in tree_dict.items():
        if isinstance(v, dict):
            result_list = flatten_tree(v, k) if parent == '' else flatten_tree(v, parent+'/'+k)
            dir_list.extend(result_list)
        else:
            if parent == '':
                dir_list.append(v)
            else:
                dir_list.append(parent+'/'+v)
    return dir_list

@app.post("/upload_files", response_class=JSONResponse)
async def upload_files_router(request: Request, background_tasks: BackgroundTasks):
    """Receive post request from expressjs"""
    try:
        request_dict = await request.json()
        dir_tree = request_dict['dict_tree']
        path2currFolder = request_dict['path2currDir']

        # flatten tree
        list_files = flatten_tree(dir_tree,'')
        
        list_data = File_List(list_file = [Script_File(file_path = path2currFolder+dir,
                                                       relative_file_path = dir) 
                                            for dir in list_files])

        # insert to DB
        request.app.implement_db.insert_files(list_data)
        request.app.test_cases_db.insert_files(list_data)

        # create user repo with dict_tree
        background_tasks.add_task(request.app.model.make_user_repo, 
                                  path2currFolder = path2currFolder, 
                                  folder_name = list(dir_tree.keys())[-1])

        return JSONResponse(status_code=200,content='')
    
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,content='')


@app.get("/load_py/", response_class=JSONResponse)
async def get_file_content(file_name:str, request: Request):
    """Receive get request from front-end"""
    try:
        html_content = request.app.implement_db.get_content_from_url(url = file_name, 
                                                        content_type= 'RenderContent')
        return JSONResponse(content={'html_content': html_content})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,content={'html_content': 'ERROR LOAD FILE'})


@app.post("/generate_test_cases_task-1", response_class=JSONResponse)
async def generate_test_cases(request: Request):
    """Receive get request from front-end"""
    try:
        request_dict = await request.json()
        request_files = request_dict['file_list']

        file_contents = [
            {
                'repo_url': query_result[0],
                'file_content':query_result[1],
                'module_path': query_result[2]
            }
            for file_name in request_files
            if len((query_result:=request.app.test_cases_db.get_content_from_url(url = file_name,
                                                        content_type='RawContent')
             )) == 3
        ]

        response_data = request.app.model.run(file_contents)
        # await asyncio.sleep(10)
        return JSONResponse(status_code=200,content= {'data': 'created'})
        
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,content={'html_content': 'ERROR LOAD FILE'})


# @app.get("/generate_test_cases/{task_id}")
# async def generate_test_cases(task_id: str,request: Request):
#     """Receive get request from front-end"""
#     try:
#         if task_id == 'task-1':
#             logger.info('in main: ',request)
#             request_dict = request.json()
#             logger.info('in main: ',request_dict)
#             # request_files = request_dict['file_list']
#             # logger.info('in main: ',request_files)


#             # response_data = _make_test_cases(request, request_files)
#             # await asyncio.sleep(10)
#             return JSONResponse(status_code=200,content= {'data': [1,2,3,4]})
#         else:
#             # await asyncio.sleep(5)
#             return JSONResponse(status_code=200,content= {'data': [5,6,7,8]})
    
#     except Exception as e:
#         print(e)
#         return JSONResponse(status_code=500,content={'html_content': 'ERROR LOAD FILE'})



async def main_run():
    config = uvicorn.Config("main:app", 
    	port=8000, 
    	log_level="info",
    	reload=True
    	)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main_run())