from app.utils.trace import (
    create_trace_id,
    get_trace_id,
)



def test_trace_id():

    trace_id = (
        create_trace_id()
    )


    assert trace_id is not None


    assert (
        get_trace_id()
        ==
        trace_id
    )