import requests
import time
import os
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# CometChat configuration
COMETCHAT_APP_ID = "272738e1c3d1b4aa"
COMETCHAT_REGION = "in"
COMETCHAT_API_KEY = "37f1bad27f18415e2e06894a9bf8e5f6194cb74d" # Use environment variable or fallback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cometchat")

class CometChatService:
    # Updated URL format - try multiple formats if needed
    BASE_URL = f"https://api-{COMETCHAT_REGION}.cometchat.io/v3"
    # Alternative URL format if the above doesn't work
    ALT_BASE_URL = f"https://{COMETCHAT_REGION}.api.cometchat.io/v3"
    
    @staticmethod
    def _get_session():
        """Create and return a requests session with retry logic"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,  # Maximum number of retries
            backoff_factor=0.5,  # Time between retries (0.5, 1, 2 seconds)
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
            allowed_methods=["GET", "POST", "DELETE"]  # Retry for these HTTP methods
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
    
    @staticmethod
    def _get_headers():
        """Return the headers needed for CometChat API requests"""
        if not COMETCHAT_API_KEY:
            raise ValueError("COMETCHAT_API_KEY environment variable is not set")
            
        return {
            "apiKey": COMETCHAT_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "appId": COMETCHAT_APP_ID  # Add the App ID to the headers
        }
    
    @staticmethod
    async def test_connection() -> Dict[str, Any]:
        """Test the connection to CometChat API to ensure connectivity"""
        urls_to_try = [
            CometChatService.BASE_URL,
            CometChatService.ALT_BASE_URL,
            f"https://{COMETCHAT_REGION}-api.cometchat.io/v3"  # Original format
        ]
        
        session = CometChatService._get_session()
        headers = CometChatService._get_headers()
        
        for url in urls_to_try:
            try:
                logger.info(f"Testing connection to: {url}")
                # Try to access the /users endpoint which should be available if API key is valid
                test_url = f"{url}/users?limit=1"
                response = session.get(test_url, headers=headers, timeout=10)
                
                if response.status_code in (200, 401, 403):  # Any of these means we can reach the API
                    CometChatService.BASE_URL = url  # Set the working URL as the BASE_URL
                    logger.info(f"Successfully connected to CometChat API at {url}")
                    return {"status": "success", "url": url}
            except Exception as e:
                logger.warning(f"Failed to connect to {url}: {str(e)}")
        
        logger.error("Could not establish connection to any CometChat API URL")
        return {"status": "error", "message": "Could not establish connection to CometChat API"}
    
    @staticmethod
    async def create_user(user_id: str, name: str, avatar: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a user in CometChat"""
        url = f"{CometChatService.BASE_URL}/users"
        
        payload = {
            "uid": user_id,
            "name": name,
        }
        
        if avatar:
            payload["avatar"] = avatar
            
        if metadata:
            payload["metadata"] = metadata
        
        try:
            session = CometChatService._get_session()
            response = session.post(url, json=payload, headers=CometChatService._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 409:  # User already exists
                logger.warning(f"User {user_id} already exists in CometChat")
                return {"status": "exists", "message": "User already exists in CometChat"}
            else:
                error_msg = f"Failed to create CometChat user: {response.text}"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg, "code": response.status_code}
                
        except Exception as e:
            error_msg = f"Exception while creating CometChat user: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    @staticmethod
    async def user_exists(user_id: str) -> bool:
        """Check if a user exists in CometChat"""
        url = f"{CometChatService.BASE_URL}/users/{user_id}"
        
        try:
            session = CometChatService._get_session()
            response = session.get(url, headers=CometChatService._get_headers(), timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error checking if user exists in CometChat: {str(e)}")
            return False
    
    @staticmethod
    async def delete_user(user_id: str) -> Dict[str, Any]:
        """Delete a user from CometChat"""
        url = f"{CometChatService.BASE_URL}/users/{user_id}"
        
        try:
            session = CometChatService._get_session()
            response = session.delete(url, headers=CometChatService._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Failed to delete CometChat user: {response.text}"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Exception while deleting CometChat user: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

# Function to handle user creation during registration
async def register_user_with_cometchat(user_id: str, full_name: str, profile_picture: str = None, email: str = None):
    """
    Register a user with CometChat after they've been created in your database
    
    Args:
        user_id: The MongoDB _id of the user as a string
        full_name: The user's full name
        profile_picture: URL to the user's profile picture (optional)
        email: The user's email (optional, could be stored in metadata)
    """
    # Ensure we can connect to CometChat before trying to register the user
    connection_test = await CometChatService.test_connection()
    if connection_test.get("status") != "success":
        logger.warning(f"Could not establish connection to CometChat: {connection_test.get('message')}")
        return {"status": "error", "message": "Could not connect to CometChat API"}
    
    metadata = {"email": email} if email else None
    result = await CometChatService.create_user(
        user_id=user_id,
        name=full_name,
        avatar=profile_picture,
        metadata=metadata
    )
    
    if result.get("status") == "error":
        logger.error(f"Error creating CometChat user during registration: {result.get('message')}")
        # We don't raise an exception here because we don't want user registration to fail
        # if CometChat integration fails. Instead, we log the error and continue.
    
    return result
