# ./middleware/middleware.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, Response
import time
from middleware.logger_module import logger as log

def add_middlewares(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def enforce_request_policies(request: Request, call_next):
        start_time = time.perf_counter()

        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            request.state.auth = "public"
        else:   
            request.state.auth = auth_header
        
        response = await call_next(request)
        response.headers["X-Process-Time"] = f"{time.perf_counter() - start_time:0.4f}"
        return response