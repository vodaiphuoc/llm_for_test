from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import uvicorn
import os
import time

from data_model import Script_File, File_List
from db import DB_handler
from typing import List

@asynccontextmanager
async def lifespan(app: FastAPI):
    # init engine here
    app.implement_db = DB_handler('db/implement.db')
    app.test_cases_db = DB_handler('db/test_cases.db')
    yield

    app.implement_db.close()
    app.implement_db = None

    app.test_cases_db.close()
    app.test_cases_db = None

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
async def upload_files_router(request: Request):
    """Receive post request from expressjs"""
    try:
        request_dict = await request.json()
        dir_tree = request_dict['dict_tree']
        path2currFolder = request_dict['path2currDir']
        
        # flatten tree
        list_files = flatten_tree(dir_tree,'')
        
        list_data = File_List(list_file = [Script_File(file_path = path2currFolder+dir) for dir in list_files])
        # insert to DB
        request.app.implement_db.insert_files(list_data)
        request.app.test_cases_db.insert_files(list_data)

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


# def _make_test_cases(request: Request, file_list: List[str]):
#     # get raw content of all request files
#     file_contents = [request.app.db.get_content_from_url(url = file_name, 
#                                                     content_type='RawContent')
#                     for file_name in file_list
#     ]

    # agent tester inference and
    # output content (code) of test cases

    

    # save content of test cases to DB (`test_cases` table)



# def _run_test_prepare_report():
    # run pytest


    # load report file of pytest, attach to reponse

@app.get("/generate_test_cases/{task_id}")
@app.post("/generate_test_cases/{task_id}")
async def generate_test_cases(task_id: str,request: Request):
    """Receive get request from front-end"""
    try:

        if task_id == 'task-1':
            request_dict = await request.json()
            request_files = request_dict['file_list']
            # _make_test_cases(request, request_files)
            await asyncio.sleep(50)
            return JSONResponse(status_code=200,content= {'data': [1,2,3,4]})
        else:
            await asyncio.sleep(30)
            return JSONResponse(status_code=200,content= {'data': [5,6,7,8]})
    
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,content={'html_content': 'ERROR LOAD FILE'})



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