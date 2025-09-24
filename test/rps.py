import asyncio
import httpx
import time

URL = "https://i-remember.onrender.com/api/i-remember"
HEADERS = {
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJpZmllZCI6dHJ1ZSwiZXhwIjoxNzU4NzM0NTUwLCJkYXRhIjoiYzViZjIxY2MtNzkwMy00ZWE2LWFjOGMtZjE3YmU0MDNiZmY3In0.Mo37fbUClIcjqVgBEdRPpoQmU2C3v18DSuaz8ox82yk",
    "content-type": "application/json",
    "referer": "https://i-remember.onrender.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

async def fetch(client):
    try:
        resp = await client.get(URL, headers=HEADERS, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False

async def measure_rps(request_count=1000):
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        tasks = [fetch(client) for _ in range(request_count)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start
        success = sum(results)
        fail = request_count - success
        rps = success / elapsed if elapsed > 0 else 0
        print(f"Toplam istek: {request_count}")
        print(f"Geçen süre: {elapsed:.2f} sn")
        print(f"Başarılı istek: {success}")
        print(f"Başarısız istek: {fail}")
        print(f"Request per second (RPS): {rps:.2f}")

if __name__ == "__main__":
    asyncio.run(measure_rps(1000))