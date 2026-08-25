# B4：Docker 化部署、全链路测试与 CI/CD

适用项目：Enterprise Knowledge Copilot / 星云科技有限公司企业知识库问答后端。

本手册继续使用当前仓库，不重新创建脱离项目的示例。默认工作目录：

~~~powershell
cd C:\wyy\project\AIproject\backend
~~~

## 当前项目关键文件

| 作用 | 文件 |
| --- | --- |
| API/Worker 镜像 | Dockerfile |
| 全栈编排 | docker-compose.yml |
| 基础依赖 | deploy/docker-compose.yml |
| 数据库迁移 | alembic/、alembic.ini |
| Celery | app/worker/celery_app.py |
| 文档索引任务 | app/tasks/document_tasks.py |
| 前端页面 | frontend/ |
| 监控 | monitoring/ |
| 当前 CI | .github/workflows/test.yml |

## B4 总目标

完成三章后，你需要能解释并实践：

1. API、Worker、数据库迁移为什么是不同容器。
2. Docker Compose 的服务名、健康检查、数据卷和网络。
3. 文档上传到 RAG 回答的完整链路验证。
4. Agent 的订单 Tool、物流 Tool、售后审批如何做业务冒烟测试。
5. CI 如何校验代码、Compose、镜像和前端。
6. CD 如何迁移、发布、健康检查和回滚。

---

# B4 第 1 章：Docker 化部署 AI Agent 全栈环境

## 1.1 宿主机基线

容器化不能掩盖应用本身的问题，先运行：

~~~powershell
.venv\Scripts\python.exe -m compileall -q app tests
.venv\Scripts\python.exe -m pytest -q
docker compose config -q
~~~

预期：测试通过，Compose 配置无输出。

## 1.2 Dockerfile 学习顺序

当前 Dockerfile 的职责是选择 Python 运行时、安装 requirements、复制代码并提供 API 默认启动命令。API 和 Worker 共用镜像，但 Compose 使用不同 command。

建议新增 .dockerignore：

~~~text
.git
.github
.venv
__pycache__
*.pyc
.pytest_cache
.mypy_cache
.ruff_cache
.env
storage/*
!storage/.gitkeep
~~~

原因：不复制虚拟环境、缓存、密钥和本地用户数据。

建议逐步加入：

~~~dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
~~~

再练习非 root 用户；修改后必须验证 storage/ 的写权限。

## 1.3 Compose 服务边界

| 服务 | 职责 | 依赖 |
| --- | --- | --- |
| postgres | PostgreSQL + pgvector | 无 |
| redis | Broker、Result、锁、缓存 | 无 |
| migrate | alembic upgrade head | postgres healthy |
| api | FastAPI 和静态前端 | postgres、redis、migrate |
| worker | Celery 文档索引 | postgres、redis、migrate |
| nginx | 可选反向代理 | api |
| prometheus/grafana | 监控 | api |

不要在每个 API 进程启动时自动迁移。多副本同时迁移会造成竞态；当前项目用 migrate 成功后再启动 API/Worker，体现发布阶段执行迁移的原则。

容器不能用 127.0.0.1 访问另一个容器，使用：

~~~text
postgres:5432
redis:6379
~~~

真实 .env 不提交；容器内连接地址和宿主机连接地址不是一回事。

## 1.4 第一次启动

~~~powershell
Copy-Item .env.example .env
# 编辑 .env，填写 DEEPSEEK_API_KEY、EMBEDDING_API_KEY
docker compose up -d --build postgres redis
docker compose run --rm migrate
docker compose up -d api worker
docker compose ps
docker compose logs --tail=100 api
docker compose logs --tail=100 worker
~~~

完整监控栈：

~~~powershell
docker compose up -d --build
~~~

访问：

~~~text
http://localhost:8000/api/v1/health
http://localhost:8000/ui/
http://localhost:8000/ui/orders.html
http://localhost:8000/ui/performance.html
~~~

## 1.5 本章练习、案例和面试题

1. 停止 Worker，上传文档，恢复 Worker 后确认任务继续执行。
2. 解释 depends_on、healthcheck 和 service_completed_successfully 的差异。
3. 说明 API 和 Worker 为什么可以共用镜像但使用不同 command。

企业案例：电商企业通常让订单 API 扩容多个副本，但数据库迁移只由一个发布 Job 执行；这正对应本项目的 api、worker、migrate 拆分。

面试题：Compose 的 depends_on 是否等于服务可用？为什么镜像不能包含 .env？如何保证迁移只执行一次？为什么容器内不能用 localhost 访问 Postgres？

---

# B4 第 2 章：Docker 环境下 AI Agent 全链路测试

## 2.1 测试目标

~~~text
前端上传 → FastAPI Document → Celery → Redis 锁
→ 解析/切块/Batch Embedding → pgvector
→ Hybrid Retrieval → LLM → Citation / SSE
~~~

订单链路：

~~~text
orders.html → /api/v1/orders → MockBusinessGateway
             ├→ query_order
             ├→ query_logistics
             └→ create_ticket（需要审批）
~~~

## 2.2 测试分层

| 层级 | 入口 | 检查内容 |
| --- | --- | --- |
| 静态 | compileall、node --check | 语法 |
| 单元 | pytest | Tool、RAG、业务网关 |
| API | HTTP/浏览器 | 状态码和响应结构 |
| Compose | docker compose | 网络、环境、服务 |
| 任务 | Worker 日志、数据库 | 异步索引真的完成 |
| 质量 | evaluation 数据集 | 召回和答案质量 |

## 2.3 文档索引全链路

~~~powershell
docker compose up -d --build
docker compose ps
docker compose logs -f worker
~~~

在 http://localhost:8000/ui/ 创建知识库，上传 data/company_policy.md 或 data/expense_reimbursement_policy.md。记录文档 ID，观察 Worker 日志。

数据库验证：

~~~powershell
docker compose exec postgres psql -U postgres -d enterprise_rag
~~~

~~~sql
SELECT id, file_name, status, chunk_count
FROM documents ORDER BY created_at DESC LIMIT 10;
SELECT COUNT(*) FROM document_chunks;
~~~

文档状态完成但切片数量为 0，不能算链路成功；继续排查 Worker、Embedding API、向量维度和事务提交。

## 2.4 RAG、SSE 和订单验证

在知识库页面提问“费用报销需要哪些审批？”，确认回答来自当前知识库并返回 Citation；/api/v1/rag/chat/stream 应产生 start、delta、sources、done 或 error。

性能页：

~~~text
http://localhost:8000/ui/performance.html
~~~

订单页：

~~~text
http://localhost:8000/ui/orders.html
~~~

订单验证顺序：

1. demo-user 查看 XN-2026-000381。
2. 确认“运输中”和运单号 SF2026082100381。
3. 查看物流时间线。
4. 填写售后原因，点击提交审批预览，确认 requires_approval=true。
5. 点击批准并创建，确认返回 ticket_id 和 pending_review。
6. 切换 finance-user，确认只显示企业私有化订单。

订单页面和 Agent Tools 共用 data/order_mock_data.json，不能出现两套数据。

## 2.5 故障定位

| 现象 | 检查 |
| --- | --- |
| 页面打不开 | docker compose ps、API 日志、端口 |
| 文档一直处理中 | Worker、Redis 健康状态 |
| 完成但无切片 | document_chunks、Embedding 日志 |
| RAG 无结果 | knowledge base ID、向量维度、切片数量 |
| LLM 超时 | LLM_TIMEOUT、网络、重试日志 |
| 订单为空 | tenant_id、user_id、mock JSON |
| 工单直接创建 | approved 分支和人工审批逻辑 |

企业案例：客服系统上线前用“查询订单 → 查询物流 → 发起售后 → 人工审批 → 工单落库”作为黄金链路。AI 只负责决策，结果必须落到可观测业务状态。

面试题：如何证明 Celery 任务已完成而不是只投递成功？文档完成但向量为 0 如何排查？查询 Tool 和工单 Tool 为什么权限不同？多租户订单如何防止越权？

---

# B4 第 3 章：CI/CD 自动化部署 AI Agent

## 3.1 目标流水线

~~~text
Pull Request → 静态检查 → pytest → Compose 校验
→ Docker 构建 → 镜像扫描 → 推送
→ migrate → 发布 API/Worker → 健康检查 → 回滚
~~~

## 3.2 当前 CI 的不足

当前 .github/workflows/test.yml 只有 checkout、pip install、pytest，还没有覆盖 Python 版本和缓存、compileall、前端检查、Compose 校验、镜像构建、安全扫描、推送、部署和回滚。因此它是测试流水线，不是完整 CI/CD。

建议保留 test.yml 作为基础示例，并新增：

~~~text
.github/workflows/ci.yml
.github/workflows/deploy.yml
~~~

## 3.3 推荐 CI 内容

~~~yaml
- name: Compile Python
  run: python -m compileall -q app tests

- name: Check frontend JavaScript
  run: |
    node --check frontend/app.js
    node --check frontend/orders.js
    node --check frontend/performance.js

- name: Install dependencies
  run: pip install -r requirements.txt

- name: Run tests
  run: python -m pytest -q

- name: Validate Compose
  run: docker compose config -q

- name: Build image
  run: docker build --tag enterprise-knowledge-copilot:GIT_SHA .
~~~

API 和 Worker 共用镜像，因为 Compose 通过不同 command 启动不同进程：

~~~text
API：uvicorn app.main:app --host 0.0.0.0 --port 8000
Worker：celery -A app.worker.celery_app:celery_app worker --loglevel=INFO -Q document_index
~~~

## 3.4 CD 发布顺序

1. 构建不可变镜像并使用 Git SHA 标记。
2. 推送镜像仓库。
3. 备份数据库或确认迁移可回滚。
4. 执行 alembic upgrade head。
5. 启动新版本 API 和 Worker。
6. 调用 /api/v1/health。
7. 执行只读订单查询和 RAG 冒烟测试。
8. 确认旧版本连接排空后再移除。

示例：

~~~powershell
docker compose pull
docker compose run --rm migrate
docker compose up -d api worker
docker compose ps
Invoke-RestMethod http://localhost:8000/api/v1/health
~~~

## 3.5 Secret 和回滚

GitHub Actions 使用 Secrets/Variables 管理 DEEPSEEK_API_KEY、EMBEDDING_API_KEY、DATABASE_URL、JWT_SECRET 和 Registry 凭据。禁止把 .env、API Key、数据库密码写入仓库、Dockerfile、前端 JavaScript 或 workflow 日志。CI 不应连接生产数据库或默认调用真实 LLM，单元测试使用 Fake Client。

应用版本回滚和数据库迁移回滚必须分开。不要把 alembic downgrade -1 当作通用回滚；优先采用向后兼容迁移：新增结构 → 发布兼容版本 → 回填 → 删除旧结构。

## 3.6 本章练习、案例和面试题

1. 新建 .github/workflows/ci.yml，完成 compileall → pytest → node --check → docker compose config → docker build。
2. 故意制造 Python、JavaScript、Compose、Dockerfile 和 pytest 错误，确认 CI 能阻止合并。
3. 发布后自动验证 health、orders、metrics、订单详情和 Token 诊断接口。
4. 解释 API 和 Worker 版本不一致会导致什么问题。

企业案例：金融和电商企业把 AI Agent 当普通微服务发布；模型可以变化，但订单查询、审批、审计、迁移和回滚必须遵循标准 CI/CD。

面试题：CI 和 CD 的边界是什么？为什么镜像用 Git SHA 而不是 latest？迁移失败为什么不能简单回滚应用镜像？如何在 CI 测试 Worker？为什么健康检查通过后仍要业务冒烟？

---

# B4 最终验收清单

## Docker 化

- [ ] docker compose config -q 通过。
- [ ] API、Worker、Postgres、Redis、migrate 职责清晰。
- [ ] 容器内使用服务名访问依赖。
- [ ] .env 未进入镜像和 Git。
- [ ] 数据库和 Redis 使用持久化卷。
- [ ] API 和 Worker 使用同一镜像、不同启动命令。

## 全链路测试

- [ ] health 正常。
- [ ] 前端页面正常加载。
- [ ] 文档上传后 Worker 接收到任务。
- [ ] 文档切片和向量数量大于 0。
- [ ] RAG 返回 Citation。
- [ ] SSE 返回 start、delta、done 或 error。
- [ ] 订单、物流和售后审批链路正常。
- [ ] 多租户/多用户隔离通过。

## CI/CD

- [ ] Python、前端静态检查通过。
- [ ] pytest 全部通过。
- [ ] Compose 校验通过。
- [ ] Docker 镜像构建通过。
- [ ] Secret 使用 CI Secret 管理。
- [ ] 镜像使用不可变版本标签。
- [ ] 部署后有健康检查和业务冒烟测试。
- [ ] 有明确的应用回滚策略。

## 推荐学习节奏

~~~text
第 1 天：读 Dockerfile 和 Compose，启动 Postgres/Redis
第 2 天：启动 API/Worker，完成文档索引全链路
第 3 天：用订单联调页验证 Tool Calling 和人工审批
第 4 天：补齐 CI 静态检查、pytest、Compose 校验
第 5 天：增加镜像构建、推送、部署和冒烟测试
~~~

完成一章后，先运行本章命令并记录实际输出，再进入下一章。不要只复制 YAML；面试和生产排障更看重你能否解释服务边界、失败模式和回滚策略。
