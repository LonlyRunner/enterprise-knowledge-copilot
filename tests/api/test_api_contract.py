from app.main import app


def test_openapi_has_unique_operation_ids_and_ai_routes():
    document = app.openapi()
    operations = [
        operation.get("operationId")
        for path in document["paths"].values()
        for operation in path.values()
        if isinstance(operation, dict) and operation.get("operationId")
    ]
    assert len(operations) == len(set(operations))
    assert {"/api/v1/ai/chat", "/api/v1/ai/agent", "/api/v1/ai/stream"} <= set(document["paths"])
