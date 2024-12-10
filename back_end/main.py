from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import uvicorn


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
app.mount(path = '/statics', 
          app = StaticFiles(directory='./statics', html = False), 
          name='statics')

# for testing on web browser only
templates = Jinja2Templates(directory='./templates')
@app.get("/", response_class=HTMLResponse)
async def index_router(request: Request):
	return templates.TemplateResponse(
		request = request,
		name = "index.html"
		)

# @app.get("/open", response_class=HTMLResponse)
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
                dir_list.append(k)
            else:
                dir_list.append(parent+'/'+k)
    return dir_list

@app.post("/upload_files", response_class=JSONResponse)
async def upload_files_router(request: Request):
    dir_tree = await request.json()
    # dir_tree = dir_tree['dir']
    # flatten tree
    print('dir tree: ',dir_tree)
    list_files = flatten_tree(dir_tree,'')
    print(list_files)
    list_data = File_List(list_file = [Script_File(file_path = dir) for dir in list_files])
    # insert to DB
    request.app.db.insert_files(list_data)
    # return oke
    return JSONResponse({'status':''})

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