from config.database import posts_collection
from models.PostModel import Post,PostOut
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse

def convert_objectid_to_str(data):
    """Recursively converts ObjectId instances in the data to strings."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data


async def getAllPosts():
    posts = await posts_collection.find().to_list()
    return [PostOut(**post) for post in posts]

async def getPostById(postId: str):
    post = await posts_collection.find_one({"_id": ObjectId(postId)})
    if post:
        return PostOut(**post)
    raise HTTPException(status_code=404, detail="Post not found")   

async def addPost(post: Post):
    post = post.dict()
    post["userId"] = ObjectId(post["userId"])
    if "comments" in post:
        for i, item in enumerate(post["comments"]):
            post["comments"][i] = ObjectId(item)
    createPost = await posts_collection.insert_one(post)
    postId = createPost.inserted_id
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
    posts = await posts_collection.find({"userId": ObjectId(userId)}).to_list()
    return [PostOut(**post) for post in posts]