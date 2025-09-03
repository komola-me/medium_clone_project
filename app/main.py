from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers.auth import router as auth_router
from app.routers.article import router as article_router
from app.middleware import LoggingMiddleware
from app.admin.settings import admin


app = FastAPI(debug=True, title="Medium Clone")

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(article_router)

admin.mount_to(app=app)

app.mount('/static', StaticFiles(directory="app/static"), name="static")

app.mount('/media', StaticFiles(directory="app/media"), name="media")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def welcome_page(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})
