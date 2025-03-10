from config.database import posts_collection
from models.PostModel import Post,PostOut
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse


async def getAllPosts():
    posts = await posts_collection.find().to_list()
    return [PostOut(**post) for post in posts]

async def getPostById(postId: str):
    post = await posts_collection.find_one({"_id": ObjectId(postId)})
    if post:
        return PostOut(**post)
    raise HTTPException(status_code=404, detail="Post not found")   

async def addPost(post: Post):
    createPost = await posts_collection.insert_one(post.dict(exclude_unset=True))
    postId = str(createPost.inserted_id)
    return JSONResponse({
        "message": "Post created successfully",
        "postId": str(postId)
    },status_code=201)

async def deletePost(postId: str):
    deletePost = await posts_collection.delete_one({"_id": ObjectId(postId)})
    if deletePost.deleted_count == 1:
        return JSONResponse({
            "message": "Post deleted successfully"
        })
    raise HTTPException(status_code=404, detail="Post not found")

async def getPostsByUserId(userId: str):
    posts = await posts_collection.find({"userId": userId}).to_list()
    return [PostOut(**post) for post in posts]