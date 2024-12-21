from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, Depends, Body, Path
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import uvicorn
import os
import re
import time
from typing import List, Annotated, Dict, Any
from loguru import logger

from databases.api_data_model import Script_File, File_List, \
UploadFilesBody, UploadFilesBody_Testing, GenerateTask_Testing

from databases.db import DB_handler
from llm.agent import Agent


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

def _flatten_tree(tree_dict: dict, parent:str = ''):
    dir_list = []
    for k, v in tree_dict.items():
        if isinstance(v, dict):
            result_list = _flatten_tree(v, k) if parent == '' else _flatten_tree(v, parent+'/'+k)
            dir_list.extend(result_list)
        else:
            if parent == '':
                dir_list.append(v)
            else:
                dir_list.append(parent+'/'+v)
    return dir_list

def get_app(request: Request):
    """get FastAPI app in each request"""
    return request.app

class UploadFileDependencies:
    """Dependency to classify input which `request_data` can be
    istance of `UploadFilesBody` or `UploadFilesBody_Testing`.
    """
    def __init__(self,
                 request_data: Annotated[UploadFilesBody | UploadFilesBody_Testing, Body()],
                 app: Annotated[FastAPI | None, Depends(get_app)] = None
                 ):
        if isinstance(request_data, UploadFilesBody) and app is not None:
            
            self.path2currFolder = request_data.path2currDir
            # flatten tree
            dir_tree = request_data.dict_tree
            self.list_files = _flatten_tree(dir_tree,'')

            # selected_folder_name
            self.selected_folder_name =list(dir_tree.keys())[-1]

            # db and agent accessing
            self.implement_db = app.implement_db
            self.test_cases_db = app.test_cases_db
            self.model = app.model
            
        else:
            # testing case
            assert isinstance(request_data, UploadFilesBody_Testing)
            self.path2currFolder = request_data.path2currDir
            self.list_files = request_data.list_files

            # selected_folder_name
            self.selected_folder_name = request_data.selected_folder_name

            # db and agent accessing
            self.implement_db = request_data.implement_db
            self.test_cases_db = request_data.test_cases_db
            self.model = request_data.model    

@app.post("/upload_files", response_class=JSONResponse)
async def upload_files_router(params: Annotated[UploadFileDependencies, 
                                                Depends(UploadFileDependencies)]
                            ):
    """Receive post request from expressjs"""
    try:
        list_data = File_List(list_file = [Script_File(file_path = params.path2currFolder / dir,
                                                       relative_file_path = dir) 
                                            for dir in params.list_files])
        # insert to DB
        params.implement_db.insert_files(list_data)
        params.test_cases_db.insert_files(list_data)

        # create user repo with dict_tree
        params.model.make_user_repo(path2currFolder = params.path2currFolder, 
                                         folder_name = params.selected_folder_name)

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


class GenerateTasksDependencies:
    def __init__(self,
        task_id: Annotated[str, Path()],
        request_data: Annotated[ Dict[str, List[str]] | GenerateTask_Testing | None, Body()] = None,
        app: Annotated[FastAPI | None, Depends(get_app)] = None,
        )-> None:
        
        if app is not None and not isinstance(request_data, GenerateTask_Testing):
            self.model = app.model
            
            if task_id == 'task-1':
                self.test_cases_db = app.test_cases_db
                # only task 1 has body data
                self.request_files = request_data['file_list']
            self.task_id = task_id
        
        else:
            # testing branch
            self.model = request_data.model
            self.test_cases_db = request_data.test_cases_db
            self.request_files = request_data.file_list
            self.task_id = task_id

@app.get("/generate_test_cases/{task_id}", response_class=JSONResponse)
@app.post("/generate_test_cases/{task_id}", response_class=JSONResponse)
async def generate_test_cases(params: Annotated[GenerateTasksDependencies, 
                                                Depends(GenerateTasksDependencies)]):
    """Receive get request from front-end"""
    try:
        if params.task_id == 'task-1':
            response_status = params.model.prepare_input(request_files = params.request_files,
                                                            test_cases_db = params.test_cases_db)
            # await asyncio.sleep(10)
            return JSONResponse(status_code=200,content= {f'{params.task_id}': response_status})
        
        elif params.task_id == 'task-2':
            response_status = params.model.create_testcases()
            # await asyncio.sleep(10)
            return JSONResponse(status_code=200,content= {f'{params.task_id}': response_status})
        elif params.task_id == 'task-3':
            response_status = params.model.check_dependencies()
            # await asyncio.sleep(10)
            return JSONResponse(status_code=200,content= {f'{params.task_id}': response_status})
        elif params.task_id == 'task-4':
            response_status = params.model.execute_pytest()
            # await asyncio.sleep(10)
            return JSONResponse(status_code=200,content= {f'{params.task_id}': response_status})

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,content={f'{params.task_id}': False})


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