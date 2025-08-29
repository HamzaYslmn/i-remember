import socket

hostname = socket.gethostname()
ipv4_address = socket.gethostbyname(hostname)
print(f"IPv4 Address: {ipv4_address}")

# ./xMain.py
from dotenv import load_dotenv
load_dotenv("../ENV/.env")

from fastapi import FastAPI
import pkgutil
import importlib

# middleware
import middleware.middleware as custom_middleware

# Create the FastAPI app
app = FastAPI(
    title="API Service",
    description="API service from HamzaY",
    root_path="/api",
    version="0.0.1",
    redoc_url="/redocs",  # None
    docs_url="/docs"  # None
)

custom_middleware.add_middlewares(app)

#* Tüm routes klasörünü otomatik tara ve router'ları ekle
def include_all_routers(app, package):
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "router"):
                app.include_router(module.router)
            if is_pkg and hasattr(module, "__path__"):
                include_all_routers(app, module)
        except Exception as e:
            print(f"Router import error for {module_name}: {e}")

include_all_routers(app, importlib.import_module("routes"))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)