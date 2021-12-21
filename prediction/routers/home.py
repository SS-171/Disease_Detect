from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from prediction.database.config.db import UserCollection
from prediction.database.models.user import User
from prediction.database.schemas.user import userEntity, usersEntity
from bson import ObjectId

templates = Jinja2Templates(directory="prediction\\templates")
router = APIRouter()
RECIPES  = {
    "car": {
        "label": 'BMW',
        "price": 12
    },
    "book": {
        "label": 'hi',
        "price": 15
    }
}
# for test database: CRUD with mongoDb
@router.get('user/one')
async def find_one(id):
    return userEntity(UserCollection.find_one({'_id': ObjectId(id)}))
@router.get('/user/all')
async def userAll():
    return usersEntity(UserCollection.find())

@router.post('/user/create')
async def user_create(user: User):
    UserCollection.insert_one(dict(user))
    return usersEntity(UserCollection.find())

@router.put('/user/put/{id}')
async def update_user(id, user: User):
    updateUser =UserCollection.find_one_and_update({"_id": ObjectId(id)}, {"$set": dict(user)})
    return userEntity(UserCollection.find_one({"_id": ObjectId}))

@router.delete('/user/delete')
async def delete_user(id, user: User):
    deleteUser =UserCollection.find_one_and_delete(dict({"_id": ObjectId(id)}))
    return deleteUser

# end testing
@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("general_pages/home.html", {"request": request})

@router.get('/user/{id}')
async def user(request: Request, id: int) ->dict:
    # invoke function to get user from db
    return templates.TemplateResponse("general_pages/user.html", {"request": request,"id": id, "recipes": RECIPES })



# Receive message from client to ws server and send back to client

