# ./modules/Supabase/xSupabase.py
import os
from dotenv import load_dotenv
from supabase import AsyncClient, create_async_client

load_dotenv("../../../ENV/.env")

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase credentials missing: check .env file path and content.")

DB_SCHEMA = "public"

_clients = {}

async def get_client(storage: bool = False) -> AsyncClient:
    key = "storage" if storage else "db"
    if key not in _clients:
        client = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
        _clients[key] = client.storage.from_("conversation.prefix") if storage else client.schema(DB_SCHEMA)
    return _clients[key]
    
async def create_sdoc(table: str, data: dict, uuid: str = None) -> str:
    client = await get_client()
    if uuid:
        data["uuid"] = uuid
    
    try:
        response = await client.table(table).insert(data, returning="representation").execute()
        return response.data[0]["uuid"]
    except Exception as e:
        if "duplicate key value violates unique constraint" in str(e):
            raise ValueError("Document already exists.")
        raise RuntimeError(f"Error creating sdoc: {e}")

async def read_sdoc(
    table: str,
    limit: int = 1,
    page: int = 0,
    select: str = "*",
    doc_id: list = None,
    filters: dict = None,
    descending: bool = True,
    descending_field: list = None,
) -> dict:
    try:
        client = await get_client()
        query = client.table(table).select(select or "*", count="exact")

        if filters:
            for field_key, value in filters.items():
                if "." in field_key:
                    column, key = field_key.split(".", 1)
                    if isinstance(value, list):
                        conditions = [f"{column}->>{key}.ilike.%{v}%" for v in value]
                        query = query.or_(",".join(conditions))
                    else:
                        query = query.ilike(f"{column}->>{key}", f"%{value}%")
                else:
                    query = query.in_(field_key, value) if isinstance(value, list) else query.eq(field_key, value)

        if doc_id:
            query = query.in_("uuid", doc_id)
            
        for field in (descending_field or ["created_at"]):
            query = query.order(field, desc=descending)

        offset = page * limit
        query = query.range(offset, offset + limit - 1)
        
        response = await query.execute()
        if not response.data:
            raise ValueError("Response data is empty")
        return {"data": response.data, "count": response.count}
    except Exception as e:
        raise RuntimeError(f"Error reading sdoc: {e}")

async def update_sdoc(table: str, doc_id: str, data: dict) -> dict:
    try:
        client = await get_client()
        
        response = await client.table(table)\
            .update(data)\
            .eq("uuid", doc_id)\
            .execute()

        return response.data[0]["uuid"]

    except Exception as e:
        raise RuntimeError(f"Error updating sdoc: {e}")

async def delete_sdoc(table: str, doc_id: str, owner: str = None) -> bool:
    try:
        client = await get_client()
        query = client.table(table).delete().eq("uuid", doc_id)
        
        if owner:
            query = query.eq("owner", owner)
        
        response = await query.execute()
        return bool(response.data)
    except Exception as e:
        raise RuntimeError(f"Error deleting sdoc: {e}")

if __name__ == "__main__":
    import asyncio
    import datetime
    
    async def main():
        # columns: uuid(uuid), created_at(timestampz), data(jsonb), valid(timestampz), api-key(text)
            # CREATE - Insert a new document
            print("=== CREATE EXAMPLE ===")
            new_data = {
                "data": {
                    "title": "Test Memory",
                    "content": "This is a test memory entry",
                    "tags": ["test", "example"]
                },
                "valid": (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat(),
            }
            doc_uuid = await create_sdoc("i-remember", new_data)
            print(f"Created document with UUID: {doc_uuid}")
            
            # READ - Get all documents
            print("\n=== READ ALL EXAMPLE ===")
            all_docs = await read_sdoc("i-remember", limit=10)
            print(f"Found {all_docs['count']} total documents")
            print(f"Retrieved {len(all_docs['data'])} documents")
            for doc in all_docs['data']:
                print(f"- UUID: {doc['uuid']}, Title: {doc['data'].get('title', 'No title')}")
            
            # READ - Get specific document by UUID
            print("\n=== READ BY UUID EXAMPLE ===")
            specific_doc = await read_sdoc("i-remember", doc_id=[doc_uuid])
            print(f"Retrieved specific document:")
            print(f"- UUID: {specific_doc['data'][0]['uuid']}")
            print(f"- Data: {specific_doc['data'][0]['data']}")
            
            # READ - Filter by data content
            print("\n=== READ WITH FILTER EXAMPLE ===")
            filtered_docs = await read_sdoc(
                "i-remember", 
                filters={"data.title": "Test Memory"},
                limit=5
            )
            print(f"Filtered documents found: {len(filtered_docs['data'])}")
            
            import time
            time.sleep(30)
            
            # DELETE - Remove the created document
            print("\n=== DELETE EXAMPLE ===")
            deleted = await delete_sdoc("i-remember", doc_uuid)
            print(f"Document deleted: {deleted}")
            
            # Verify deletion
            print("\n=== VERIFY DELETION ===")
            verification_result = await read_sdoc("i-remember", doc_id=[doc_uuid])
            if not verification_result['data']:
                print("Confirmed deletion: Document no longer exists")
            else:
                print("Warning: Document still exists after deletion")

    asyncio.run(main())