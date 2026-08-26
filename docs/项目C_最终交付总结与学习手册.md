# 项目 C：Enterprise AI Gateway / Multi-Agent 交付手册

本文件以当前仓库代码为准，说明项目 C 已经落地的能力、文件边界和学习顺序。新增代码复用项目 A 的 RAG 服务、项目 B 的订单 Mock Business Gateway，不改变原有 `/rag`、`/orders`、`/agent` 接口。

## 1. 已落地的最终链路

```text
Web / API
   ↓
FastAPI /api/v1/ai
   ↓
AI Gateway（限流、模型选择、审计、指标、异常合同）
   ↓
SupervisorAgent（拆解任务）
   ├─ Chat Agent       → 回答汇总
   ├─ RAG Agent        → 项目 A RagService / Citation
   └─ Action Agent     → EnterpriseMCPService
                              ├─ Tool：订单、物流、工单
                              ├─ Resource：客户、订单历史、企业制度
                              └─ Prompt：客服 Agent 统一模板
   ↓
AgentResult（步骤、工具调用、引用、工件、审批、Token）
   ↓
JSON 或 SSE
```

写操作默认返回 `pending_approval`，只有请求 `approve_actions=true` 才创建工单。这样既能演示业务闭环，也不会让模型自由循环产生不可逆副作用。

## 2. 关键文件地图

| 目录/文件 | 职责 |
| --- | --- |
| `app/contracts/agent_result.py` | Gateway、Agent、MCP 共用结果合同 |
| `app/gateway/schemas.py` | 统一请求/响应；兼容旧 `message` 字段 |
| `app/gateway/service.py` | AI Gateway 主服务、模型路由、限流、审计、Prometheus |
| `app/gateway/limiter.py` | Redis 限流；Redis 不可用时本地联调 fail-open |
| `app/gateway/audit.py` | 结构化审计日志及 Redis 最近事件 |
| `app/api/v1/endpoints/ai.py` | `/ai/chat`、`/ai/agent`、`/ai/stream` |
| `app/agent/project_c/supervisor.py` | 规则化任务拆解与路由 |
| `app/agent/project_c/rag_agent.py` | 调用既有 RAG 服务并映射引用 |
| `app/agent/project_c/action_agent.py` | 订单分析、订单/物流查询、审批工单 |
| `app/agent/project_c/chat_agent.py` | LLM 汇总；无 Key 时使用可测试的确定性回答 |
| `app/agent/project_c/orchestrator.py` | Supervisor → 专业 Agent → Chat 汇总 |
| `app/mcp/enterprise.py` | MCP Tool/Resource/Prompt 的进程内企业边界 |
| `app/mcp/enterprise_server.py` | 可单独部署的 Streamable HTTP MCP Server（8001） |
| `frontend/project-c.*` | 项目 C Gateway、SSE、审批、原始 JSON 联调页 |
| `tests/agent/test_project_c.py` | 多 Agent、MCP 工具、审批回归测试 |

命名约定：业务 Agent 使用 `ProjectC*Agent`，跨层结果使用 `Agent*`，企业工具统一从 `EnterpriseMCPService` 进入；不要在 Agent 内直接 import `MockBusinessGateway`。

## 3. API 联调

```powershell
# 本地启动
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# JSON Agent 请求
Invoke-RestMethod http://127.0.0.1:8000/api/v1/ai/agent `
  -Method Post -ContentType 'application/json' `
  -Body '{"question":"查询订单 XN-2026-000381 的物流","mode":"agent"}'
```

接口：

- `POST /api/v1/ai/chat`：统一入口，支持 `auto/chat/rag/agent`。
- `POST /api/v1/ai/agent`：强制 Agent 编排。
- `POST /api/v1/ai/stream`：`start → step → delta → result → done` SSE。
- `GET /ui/project-c.html`：星云科技项目 C 前端联调页。
- `python -m app.mcp.enterprise_server`：启动 `http://localhost:8001/mcp`。

本地无 LLM Key 时，默认 `GATEWAY_DEFAULT_MODEL=project-c-router`，可验证完整路由、MCP、审批和 SSE；配置 `model=deepseek-chat` 或修改环境变量后再接入真实模型。

## 4. 分章节学习顺序

### 第 1 章：读懂统一合同

先阅读 `app/contracts/agent_result.py` 和 `app/gateway/schemas.py`。理解为什么工具调用、引用、审批和 Token 必须是结构化字段，而不是拼接在回答字符串里。

### 第 2 章：手写 Supervisor

阅读 `supervisor.py`，为一个新意图增加关键词和 `PlannedTask`。要求先写单测，再修改路由；不要让 Agent 自由递归调用自己。

### 第 3 章：接入 RAG Agent

阅读 `rag_agent.py`，沿用项目 A 的 `RagService.query` 和租户过滤，验证 `knowledge_base_id` 缺失时返回 422/400，而不是静默查询全部知识库。

### 第 4 章：Action Agent 与人工审批

阅读 `action_agent.py` 和 `EnterpriseMCPService.call_tool`。查询是无副作用 Tool，创建工单是有副作用 Tool；先生成 `ApprovalRequest`，批准后才执行。

### 第 5 章：MCP 三大对象

分别调用 `list_capabilities()`、`read_resource()`、`get_prompt()`，再启动 `enterprise_server.py` 验证 HTTP MCP。后续替换 Java 业务系统时，只替换 MCP Server 内部实现，Agent 合同不变。

### 第 6 章：Gateway 生产化

学习 Redis 限流、审计事件、Prometheus 指标、模型白名单和 SSE 错误事件。真实企业中还应继续补充 JWT 强制开启、幂等键、分布式审批存储和外部 MCP 客户端连接池。

## 5. 验收命令与真实案例

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

当前回归覆盖项目 C 与原有项目 A/B，共 63 项测试。建议在面试或演示中使用：

1. “查询订单 XN-2026-000381 的物流”——Supervisor 路由 Action，MCP 调用两个只读 Tool。
2. “总结今年销售情况，如果发现异常订单帮我创建工单”——生成销售报告工件，异常工单先挂起人工审批。
3. 勾选“批准写操作”重新提交——调用 `create_ticket`，结果中出现 `approved` 审批和工单 Tool 调用。
4. “查询合同付款条件，然后创建审批流程”——RAG Agent 提供引用；当前审批写操作应继续接入一个真实 MCP Tool 后再放行。

## 6. 后续生产增强清单

- 将审批记录持久化到数据库并绑定 `approval_id`，禁止仅依赖前端布尔值。
- 为外部 MCP Client 增加连接池、超时、重试和断路器，并在 `MCP_EXTERNAL_ENABLED=true` 时切换。
- Supervisor 从关键词升级为可评估的意图分类器，保留规则兜底和人工审计。
- 将报告工件存储到对象存储，返回下载地址与权限校验。
- 为每次请求增加幂等键、用户级 Token 配额和敏感数据脱敏策略。

本次生产化加固已提前落地：知识库增加租户归属、文档/会话/订单接口接入 RBAC、写操作审批持久化到 `ai_approvals`、Docker Compose 覆盖容器内服务地址、MCP Server 支持静态 Service Token。升级数据库后再启动 API：

```powershell
python -m alembic upgrade head
```

AI Gateway 的 SSE 已支持通过 `ChatAgent.stream()` 发送真实增量；当未配置模型时仍以确定性分片保持联调可用。RAG 查询、Hybrid Vector/BM25 检索和 Citation 现在携带租户及稳定 `chunk_id`，便于权限审计和 C5 评测。

## 8. 生产注意事项

不要在生产环境使用仓库根目录 `.env` 的本机地址；Compose 已为 API、Worker 和迁移任务覆盖为 `postgres`/`redis` 服务名。生产应设置 `AUTH_ENABLED=true`、非默认 `JWT_SECRET` 和 `MCP_AUTH_TOKEN`，并通过网关限制 MCP 的网络来源。

## 7. C5 Evaluation 评测闭环

C5 评测代码位于 `app/evaluation/`，统一 Runner 会对同一批 Golden Cases 计算 Agent、Retrieval、Generation 三组指标，并输出逐案例结果、缓存命中数和质量门禁结论。

```powershell
# 离线回放（适合开发和 CI）
python -m app.evaluation.cli run `
  --dataset data/evaluation/c5_cases.json `
  --results data/evaluation/c5_results.json `
  --gate data/evaluation/quality_gate.json

# 对运行中的 Gateway 做真实 HTTP 评测
python -m app.evaluation.cli run `
  --dataset data/evaluation/c5_cases.json `
  --base-url http://127.0.0.1:8000/api/v1 `
  --no-cache
```

缓存位于 `storage/evaluation/cache/`，按案例输入、Runner 版本和执行器版本生成 SHA-256 Key；修改数据或执行器版本会自动失效。需要强制重跑时使用 `--no-cache --clear-cache`。

`data/evaluation/quality_gate.json` 是 CI 的唯一门禁配置。任一已启用指标低于阈值，CLI 返回退出码 2，GitHub Actions 会阻止流水线通过并上传 Markdown 报告 artifact。覆盖的指标包括：路由、Tool Selection、Tool Arguments、Hit Rate、Recall@K、MRR、Keyword、Citation、Groundedness、Relevance。
