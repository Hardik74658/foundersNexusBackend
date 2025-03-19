from config.database import comments_collection,posts_collection
from models.CommentModel import Comment,CommentOut
from bson import ObjectId
from fastapi import HTTPException,Response
from fastapi.responses import JSONResponse


async def getAllComments():
    comments = await comments_collection.find().to_list()
    return [CommentOut(**comment) for comment in comments]

async def getCommentById(commentId: str):
    comment = await comments_collection.find_one({"_id": ObjectId(commentId)})
    if comment:
        return CommentOut(**comment)
    raise HTTPException(status_code=404, detail="Comment not found")

async def addComment(postId: str, comment: Comment):
    # Convert comment model to dictionary
    comment_data = comment.dict(exclude_unset=True)

    # Convert the postId and userId to ObjectId before inserting into the database
    comment_data["postId"] = ObjectId(postId)
    comment_data["userId"] = ObjectId(comment_data["userId"])
    
    # Insert the comment document
    result = await comments_collection.insert_one(comment_data)
    comment_id = result.inserted_id
    if comment_id is None:
        raise HTTPException(status_code=500, detail="Failed to create comment")
    
    # Update the corresponding post document:
    # Convert postId to ObjectId in the query as well.
    update_result = await posts_collection.update_one(
        {"_id": ObjectId(postId)},
        {"$push": {"comments": str(comment_id)}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found or comment not added")
    
    return JSONResponse(
        content={
            "message": "Comment created successfully",
            "commentId": str(comment_id)
        },
        status_code=201
    )


async def deleteComment(postId: str, commentId: str):
       # Optionally check that the comment's post_id matches postId before deletion
    comment = await comments_collection.find_one({"_id": ObjectId(commentId)})
    if not comment or comment["postId"] != ObjectId(postId):
        raise HTTPException(status_code=404, detail="Comment not found for the given post")
    
    await comments_collection.delete_one({"_id": ObjectId(commentId)})
    # Remove the commentId from the post's comments array
    await posts_collection.update_one(
        {"_id": ObjectId(postId)},
        {"$pull": {"comments": commentId}}
    )
    
    return Response(status_code=204)

# async def getCommentsByUserId(userId: str):
#     comments = await comments_collection.find({"userId": userId}).to_list()
#     return [CommentOut(**comment) for comment in comments]

async def getCommentsByPostId(postId: str):
    comments = await comments_collection.find({"postId": ObjectId(postId)}).to_list()
    return [CommentOut(**comment) for comment in comments]




