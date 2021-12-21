from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ..routers import predict, home, analysis
import uvicorn
from ..core.config import settings
import socketio
from typing import Any
sio: Any = socketio.AsyncServer(async_mode = "asgi")
socket_app = socketio.ASGIApp(sio)
app = FastAPI()

def include_router(app):
    app.include_router(predict.router)
    app.include_router(home.router)
    app.include_router(analysis.router)
def configure_static(app):
    app.mount(
        '/prediction/static',  StaticFiles(directory="prediction/static"), name="static")
def websocket(app):
    app.mount("/", socket_app)
    @sio.on("connnect")
    async def connect(sid, env):
        print("Raspberry on connect")

    @sio.on("control")
    async def control(sid, msg):
        await sio.emit("control", msg)

    @sio.on("envi")
    async def envi(sid, msg):
        # save data to mongoDB
        await sio.emit('envi', msg)

@sio.on("disconnect")
async def disconnect(sid):
    print("client disconnected")
if __name__ == "__main__":
    uvicorn.run("prediction.app.main:app", host="0.0.0.0", port=8080, reload=True)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME,
                  version=settings.PROJECT_VERSION)
    include_router(app)
    websocket(app)
    configure_static(app)  # new
    return app

app = start_application()
