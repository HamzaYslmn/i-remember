from xSupabase import read_sdoc
import time
import asyncio

async def main():
    doc_id = "x"
    
    # Heating up the connection
    try:
        warmup_task = read_sdoc(table="i-remember", doc_id=[doc_id])
        await warmup_task
        print("Warmup completed")
    except Exception as e:
        print(f"Warmup failed: {e}")
        return
    
    # Main test
    tasks = [
        read_sdoc(table="i-remember", doc_id=[doc_id])
        for _ in range(100)
    ]
    
    start_time = time.perf_counter()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.perf_counter() - start_time
    
    num_success = sum(1 for result in results if not isinstance(result, Exception) and result is not None)
    success_rate = (num_success / 50) * 100
    total_requests = len(tasks)

    print("Total requests: {}".format(total_requests))
    print("Total duration: {:.2f} seconds".format(total_time))
    print("Average duration per call: {:.4f} seconds".format(total_time / total_requests))
    print("Success rate: {:.2f}%".format(success_rate))
    print("done")

if __name__ == '__main__':
    asyncio.run(main())