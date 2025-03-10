from fastapi import APIRouter
from models.CommentModel import Comment
from controllers import CommentController


router = APIRouter()


# @router.get("/comments/")
# async def get_all_comments():
#     return await CommentController.getAllComments()

@router.post("/comments/")
async def add_comment(comment: Comment):
    return await CommentController.addComment(comment)

@router.get("/comments/{commentId}")
async def get_comment_by_id(commentId: str):
    return await CommentController.getCommentById(commentId)

@router.delete("/comments/{commentId}")
async def delete_comment(commentId: str):
    return await CommentController.deleteComment(commentId)

@router.get("/comments/post/{postId}")
async def get_comments_by_post_id(postId: str):
    return await CommentController.getCommentsByPostId(postId)