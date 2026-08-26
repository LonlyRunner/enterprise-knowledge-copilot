import pytest

from app.agent.project_c.action_agent import ProjectCActionAgent
from app.agent.project_c.chat_agent import ProjectCChatAgent
from app.agent.project_c.orchestrator import ProjectCOrchestrator
from app.agent.project_c.rag_agent import ProjectCRagAgent
from app.agent.project_c.supervisor import SupervisorAgent
from app.gateway.schemas import GatewayRequest
from app.mcp.enterprise import EnterpriseMCPService


@pytest.mark.asyncio
async def test_project_c_sales_requires_approval_for_anomaly_tickets():
    request = GatewayRequest(
        question="总结销售情况，如果发现异常订单帮我创建工单",
        mode="agent",
    )
    orchestrator = ProjectCOrchestrator(
        supervisor=SupervisorAgent(),
        action_agent=ProjectCActionAgent(EnterpriseMCPService()),
        rag_agent=ProjectCRagAgent(),
        chat_agent=ProjectCChatAgent(),
    )
    result = await orchestrator.run(
        request,
        session=None,
        request_id="req-1",
        task_id="task-1",
        trace_id="trace-1",
        tenant_id="default",
        user_id="demo-user",
    )
    assert result.status == "pending_approval"
    assert result.approvals
    assert result.tool_calls
    assert any(call.tool == "list_orders" for call in result.tool_calls)


@pytest.mark.asyncio
async def test_project_c_order_approval_then_ticket():
    request = GatewayRequest(
        question="查询订单 XN-2026-000381 并创建售后工单",
        mode="agent",
        approve_actions=True,
    )
    orchestrator = ProjectCOrchestrator(
        action_agent=ProjectCActionAgent(EnterpriseMCPService()),
        rag_agent=ProjectCRagAgent(),
        chat_agent=ProjectCChatAgent(),
    )
    result = await orchestrator.run(
        request,
        session=None,
        request_id="req-2",
        task_id="task-2",
        trace_id="trace-2",
        tenant_id="default",
        user_id="demo-user",
    )
    assert result.status == "completed"
    assert any(call.tool == "create_ticket" and call.success for call in result.tool_calls)
    assert result.approvals[0].status == "approved"


@pytest.mark.asyncio
async def test_project_c_orchestrator_streams_answer_deltas():
    request = GatewayRequest(question="查询订单 XN-2026-000381 的物流", mode="agent")
    deltas = []
    async def collect(delta):
        deltas.append(delta)
    result = await ProjectCOrchestrator(chat_agent=ProjectCChatAgent()).run(
        request,
        session=None,
        request_id="req-stream",
        task_id="task-stream",
        trace_id="trace-stream",
        tenant_id="default",
        user_id="demo-user",
        delta_callback=collect,
    )
    assert "".join(deltas) == result.answer
    assert deltas
