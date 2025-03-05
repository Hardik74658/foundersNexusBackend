from fastapi  import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.RoleRoutes import router as RoleRouter
from routes.UserRoutes import router as UserRouter

app = FastAPI()

app.include_router(RoleRouter)
app.include_router(UserRouter)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test/")
async def test():
    return "Hello FastPI!!"

@app.get("/users/")
async def users():
    return {"message":"Hello JSON Response","users":["user1","user2","user3"]}


