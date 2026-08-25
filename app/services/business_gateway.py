from typing import Protocol


class BusinessGateway(Protocol):
    """
    企业业务系统抽象接口

    Agent Tool 不直接依赖数据库/API
    """

    async def query_order(
        self,
        order_id: str,
        *,
        tenant_id: str,
        user_id: str,
    ) -> dict:
        ...


class MockBusinessGateway:
    """
    本地开发测试实现

    后续替换:
    Java API Gateway
    """

    def __init__(self):

        self.orders = {
            "XN-2026-000381": {
                "order_id": "XN-2026-000381",
                "status": "shipping",
                "product": "AI服务器",
                "amount": 8999,
            },

            "XN-2026-000382": {
                "order_id": "XN-2026-000382",
                "status": "completed",
                "product": "企业软件授权",
                "amount": 19999,
            },
        }


    async def query_order(
        self,
        order_id: str,
        *,
        tenant_id: str,
        user_id: str,
    ) -> dict:

        order = self.orders.get(
            order_id
        )

        if order is None:
            return {
                "success": False,
                "error_code": "ORDER_NOT_FOUND",
            }


        return {
            "success": True,
            "data": order,
        }