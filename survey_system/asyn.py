import asyncio
import time
import random



async def barista(order_number, lock, start) :
    print(f"[{time.time()-start:.2f}s]Customer {order_number} placed an order ")
    await asyncio.sleep(0.2)
    async with lock:
        print(f"[{time.time()-start:.2f}s]Barista is making coffee for customer {order_number}")
        await asyncio.sleep(random.uniform(0.5, 2.0))
        print(f"[{time.time()-start:.2f}s]Customer {order_number} got their drink")   


async def main():
    lock = asyncio.Lock()
    start = time.time()
    await asyncio.gather(barista(1, lock, start),
                        barista(2, lock, start),
                        barista(3, lock, start))

asyncio.run(main())