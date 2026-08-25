# Enterprise Knowledge Copilot

星云科技有限公司企业知识库问答后端。本文档以当前代码为准，区分已经接入的技术和架构图中尚未真正使用的技术。

## 实际运行架构

```text
文档上传
  ↓
TXT / Markdown / PDF / Word 解析
  ↓
Document 元数据
  ↓
RecursiveTextSplitter
  ↓
批量 Embedding（OpenAI 兼容接口，默认 text-embedding-3-small）
  ↓
PostgreSQL + pgvector（HNSW，1024 维）
  ↓
Vector Search + BM25
  ↓
RRF Hybrid Retrieval
  ↓
LLM Reranker
  ↓
Query Rewrite
  ↓
Token-aware Context Builder
  ↓
Conversation Summary + Message History
  ↓
DeepSeek LLM
  ↓
JSON 问答响应 + Citation Sources
```

文档上传后的索引任务由 Celery Worker 异步执行，Redis 用作 Broker、Result Backend 和文档分布式锁。数据库迁移由 Alembic 管理，Docker Compose 提供 PostgreSQL、Redis、API、Worker 和 migrate 服务。

前端联调台位于 `/ui/`，入口为：

```text
http://localhost:8000/ui/
```

## 当前已使用的技术栈

| 能力 | 当前实现 |
| --- | --- |
| Web API | FastAPI + Pydantic |
| 文档解析 | TXT、Markdown、PDF、DOCX Loader |
| 文本切块 | RecursiveTextSplitter |
| Embedding | OpenAI 兼容 Embedding API，默认 `text-embedding-3-small`，1024 维校验 |
| 向量数据库 | PostgreSQL + pgvector，不是 Milvus |
| 向量索引 | pgvector HNSW |
| 稀疏检索 | 自研 BM25 |
| 混合检索 | Dense + BM25 + RRF |
| 重排序 | LLMReranker |
| 查询改写 | QueryRewriter |
| 多轮上下文 | Conversation、Message、Summary Checkpoint |
| Context Engineering | TokenCounter、TokenBudget、History Selector、RAG Context Selector、TokenGuard、ContextDegrader |
| LLM | DeepSeek Chat API |
| 异步任务 | Celery |
| 消息和锁 | Redis |
| 持久化 | PostgreSQL + SQLAlchemy AsyncSession |
| 迁移 | Alembic |
| 引用来源 | `RagSource`，随 RAG 响应返回 `sources` |
| 可观测性 | Trace ID、Token、Latency、Cost、结构化日志、Prometheus `/metrics`、Grafana Dashboard |
| 认证 | 可选 JWT 登录、注册、当前用户、角色字段和租户字段 |
| 语义缓存 | Redis 查询结果缓存，带 TTL 和知识库索引失效 |
| 流式响应 | `/api/v1/rag/chat/stream` SSE（与 JSON 问答共用持久化逻辑） |
| 测试 | pytest + pytest-asyncio |
| 部署 | Docker、Docker Compose、Dockerfile |

## 架构图中提到但当前没有真正接入的技术

### Milvus

当前项目没有 Milvus 依赖、连接配置或 Repository。实际向量存储是 PostgreSQL + pgvector，代码和迁移都围绕 `document_chunks.embedding` 及 HNSW 索引实现。

因此架构图中的：

```text
Vector Store / Milvus
```

应改为：

```text
PostgreSQL / pgvector / HNSW
```

### Streaming / SSE

项目提供主 RAG 问答的 SSE 接口，并保留一个基础演示接口：

```text
POST /api/v1/stream-test
```

主问答 JSON 接口：

```text
POST /api/v1/rag/chat
```

流式主问答接口：

```text
POST /api/v1/rag/chat/stream
```

该接口返回 `start`、`delta`、`sources`、`done`/`error` 事件；前端可以按 SSE 增量渲染回答并在结束事件中展示引用。

因此当前架构应写成：

```text
DeepSeek LLM
  ↓
JSON Response + Citation
```

而不是把 Streaming / SSE 描述成主链路已完成能力。

### Nginx

仓库中存在 `nginx/nginx.conf`，但根目录 `docker-compose.yml` 当前没有启动 Nginx 服务。Nginx 配置属于预留反向代理配置，不应描述为当前默认部署拓扑的一部分。

### Authentication / RBAC

已补齐用户表迁移、PBKDF2 密码哈希、注册、登录、JWT 校验和 `/api/v1/auth/me`。通过 `AUTH_ENABLED=true` 开启 RAG 查询和问答接口的 Bearer Token 校验；默认关闭以保持本地联调兼容。

### Redis Semantic Cache

Redis 已实际用于 Celery、文档锁和无会话 RAG 查询缓存。缓存包含标准化问题、知识库和 `top_k`，带 TTL；重新索引知识库后会自动失效。会话问答不直接缓存，以避免跳过消息持久化。

### Prometheus / Grafana / OpenTelemetry

已接入 Prometheus exporter，访问 `/metrics` 可获取 HTTP 请求计数和延迟指标；Docker Compose 同时提供 Prometheus（9090）和 Grafana（3000），并自动加载基础 HTTP Dashboard。安装 `requirements-observability.txt` 并设置 `OTEL_EXPORTER_OTLP_ENDPOINT` 后，会自动启用 FastAPI OpenTelemetry tracing；Collector 配置模板位于 `monitoring/otel-collector-config.yaml`。

### Kafka、RabbitMQ、Elasticsearch、Qdrant、FAISS

当前项目没有使用 Kafka、RabbitMQ、Elasticsearch、Qdrant 或 FAISS。消息队列使用 Celery + Redis，向量检索默认使用 PostgreSQL + pgvector。

### Milvus

已提供可选 `MilvusVectorRepository`。执行 `pip install -r requirements-milvus.txt` 并设置 `VECTOR_STORE_BACKEND=milvus` 后，索引任务会把向量写入 Milvus，查询使用 Milvus 检索；PostgreSQL 仍保存文档和切片元数据。默认仍为 pgvector，避免改变现有环境。

## 修正后的项目介绍

> 我实现的是一个基于 FastAPI 的企业级 RAG Backend。系统支持 TXT、Markdown、PDF 和 Word 文档上传，通过 Celery 异步完成解析、切块和批量 Embedding，并将文档块及 1024 维向量持久化到 PostgreSQL + pgvector。查询阶段结合向量检索和 BM25，通过 RRF 融合、LLM Rerank 和 Query Rewrite 提升召回与排序质量，再结合会话历史、摘要检查点和 Token-aware Context Engineering 生成答案，并返回 Citation Sources、Trace、Token、Latency 和 Cost 信息。当前主问答接口返回 JSON，SSE 仅有演示接口；Milvus、完整认证、语义缓存和 Prometheus 监控尚未接入主链路。

## 启动与验证

B4 Docker、全链路测试和 CI/CD 学习手册：

[docs/B4_Docker_CI-CD_AI-Agent_实战学习手册.md](docs/B4_Docker_CI-CD_AI-Agent_实战学习手册.md)

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

打开：

```text
http://localhost:8000/ui/
```

验证：

```powershell
python -m compileall -q app tests
python -m pytest -q
node --check frontend/app.js
docker compose config -q
```
