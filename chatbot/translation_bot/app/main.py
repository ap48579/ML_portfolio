from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from fastapi.templating import Jinja2Templates

app = FastAPI()

#Setup for Jinja2 templates
templates= Jinja2Templates(directory="templates")

@app.get('/index', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})