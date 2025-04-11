from config.database import posts_collection,users_collection,comments_collection
from models.PostModel import Post,PostOut
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from bson.errors import InvalidId

def convert_objectid_to_str(data):
    """Recursively converts ObjectId instances in the data to strings."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data

#CRUD OF POST

async def getAllPosts():
    posts = await posts_collection.find().to_list()
    if len(posts) > 0:
        for i, post in enumerate(posts):
            if "userId" in post and isinstance(post["userId"],ObjectId):
                user = await users_collection.find_one({"_id":post["userId"]})
                posts[i]["user"] = user
    posts = convert_objectid_to_str(posts)
    return [PostOut(**post) for post in posts]


async def getPostById(postId: str):
    try:
        # Validate that postId is a valid ObjectId
        post_id = ObjectId(postId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid postId format")

    # Fetch the post from the database
    post = await posts_collection.find_one({"_id": ObjectId(postId)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if "userId" in post and isinstance(post["userId"], ObjectId):
        user = await users_collection.find_one({"_id": post["userId"]})
        post["user"] = user    

    # Fetch comments data
    comments_data = []
    if "comments" in post and post["comments"]:
        for comment_id in post["comments"]:
            comment = await comments_collection.find_one({"_id": ObjectId(comment_id)})
            if comment:
                if "userId" in comment:
                    commentUser = await users_collection.find_one({"_id": ObjectId(comment["userId"])})
                    comment["user"] = commentUser
                comments_data.append(comment)

    # Add commentsData to the post
    post["commentsData"] = comments_data

    post = convert_objectid_to_str(post)
    return PostOut(**post)

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
    if len(posts) > 0:
        for i, post in enumerate(posts):
            if "userId" in post and isinstance(post["userId"],ObjectId):
                user = await users_collection.find_one({"_id":post["userId"]})
                posts[i]["user"] = user
    posts = convert_objectid_to_str(posts)
    return [PostOut(**post) for post in posts]


#FUNCTIONALITIES ON POST
from bson import ObjectId
from fastapi import HTTPException

async def likeToggleOnPost(postId: str, userId: str):
    # Ensure the user exists
    user = await users_collection.find_one({"_id": ObjectId(userId)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch the post
    post = await posts_collection.find_one({"_id": ObjectId(postId)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Toggle like
    if userId in post.get("likes", []):
        # Unlike the post
        await posts_collection.update_one(
            {"_id": ObjectId(postId)},
            {"$pull": {"likes": userId}}
        )
        return {"message": "Post unliked successfully"}
    else:
        # Like the post
        await posts_collection.update_one(
            {"_id": ObjectId(postId)},
            {"$addToSet": {"likes": userId}}
        )
        return {"message": "Post liked successfully"}