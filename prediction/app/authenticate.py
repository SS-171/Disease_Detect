from fastapi import FastAPI, Request, Form, Depends, status
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi_login import LoginManager
from numpy import save
from prediction.database.config.db import UserCollection
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta, datetime
from .websocket import saveLogToDb
class NotAuthenticatedException(Exception):
    pass
# authenticate
manager = LoginManager('123456', token_url = "/verify", use_cookie=True, 
    custom_exception=NotAuthenticatedException,
    cookie_name = "authentication"
)
@manager.user_loader
def load_user(username:str):
    user = UserCollection.find_one({"username": username})
    return user

user  = {
    "username" : "admin",
    "password" : "1234",
    "isAdmin": False,
    "dateCreated": str
}

templates = Jinja2Templates(directory="prediction\\templates")



# update password
def updatePassword(newPwd):
    dbUser = UserCollection.find_one({"username": curentUser})
    oldPassword = {"password" : dbUser.get('password')}
    newPassword = { "$set": {"password" : newPwd}}
    UserCollection.update_one(oldPassword, newPassword)
# update username
def updateUsername(newUser):
    oldUsername = {"username" : curentUser}
    newUsername = { "$set": {"username" : newUser}}
    UserCollection.update_one(oldUsername, newUsername)
def getUserCreateTime():
    now = datetime.now()
    return now.strftime("%d-%m-%Y")

def authenticate(app):
    @app.get("/login", response_class=HTMLResponse)
    async def read_item(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})

    @app.post("/verify")
    async def verify(username: str = Form(...), password:str = Form(...) ):
        user = load_user(username)
        if not user:
            raise InvalidCredentialsException
        elif password != user['password']:
            raise InvalidCredentialsException
        access_token = manager.create_access_token(
            data = {"sub": username}, expires = timedelta(minutes=15)
        )
        resp = RedirectResponse(url="/", status_code = status.HTTP_302_FOUND)
        global curentUser
        curentUser = username
        saveLogToDb(curentUser)
        manager.set_cookie(resp, access_token)
        resp.set_cookie(key="username", value = curentUser)
        return resp
                
    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request, _=Depends(manager)):
        return templates.TemplateResponse("home.html", {"request": request})

    @app.exception_handler(NotAuthenticatedException)
    def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
        return RedirectResponse(url= "/login")

    # update user
    @app.post("/changeUser")
    async def changeUser(request:Request, username: str = Form(...) ):
        updateUsername(username)
        return RedirectResponse(url= "/", status_code = status.HTTP_302_FOUND)


    @app.post("/changePwd")
    async def changePwd( request:Request,password:str = Form(...)):
        updatePassword(password)
        return RedirectResponse(url= "/",status_code = status.HTTP_302_FOUND)

    @app.post('/admin/create/user')
    def adminCreateUser(username: str = Form(...), password:str = Form(...)):
        user['username'] = username
        user['password'] = password
        user['dateCreated'] = getUserCreateTime()
        UserCollection.insert_one(user)
        return RedirectResponse(url= "/", status_code = status.HTTP_302_FOUND)
    @app.get('/admin/delete/user/')
    def adminDeleteUser(username: str):
        print("username", username)
        UserCollection.delete_one({"username": username})
        return RedirectResponse(url= "/", status_code = status.HTTP_302_FOUND)

    # logout
    @app.get('/logout')
    async def logout(request: Request):
        resp = RedirectResponse(url="/login", status_code = status.HTTP_302_FOUND)
        manager.set_cookie(resp, "none")
        return resp

    @app.exception_handler(NotAuthenticatedException)
    def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
        return RedirectResponse(url= "/login")

