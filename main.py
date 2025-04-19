import warnings

# Filter warnings as early as possible
warnings.filterwarnings("ignore", message=".*overrides an existing Pydantic.*decorator")
warnings.filterwarnings("ignore", message=".*Valid config keys have changed in V2.*")
import uvicorn
import logging
from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from routes.RoleRoutes import router as RoleRouter
from routes.UserRoutes import router as UserRouter
from routes.EntrepreneurRoutes import router as EntrepreneurRouter
from routes.InvestorRoutes import router as InvestorRouter
from routes.StartupRoutes import router as StartupRouter
from routes.PostRoutes import router as PostRouter
from routes.CommentRoutes import router as CommentRouter
from routes.PitchDeckRoutes import router as PitchDeckRouter

# Enable debug logging
# logging.basicConfig(level=logging.DEBUG)

app = FastAPI(
    title="FoundersNexus API",
    description="API for connecting entrepreneurs and investors",
    version="1.0.0",
)

app.include_router(RoleRouter)
app.include_router(EntrepreneurRouter)
app.include_router(InvestorRouter)
app.include_router(UserRouter)
app.include_router(StartupRouter)
app.include_router(PostRouter)
app.include_router(CommentRouter)
app.include_router(PitchDeckRouter)

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


