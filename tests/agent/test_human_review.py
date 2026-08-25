import pytest
import os
from langgraph.types import Command

from app.agent.langgraph.graph import (
    create_customer_graph,
)


@pytest.mark.asyncio
async def test_human_review_resume():

    os.environ[
        "REDIS_URL"
    ] = (
        "redis://localhost:6379/0"
    )


    graph = await create_customer_graph(
        FakeOrderAgent(),
        FakeRagAgent(),
    )


class FakeOrderAgent:


    async def run(
        self,
        *args,
        **kwargs,
    ):

        return {
            "answer":
            "订单查询完成"
        }



class FakeRagAgent:


    async def run(
        self,
        question,
    ):

        return "知识库结果"



@pytest.mark.asyncio
async def test_human_review_interrupt():


    graph = await create_customer_graph(

        FakeOrderAgent(),

        FakeRagAgent(),

    )

    os.environ[
        "REDIS_URL"
    ] = "redis://localhost:6379/0"


    config = {

        "configurable":
        {
            "thread_id":
            "refund-test-001"
        }

    }


    result = await graph.ainvoke(

        {

            "question":
            "我要退款，订单号是XN-001",

            "intent":
            "order",

            "answer":
            None,

            "tenant_id":
            "tenant001",

            "user_id":
            "user001",

            "trace_id":
            "trace001",

            "need_human_review":
            False,

            "human_action":
            None,

        },

        config=config,
    )


    assert (
        "__interrupt__"
        in result
    )


@pytest.mark.asyncio
async def test_human_review_resume():


    graph = await create_customer_graph(

        FakeOrderAgent(),

        FakeRagAgent(),

    )

    os.environ[
        "REDIS_URL"
    ] = "redis://localhost:6379/0"


    config = {

        "configurable":
        {
            "thread_id":
            "refund-test-002"
        }

    }


    # 第一次暂停

    await graph.ainvoke(

        {

            "question":
            "我要退款",

            "intent":
            "order",

            "answer":
            None,

            "tenant_id":
            "tenant001",

            "user_id":
            "user001",

            "trace_id":
            "trace001",

            "need_human_review":
            False,

            "human_action":
            None,

        },

        config=config,
    )


    # 人工审批继续

    result = await graph.ainvoke(

        Command(
            resume="approve"
        ),

        config=config,

    )


    assert (
        result["human_action"]
        ==
        "approve"
    )