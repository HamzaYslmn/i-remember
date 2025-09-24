import asyncio
import httpx
import time
import statistics

# Default headers for authentication
HEADERS = {
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJpZmllZCI6dHJ1ZSwiZXhwIjoxNzU4NzM0NTUwLCJkYXRhIjoiYzViZjIxY2MtNzkwMy00ZWE2LWFjOGMtZjE3YmU0MDNiZmY3In0.Mo37fbUClIcjqVgBEdRPpoQmU2C3v18DSuaz8ox82yk",
    "content-type": "application/json"
}

async def make_request(client, url, semaphore):
    async with semaphore:
        start = time.perf_counter()
        try:
            response = await client.get(url, headers=HEADERS, timeout=10)
            elapsed = time.perf_counter() - start
            return {"success": response.status_code == 200, "time": elapsed, "status": response.status_code}
        except Exception as e:
            elapsed = time.perf_counter() - start
            return {"success": False, "time": elapsed, "error": str(e)}

async def load_test(url="http://localhost:8001/api/i-remember", requests=1000, concurrent=100):
    print(f"Testing {url} with {requests} requests, {concurrent} concurrent")
    
    semaphore = asyncio.Semaphore(concurrent)
    results = []
    
    async with httpx.AsyncClient() as client:
        start_time = time.perf_counter()
        
        # Create all tasks
        tasks = [make_request(client, url, semaphore) for _ in range(requests)]
        
        # Execute with progress
        for i in range(0, len(tasks), concurrent):
            batch = tasks[i:i+concurrent]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)
            print(f"Progress: {len(results)}/{requests}")
        
        total_time = time.perf_counter() - start_time
    
    # Analyze results
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    response_times = [r["time"] for r in results]
    
    print(f"\n=== RESULTS ===")
    print(f"Total: {len(results)}")
    print(f"Success: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    print(f"RPS: {len(successful)/total_time:.2f}")
    print(f"Avg Response Time: {statistics.mean(response_times)*1000:.2f}ms")
    if response_times:
        print(f"Min: {min(response_times)*1000:.2f}ms")
        print(f"Max: {max(response_times)*1000:.2f}ms")

if __name__ == "__main__":
    url = input("URL [http://localhost:8001/api/i-remember]: ").strip() or "http://localhost:8001/api/i-remember"
    try:
        requests = int(input("Total requests [1000]: ").strip() or 1000)
    except ValueError:
        requests = 1000
    try:
        concurrent = int(input("Concurrent [100]: ").strip() or 100)
    except ValueError:
        concurrent = 100
    asyncio.run(load_test(url, requests, concurrent))