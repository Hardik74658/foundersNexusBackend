from fastapi import APIRouter
from models.PostModel import Post
from controllers import PostController


router = APIRouter()

@router.get("/posts/")
async def get_all_posts():
    return await PostController.getAllPosts()

@router.post("/posts/")
async def add_post(post: Post):
    return await PostController.addPost(post)

@router.get("/posts/{postId}")
async def get_post_by_id(postId: str):
    return await PostController.getPostById(postId)


@router.delete("/posts/{postId}")
async def delete_post(postId: str):
    return await PostController.deletePost(postId)

@router.get("/posts/user/{userId}")
async def get_posts_by_user_id(userId: str):
    return await PostController.getPostsByUserId(userId)

