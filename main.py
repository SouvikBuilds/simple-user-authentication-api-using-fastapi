from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,EmailStr
from typing import List
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

class User(BaseModel):
    username:str
    email:EmailStr
    password:str


def user_serializer(user):
    return {
        "id": str(user["_id"]),  # ObjectId ko string me convert karna hamesha
        "username": user["username"],
        "email": user["email"],
        "password": user["password"]
    }

@app.get("/")
def hello():
    return {"message":"Hello,Welcome In SouvikAuth"}

@app.get("/users")
def get_users():
    users = collection.find({})
    return {"data": list(map(user_serializer, users))}

@app.post("/register")
def add_user(user: User):
    user_dict = user.dict()
    result = collection.insert_one(user_dict)
    
    # Get the inserted user and serialize
    new_user = collection.find_one({"_id": result.inserted_id})
    
    return {
        "message": "User registered successfully",
        "data": user_serializer(new_user)
    }


@app.post("/login")
def login(user: User):
    existing_user = collection.find_one({"email": user.email})

    if not existing_user:
        return {"message": "User does not exist, please register first."}

    if existing_user["password"] != user.password:
        return {"message": "Invalid password"}

    return {
        "message": "Login successful",
        "data": user_serializer(existing_user)
    }

@app.delete("/delete_user/{id}")
def delete_user(id: str):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return {"message": "User not found"}
    return {"message": "User deleted successfully"}


