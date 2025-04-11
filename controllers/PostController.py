from typing import Optional
from config.database import posts_collection,users_collection,comments_collection
from models.PostModel import Post,PostOut
from bson import ObjectId
from fastapi import File, Form, HTTPException
from fastapi.responses import JSONResponse
from bson.errors import InvalidId
from utils.CloudinaryUpload import upload_image_from_buffer
from fastapi import UploadFile
import datetime

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
            if "userId" in post and isinstance(post["userId"], ObjectId):
                user = await users_collection.find_one({"_id": post["userId"]})
                posts[i]["user"] = user
    posts = convert_objectid_to_str(posts)
    posts.reverse()  # Reverse the order of posts
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

async def addPost(
            userId: str = Form(...),
            content: str = Form(...),
            title: str = Form(...),
            imageFile: UploadFile = File(None) 
         ):
    post_data = {
        "userId": ObjectId(userId),
        "content": content,
        "title": title,
        "image_url": "",  # Default to an empty string
        "likes": [],
        "comments": [],
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
    }

    # Upload imageFile to Cloudinary if provided
    if imageFile:
        try:
            # Log the upload process
            print(f"Uploading image: {imageFile.filename}")
            uploaded_url = await upload_image_from_buffer(imageFile)
            print(f"Uploaded URL: {uploaded_url}")  # Log the uploaded URL
            if uploaded_url:
                post_data["image_url"] = uploaded_url
                print(f"Image uploaded successfully: {uploaded_url}")
            else:
                print("Image upload failed: No URL returned")
        except Exception as e:
            print(f"Error during image upload: {str(e)}")
            raise HTTPException(status_code=500, detail="Image upload failed")

    # Log the post data before inserting into the database
    print(f"Post data to be inserted: {post_data}")

    createPost = await posts_collection.insert_one(post_data)
    postId = createPost.inserted_id
    return JSONResponse({
        "message": "Post created successfully",
        "postId": str(postId)
    }, status_code=201)

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
    try:
        post_id = ObjectId(postId)
        user_id = ObjectId(userId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid postId or userId format")

    # Ensure the user exists
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch the post
    post = await posts_collection.find_one({"_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Toggle like
    if userId in post.get("likes", []):
        # Unlike the post
        await posts_collection.update_one(
            {"_id": post_id},
            {"$pull": {"likes": userId}}
        )
        return {"message": "Post unliked successfully"}
    else:
        # Like the post
        await posts_collection.update_one(
            {"_id": post_id},
            {"$addToSet": {"likes": userId}}
        )
        return {"message": "Post liked successfully"}