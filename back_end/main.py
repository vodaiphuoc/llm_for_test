from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import uvicorn
import os

from data_model import Script_File, File_List
from db import DB_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # init engine here
    app.db = DB_handler('db/main.db')
    yield
    app.db = None

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
        reponse_dict = await request.json()
        dir_tree = reponse_dict['dict_tree']
        path2currFolder = reponse_dict['path2currDir']
        
        # flatten tree
        list_files = flatten_tree(dir_tree,'')
        
        list_data = File_List(list_file = [Script_File(file_path = path2currFolder+dir) for dir in list_files])
        # insert to DB
        request.app.db.insert_files(list_data)

        return JSONResponse(status_code=200,content='')
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,content='')


@app.get("/load_py/", response_class=JSONResponse)
async def get_file_content(file_name:str, request: Request):
    """Receive get request from front-end"""
    html_content = request.app.db.get_content_from_url(url = file_name, 
                                                       purpose= 'display').display_content
    return JSONResponse(content={'html_content': html_content})


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