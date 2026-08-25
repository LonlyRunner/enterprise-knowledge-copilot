def handoff_router(
    state,
):


    if state.get(
        "handoff_to"
    ):


        return (
            state["handoff_to"]
        )


    return "end"