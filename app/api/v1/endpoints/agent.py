from fastapi import APIRouter


router = APIRouter()


agent_executor = None



@router.post(
    "/chat"
)
async def chat(
    request: dict,
):


    result = await (
        agent_executor
        .run(
            request,
            {
                "configurable":
                {
                    "thread_id":
                    "001"
                }
            }
        )
    )


    return result