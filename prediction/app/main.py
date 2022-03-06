from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.staticfiles import StaticFiles
from ..routers import predict,  analysis
import uvicorn
from ..core.config import settings
import socketio
from .authenticate import authenticate
from typing import Any
from .websocket import websocket
sio: Any = socketio.AsyncServer(async_mode = "asgi")
socket_app = socketio.ASGIApp(sio)



def include_router(app):
    app.include_router(predict.router)
    app.include_router(analysis.router)
    
def configure_static(app):
    app.mount(
        '/prediction/static',  StaticFiles(directory="prediction/static"), name="static")


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME,
                  version=settings.PROJECT_VERSION)
    authenticate(app)
    include_router(app)
    configure_static(app)  # new
    websocket(sio, socket_app, app)
    return app

app = start_application()

#uvicorn --host 0.0.0.0 prediction.app.main:app --reload
