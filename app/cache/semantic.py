from asyncio import sleep
from operator import call

import limiter


@limiter.limit(
"20/minute"
)
async def chat():
    ...

    for retry in range(3):

        try:

            response = await call()

            break


        except Exception:

            sleep(1)