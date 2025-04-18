import asyncio
import sys
import os
import logging
from time import sleep
from typing import List, Dict

# Add the parent directory to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import users_collection
from utils.CometChatIntegration import CometChatService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cometchat_migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("migration")

# Rate limiting configuration
BATCH_SIZE = 25  # Number of users to process in a batch
RATE_LIMIT_DELAY = 1  # Seconds to wait between batches

async def migrate_users_to_cometchat():
    """Migrate all users from MongoDB to CometChat"""
    logger.info("Starting user migration to CometChat")
    
    # First, test the connection to CometChat
    connection_test = await CometChatService.test_connection()
    if connection_test.get("status") != "success":
        logger.error(f"Could not establish connection to CometChat API: {connection_test.get('message')}")
        logger.error("Migration aborted due to connection issues")
        return
    
    # Get all users from MongoDB
    users = await users_collection.find().to_list(length=None)
    logger.info(f"Found {len(users)} users in database")
    
    # Counters for tracking migration progress
    total_users = len(users)
    success_count = 0
    already_exists_count = 0
    error_count = 0
    
    # Process users in batches to handle rate limiting
    for i in range(0, total_users, BATCH_SIZE):
        batch = users[i:i+BATCH_SIZE]
        logger.info(f"Processing batch {i//BATCH_SIZE + 1}/{(total_users + BATCH_SIZE - 1)//BATCH_SIZE}")
        
        for user in batch:
            user_id = str(user["_id"])
            full_name = user.get("fullName", "Unknown User")
            profile_picture = user.get("profilePicture", "")
            email = user.get("email", "")
            
            logger.info(f"Migrating user: {user_id} - {full_name}")
            
            # Check if user already exists in CometChat (optional)
            if await CometChatService.user_exists(user_id):
                logger.info(f"User {user_id} already exists in CometChat, skipping")
                already_exists_count += 1
                continue
            
            # Create user in CometChat
            metadata = {"email": email} if email else None
            result = await CometChatService.create_user(
                user_id=user_id,
                name=full_name,
                avatar=profile_picture,
                metadata=metadata
            )
            
            if result.get("status") == "error":
                logger.error(f"Failed to migrate user {user_id}: {result.get('message')}")
                error_count += 1
            elif result.get("status") == "exists":
                already_exists_count += 1
            else:
                logger.info(f"Successfully migrated user {user_id}")
                success_count += 1
        
        # Add delay between batches for rate limiting
        if i + BATCH_SIZE < total_users:
            logger.info(f"Waiting {RATE_LIMIT_DELAY} seconds before next batch...")
            sleep(RATE_LIMIT_DELAY)
    
    # Log migration results
    logger.info(f"Migration completed:")
    logger.info(f"  - Total users: {total_users}")
    logger.info(f"  - Successfully migrated: {success_count}")
    logger.info(f"  - Already existing: {already_exists_count}")
    logger.info(f"  - Errors: {error_count}")

if __name__ == "__main__":
    # Run the migration script
    asyncio.run(migrate_users_to_cometchat())
