from motor.motor_asyncio import AsyncIOMotorClient


DATABASE_URL = "mongodb://localhost:27017/"
DATABASE_NAME ="fastapi"

# Create a MongoDB client
client = AsyncIOMotorClient(DATABASE_URL)

database = client[DATABASE_NAME]

roles_collection = database["roles"]
users_collection = database["users"]
entrepreneurs_collection = database["entrepreneurs"]
investors_collection = database["investors"]
startups_collection = database["startups"]
posts_collection = database["posts"]
comments_collection = database["comments"]