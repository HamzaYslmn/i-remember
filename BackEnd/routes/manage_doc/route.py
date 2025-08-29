from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from pydantic import Field, BaseModel, ConfigDict, field_validator, model_validator
from typing import List, Optional, Dict
import datetime
import json

import modules.Supabase.xSupabase as xSupaBase
import modules.JWT.xJWT as xJWT

router = APIRouter(
    prefix="/i-remember", 
    tags=["i-remember Routes"]
)

# Pydantic models for request and response validation
class AdResponse(BaseModel):
    detail: str

# Helper Functions
async def validate_access(jwt: str):
    if jwt == "public" or jwt is None:
        raise HTTPException(status_code=400, detail="Invalid Auth")
    try:
        decoded_jwt = await xJWT.verify_jwt_token(jwt)
        return decoded_jwt
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid Auth")

# --------------------------------------------------    POST    --------------------------------------------------
    
class POSTRequest(BaseModel):
    data: Dict = Field(..., description="Data to be stored")
    valid: int = Field(1, description="Expiration date in minutes 1 minute to 7 days", ge=1, le=10080)
    
    model_config = ConfigDict(extra="forbid")

@router.post("")
async def add(request: Request, request_data: POSTRequest):
    new_data = {
        "data": request_data.data,
        "valid": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=request_data.valid)).isoformat(),
        "client_ip": request.client.host if request.client else "Unknown"
    }
    
    try:
        # Check if the client IP already exists
        read_data = await xSupaBase.read_sdoc("i-remember", select="client_ip", filters={"client_ip": new_data["client_ip"]})
        if read_data and read_data.get('data'):
            raise HTTPException(status_code=400, detail="You can only create one document.")
    except Exception as e:
        if "Response data is empty" not in str(e) and "You can only create one document" not in str(e):
            raise HTTPException(status_code=500, detail=str(e))
        elif "You can only create one document" in str(e):
            raise e
    
    try:
        uuid = await xSupaBase.create_sdoc("i-remember", data=new_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        key = await xJWT.generate_jwt_token(uuid, request_data.valid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=201, content={"detail": key})

# --------------------------------------------------    GET    --------------------------------------------------

@router.get("")
async def get(request: Request):
    decoded_jwt = await validate_access(request.state.auth)
    doc_uuid = decoded_jwt["data"]
    try:
        read_data = (await xSupaBase.read_sdoc("i-remember", doc_id=[doc_uuid]))['data'][0]
        print(read_data)

        # Remove unwanted fields from response
        if read_data:
            read_data.pop('uuid', None)
            read_data.pop('client_ip', None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(status_code=200, content={"detail": read_data})

# --------------------------------------------------    PUT    --------------------------------------------------

class UPDATERequest(BaseModel):
    data: Dict = Field(..., description="Data to update")
    valid: Optional[int] = Field(None, description="Expiration date in minutes 1 minute to 7 days", ge=1, le=10080)

    model_config = ConfigDict(extra="ignore")
    
@router.put("")
async def update(request: Request, request_data: UPDATERequest):
    decoded_jwt = await validate_access(request.state.auth)
    doc_uuid = decoded_jwt["data"]
    
    # Prepare update data
    update_data = request_data.model_dump(exclude_unset=True)
    
    # Convert valid minutes to datetime if provided
    if 'valid' in update_data and update_data['valid'] is not None:
        update_data['valid'] = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=update_data['valid'])).isoformat()
    
    try:
        await xSupaBase.update_sdoc("i-remember", doc_id=doc_uuid, data=update_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"detail": "Document updated successfully"})

# --------------------------------------------------    DELETE    --------------------------------------------------
class DELETERequest(BaseModel):    
    model_config = ConfigDict(extra="ignore")
    
@router.delete("")
async def delete(request: Request, request_data: DELETERequest):
    decoded_jwt = await validate_access(request.state.auth)
    doc_uuid = decoded_jwt["data"]
    try:
        await xSupaBase.delete_sdoc("i-remember", doc_id=doc_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"detail": "Document deleted successfully"})