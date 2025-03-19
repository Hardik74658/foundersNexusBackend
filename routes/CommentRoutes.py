from fastapi import APIRouter
from models.CommentModel import Comment
from controllers import CommentController


router = APIRouter()


@router.get("/comments/")
async def get_all_comments():
    return await CommentController.getAllComments()

@router.post("/posts/{postId}/comments")
async def add_comment(postId: str, comment: Comment):
    return await CommentController.addComment(postId,comment)

@router.get("/comments/{commentId}")
async def get_comment_by_id(commentId: str):
    return await CommentController.getCommentById(commentId)

@router.delete("/posts/{postId}/comments/{commentId}")
async def delete_comment(postId: str,commentId: str):
    return await CommentController.deleteComment(postId,commentId)

@router.get("/posts/{postId}/comments")
async def get_comments_by_post_id(postId: str):
    return await CommentController.getCommentsByPostId(postId)