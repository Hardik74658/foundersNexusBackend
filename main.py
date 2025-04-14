import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.RoleRoutes import router as RoleRouter
from routes.UserRoutes import router as UserRouter
from routes.EntrepreneurRoutes import router as EntrepreneurRouter
from routes.InvestorRoutes import router as InvestorRouter
from routes.StartupRoutes import router as StartupRouter
from routes.PostRoutes import router as PostRouter
from routes.CommentRoutes import router as CommentRouter

app = FastAPI()

# Enable debug logging
# logging.basicConfig(level=logging.DEBUG)

app.include_router(RoleRouter)
app.include_router(EntrepreneurRouter)
app.include_router(InvestorRouter)
app.include_router(UserRouter)
app.include_router(StartupRouter)
app.include_router(PostRouter)
app.include_router(CommentRouter)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/test/")
# async def test():
#     return "Hello FastPI!!"

# @app.get("/users/")
# async def users():
#     return {"message":"Hello JSON Response","users":["user1","user2","user3"]}


