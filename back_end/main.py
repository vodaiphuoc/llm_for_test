from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import uvicorn


app = FastAPI()

origins = [
    "http://localhost",
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


templates = Jinja2Templates(directory='./templates')
@app.get("/", response_class=HTMLResponse)
async def index_router(request: Request):
	return templates.TemplateResponse(
		request = request,
		name = "index.html"
		)


@app.post("/upload_files", response_class=JSONResponse)
async def upload_files_router(request: Request):
    dir_tree = await request.json()
    
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