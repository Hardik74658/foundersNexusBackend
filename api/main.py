from fastapi import FastAPI
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware # type: ignore

# Import your routers and mount them as in your original main.py
from routes.RoleRoutes import router as RoleRouter
from routes.UserRoutes import router as UserRouter
from routes.EntrepreneurRoutes import router as EntrepreneurRouter
from routes.InvestorRoutes import router as InvestorRouter
from routes.StartupRoutes import router as StartupRouter
from routes.PostRoutes import router as PostRouter
from routes.CommentRoutes import router as CommentRouter
from routes.PitchDeckRoutes import router as PitchDeckRouter

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

handler = Mangum(app)
