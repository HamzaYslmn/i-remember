from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from pydantic import Field, BaseModel, ConfigDict, field_validator, model_validator
from typing import List, Optional, Dict
import datetime
import json
import asyncio
from collections import OrderedDict

import modules.Supabase.xSupabase as xSupaBase
import modules.JWT.xJWT as xJWT

router = APIRouter(
    prefix="/i-remember", 
    tags=["i-remember Routes"]
)

# -----------------------------------------  LRU CACHE (async)  -----------------------------------------
class AsyncLRUCache:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = OrderedDict()  # key: (value, expiry)
        self._lock = asyncio.Lock()

    async def get(self, key: str):
        async with self._lock:
            item = self.cache.get(key)
            if not item:
                return None
            value, expiry = item
            if expiry and datetime.datetime.now(datetime.timezone.utc) >= expiry:
                self.cache.pop(key, None)
                return None
            self.cache.move_to_end(key)
            return value

    async def put(self, key: str, value: any, expiry: str = None):
        async with self._lock:
            if expiry:
                if isinstance(expiry, str):
                    expiry = datetime.datetime.fromisoformat(expiry.replace('Z', '+00:00'))
            else:
                expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            self.cache[key] = (value, expiry)

    async def delete(self, key: str):
        async with self._lock:
            self.cache.pop(key, None)

    async def clear(self):
        async with self._lock:
            self.cache.clear()

# Initialize cache instance
document_cache = AsyncLRUCache(max_size=100)

# -----------------------------------------  MODELS  -----------------------------------------

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
        raise HTTPException(status_code=401, detail=str(e))

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
        # Optimized: Only select count to check limit, don't fetch full data
        read_data = await xSupaBase.read_sdoc(
            "i-remember", 
            select="uuid",  # Only select minimal field for counting
            filters={"client_ip": new_data["client_ip"]},
            limit=3  # We only need to know if there are 2 or more
        )
        if read_data.get('count', 0) >= 2:
            raise HTTPException(status_code=400, detail="You can only create two documents.")
    except Exception as e:
        if "Response data is empty" not in str(e) and "You can only create two document" not in str(e):
            raise HTTPException(status_code=500, detail=str(e))
        elif "You can only create two document" in str(e):
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
    
    # Try to get from cache first
    cached_data = await document_cache.get(doc_uuid)
    if cached_data is not None:
        return JSONResponse(status_code=200, content={"detail": cached_data})
    
    try:
        # Only select needed fields to reduce data transfer and processing
        read_data = (await xSupaBase.read_sdoc(
            "i-remember", 
            doc_id=[doc_uuid],
            select="data,valid,created_at"  # Exclude uuid and client_ip from query
        ))['data'][0]
        
        # Cache the retrieved data with its validity period
        validity_time = read_data.get('valid', 1)
        if validity_time:
            await document_cache.put(doc_uuid, read_data, validity_time)
        
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
        
        # Remove from cache after successful update
        await document_cache.delete(doc_uuid)
        
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
        
        # Remove from cache after successful deletion
        await document_cache.delete(doc_uuid)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"detail": "Document deleted successfully"})