from config.database import comments_collection
from models.CommentModel import Comment,CommentOut
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse


# async def getAllComments():
#     comments = await comments_collection.find().to_list()
#     return [CommentOut(**comment) for comment in comments]

async def getCommentById(commentId: str):
    comment = await comments_collection.find_one({"_id": ObjectId(commentId)})
    if comment:
        return CommentOut(**comment)
    raise HTTPException(status_code=404, detail="Comment not found")

async def addComment(comment: Comment):
    createComment = await comments_collection.insert_one(comment.dict(exclude_unset=True))
    commentId = str(createComment.inserted_id)
    return JSONResponse({
        "message": "Comment created successfully",
        "commentId": str(commentId)
    },status_code=201)

async def deleteComment(commentId: str):
    deleteComment = await comments_collection.delete_one({"_id": ObjectId(commentId)})
    if deleteComment.deleted_count == 1:
        return JSONResponse({
            "message": "Comment deleted successfully"
        })
    raise HTTPException(status_code=404, detail="Comment not found")

# async def getCommentsByUserId(userId: str):
#     comments = await comments_collection.find({"userId": userId}).to_list()
#     return [CommentOut(**comment) for comment in comments]

async def getCommentsByPostId(postId: str):
    comments = await comments_collection.find({"postId": postId}).to_list()
    return [CommentOut(**comment) for comment in comments]




