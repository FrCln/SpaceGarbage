import asyncio


async def sleep(delay):
    for i in range(delay):
        await asyncio.sleep(0)
