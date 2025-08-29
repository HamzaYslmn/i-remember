from dotenv import load_dotenv
load_dotenv("../../../ENV/.env")

import os
import jwt
import datetime

JWT_SECRET = os.getenv("JWT_SECRET")  # Set your JWT secret key

async def verify_jwt_token(request_token):
    try:
        # Remove the disablement of expiration verification.
        decoded = jwt.decode(request_token, JWT_SECRET, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Token Problem")
    
async def generate_jwt_token(data, exp):
    # Generate a new JWT token with a 7-day expiration.
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=exp)
    token_payload = {
        "verified": True,
        "exp": int(expiration.timestamp()),  # Use an integer timestamp for expiration.
        "data": data
    }
    session_token = jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")
    return session_token

if __name__ == "__main__":
    import asyncio
    async def main():
        generated_token = await generate_jwt_token("test")
        print(generated_token)

        decoded_payload = await verify_jwt_token(generated_token)
        print(decoded_payload)

    asyncio.run(main())