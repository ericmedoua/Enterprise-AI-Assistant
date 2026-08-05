import asyncio


async def run_parallel(*tasks):
    """
    Execute multiple awaitables concurrently.
    """
    return await asyncio.gather(*tasks)
