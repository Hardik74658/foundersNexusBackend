from config.database import startups_collection, users_collection, investors_collection
from models.StartupModel import Startup, StartupOut
from bson import ObjectId
from fastapi import HTTPException, Response, status, UploadFile
from fastapi.responses import JSONResponse
from utils.CloudinaryUpload import upload_image_from_buffer  # Import the Cloudinary upload utility
from datetime import datetime

def convert_objectid_to_str(data):
    """Recursively converts ObjectId instances in the data to strings."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data


async def getAllStartups():
    startups = await startups_collection.find().to_list()

    for startup in startups:
        if "founders" in startup:
            for i, founder in enumerate(startup["founders"]):
                founderId = ObjectId(founder)
                founderData  = await users_collection.find_one({"_id": founderId})
                if founderData:
                    startup["founders"][i] = founderData

    
    startups = convert_objectid_to_str(startups)
    return [StartupOut(**startup) for startup in startups]

async def getStartupById(startupId: str):
    try:
        startup = await startups_collection.find_one({"_id": ObjectId(startupId)})

        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")

        # Convert ObjectId fields to strings for founders
        if "founders" in startup:
            for i, founder_id in enumerate(startup["founders"]):
                founder_data = await users_collection.find_one({"_id": founder_id})
                if founder_data:
                    startup["founders"][i] = convert_objectid_to_str(founder_data)

        # Convert ObjectId fields to strings for previous fundings
        if "previous_fundings" in startup:
            for funding in startup["previous_fundings"]:
                if "investors" in funding and funding["investors"]:
                    for investor in funding["investors"]:
                        if "investorId" in investor and isinstance(investor["investorId"], ObjectId):
                            investor["investorId"] = str(investor["investorId"])

        # Convert ObjectId fields to strings for equity split
        if "equity_split" in startup:
            for equity in startup["equity_split"]:
                if "userId" in equity and isinstance(equity["userId"], ObjectId):
                    equity["userId"] = str(equity["userId"])

        # Convert the entire startup document to a response model
        startup = convert_objectid_to_str(startup)
        return StartupOut(**startup)
    except Exception as e:
        print(f"Error in getStartupById: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def addStartup(startup: Startup, logo: UploadFile = None):
    try:
        # Convert the startup object to a dictionary
        startup_data = startup.dict()

        # Upload the logo to Cloudinary if provided
        if logo:
            print("Uploading logo to Cloudinary...")  # Debugging log
            startup_data["logo_url"] = await upload_image_from_buffer(logo)
            if not startup_data["logo_url"]:
                raise HTTPException(status_code=500, detail="Failed to upload logo to Cloudinary")
        else:
            startup_data["logo_url"] = ""

        # Convert founders to ObjectId
        startup_data["founders"] = [ObjectId(founder) for founder in startup_data["founders"]]

        # Convert previous fundings' investor IDs to ObjectId
        if startup_data.get("previous_fundings"):
            for funding in startup_data["previous_fundings"]:
                if "investors" in funding and funding["investors"]:
                    for investor in funding["investors"]:
                        if "investorId" in investor and investor["investorId"]:
                            investor["investorId"] = ObjectId(investor["investorId"])

        # Convert equity split user IDs to ObjectId
        if startup_data.get("equity_split"):
            for equity in startup_data["equity_split"]:
                if "userId" in equity and equity["userId"]:
                    equity["userId"] = ObjectId(equity["userId"])

        # Insert the startup into the database
        result = await startups_collection.insert_one(startup_data)
        startup_id = str(result.inserted_id)

        # Update founders' currentStartup field
        for founder_id in startup_data["founders"]:
            await users_collection.update_one(
                {"_id": founder_id},
                {"$set": {"currentStartup": ObjectId(startup_id)}}
            )
        
        # Only add this startup to investors who are listed in the previous_fundings
        if startup_data.get("previous_fundings"):
            # Extract all unique investor IDs across all funding rounds
            investor_ids = set()
            for funding in startup_data.get("previous_fundings", []):
                for investor in funding.get("investors", []):
                    if "investorId" in investor and investor["investorId"]:
                        investor_ids.add(investor["investorId"])
            
            # For each relevant investor, add this startup to their previous_investments
            for investor_id in investor_ids:
                investor = await investors_collection.find_one({"userId": investor_id})
                if investor:
                    # Find the latest funding record for this investor to get amount and date
                    latest_funding = None
                    latest_date = None
                    
                    for funding in startup_data.get("previous_fundings", []):
                        for inv in funding.get("investors", []):
                            if inv.get("investorId") == investor_id:
                                funding_date = funding.get("date")
                                if not latest_date or funding_date > latest_date:
                                    latest_funding = funding
                                    latest_date = funding_date
                    
                    # Create investment record with data from the funding round
                    investment_record = {
                        "startup_id": startup_id,
                        "startup_name": startup_data.get("startup_name", ""),
                        "investment_amount": latest_funding.get("amount", "") if latest_funding else "",
                        "date": latest_funding.get("date", datetime.now().strftime("%Y-%m-%d")) if latest_funding else datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    # Add this startup to the investor's previous_investments
                    await investors_collection.update_one(
                        {"_id": investor["_id"]},
                        {"$push": {"previous_investments": investment_record}}
                    )
                    print(f"Added startup {startup_id} to investor {str(investor['_id'])} previous investments")

        return JSONResponse(
            content={"message": "Startup created successfully", "startupId": startup_id},
            status_code=201
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error in addStartup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def deleteStartup(startupId: str):
    try:
        startup_oid = ObjectId(startupId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid startup_id format")
    
    # Delete the startup document
    delete_result = await startups_collection.delete_one({"_id": startup_oid})
    if (delete_result.deleted_count == 0):
        raise HTTPException(status_code=404, detail="Startup not found")
    
    # Update all user documents where currentStartup equals this startup ObjectId
    await users_collection.update_many(
        {"currentStartup": startup_oid},
        {"$unset": {"currentStartup": ""}}
    )
    
    # Return a 204 No Content response
    return Response(status_code=status.HTTP_204_NO_CONTENT)

async def updateStartup(startupId: str, startup_data: dict, logo: UploadFile = None):
    try:
        # Validate the startup ID
        try:
            startup_oid = ObjectId(startupId)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid startup ID format")

        # Check if the startup exists
        existing_startup = await startups_collection.find_one({"_id": startup_oid})
        if not existing_startup:
            raise HTTPException(status_code=404, detail="Startup not found")

        # Debugging log: Inspect incoming data
        print(f"Updating startup with ID: {startupId}")
        print(f"Incoming data: {startup_data}")

        # Upload the logo to Cloudinary if provided
        if logo:
            print("Uploading logo to Cloudinary...")  # Debugging log
            startup_data["logo_url"] = await upload_image_from_buffer(logo)
            if not startup_data["logo_url"]:
                raise HTTPException(status_code=500, detail="Failed to upload logo to Cloudinary")

        # Convert founders to ObjectId if provided
        if "founders" in startup_data:
            try:
                startup_data["founders"] = [ObjectId(founder) for founder in startup_data["founders"]]
            except Exception as e:
                print(f"Error converting founders to ObjectId: {e}")
                raise HTTPException(status_code=400, detail="Invalid founders format")

        # Convert previous fundings' investor IDs to ObjectId if provided
        if "previous_fundings" in startup_data:
            for funding in startup_data["previous_fundings"]:
                if "investors" in funding and funding["investors"]:
                    for investor in funding["investors"]:
                        if "investorId" in investor and investor["investorId"]:
                            try:
                                investor["investorId"] = ObjectId(investor["investorId"])
                            except Exception as e:
                                print(f"Error converting investorId to ObjectId: {e}")
                                raise HTTPException(status_code=400, detail="Invalid investorId format")

        # Convert equity split user IDs to ObjectId if provided
        if "equity_split" in startup_data:
            for equity in startup_data["equity_split"]:
                if "userId" in equity:
                    if equity["userId"] is None:
                        # Remove invalid userId entries
                        equity.pop("userId")
                    else:
                        try:
                            equity["userId"] = ObjectId(equity["userId"])
                        except Exception as e:
                            print(f"Error converting userId to ObjectId: {e}")
                            raise HTTPException(status_code=400, detail="Invalid userId format")

        # Debugging log: Inspect processed data
        print(f"Processed data for update: {startup_data}")

        # Allow update if at least one field is present or logo is being updated
        if not startup_data:
            if logo:
                startup_data = {"logo_url": await upload_image_from_buffer(logo)}
            else:
                raise HTTPException(status_code=400, detail="No valid fields to update")

        update_result = await startups_collection.update_one(
            {"_id": startup_oid},
            {"$set": startup_data}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Startup update failed")

        # Get and return updated startup
        updated_startup = await startups_collection.find_one({"_id": startup_oid})

        # --- Populate founders with user objects (same as getAllStartups) ---
        if "founders" in updated_startup:
            for i, founder in enumerate(updated_startup["founders"]):
                founderId = ObjectId(founder)
                founderData = await users_collection.find_one({"_id": founderId})
                if founderData:
                    updated_startup["founders"][i] = convert_objectid_to_str(founderData)

        updated_startup = convert_objectid_to_str(updated_startup)
        return JSONResponse(
            content={
                "message": "Startup updated successfully",
            },
            status_code=200
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error in updateStartup: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating startup: {str(e)}")