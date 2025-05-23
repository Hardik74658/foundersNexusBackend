from fastapi import APIRouter, File, Form, UploadFile
from models.PostModel import Post
from controllers import PostController


router = APIRouter()

@router.get("/posts/",tags=["Posts"])
async def get_all_posts():
    return await PostController.getAllPosts()

@router.post("/posts/", tags=["Posts"])
async def add_post(
    userId: str = Form(...),
    content: str = Form(...),
    title: str = Form(...),
    imageFile: UploadFile = File(None)  # Accept imageFile as a file
):
    print("Image :", imageFile)
    return await PostController.addPost(userId, content, title, imageFile)

@router.get("/posts/{postId}",tags=["Posts"])
async def get_post_by_id(postId: str):
    return await PostController.getPostById(postId)


@router.delete("/posts/{postId}",tags=["Posts"])
async def delete_post(postId: str):
    return await PostController.deletePost(postId)

@router.get("/posts/user/{userId}",tags=["Posts"])
async def get_posts_by_user_id(userId: str):
    return await PostController.getPostsByUserId(userId)

@router.post("/posts/{postId}/like/{userId}", tags=["Posts"])
async def like_toggle_on_post(postId: str, userId: str):
    return await PostController.likeToggleOnPost(postId, userId)
