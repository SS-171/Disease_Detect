from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ..routers import predict, home, analysis
import uvicorn
from ..core.config import settings

app = FastAPI()

def include_router(app):
    app.include_router(predict.router)
    app.include_router(home.router)
    app.include_router(analysis.router)
def configure_static(app):
    app.mount(
        '/prediction/static',  StaticFiles(directory="prediction/static"), name="static")
if __name__ == "__main__":
    uvicorn.run("prediction.app.main:app", host="0.0.0.0", port=8080, reload=True)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME,
                  version=settings.PROJECT_VERSION)
    include_router(app)
    configure_static(app)  # new
    return app

app = start_application()
