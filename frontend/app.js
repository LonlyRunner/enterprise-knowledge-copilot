const state = {
  knowledgeBases: [],
  documents: [],
  conversations: [],
  activeKnowledgeBaseId: null,
  activeConversationId: null,
  lastDebug: null,
};

const $ = (id) => document.getElementById(id);

function apiBase() {
  return ($("apiBase").value || "/api/v1").replace(/\/$/, "");
}

function setNotice(message, isError = false) {
  const notice = $("notice");
  notice.hidden = !message;
  notice.textContent = message || "";
  notice.classList.toggle("error", isError);
}

function renderDebug(payload) {
  state.lastDebug = payload;
  $("debugOutput").textContent = JSON.stringify(payload, null, 2);
}

async function request(path, options = {}) {
  const response = await fetch(`${apiBase()}${path}`, options);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof payload === "object" ? (payload.message || payload.detail || JSON.stringify(payload)) : payload;
    throw new Error(`${response.status}: ${message || "请求失败"}`);
  }
  renderDebug({ path, status: response.status, response: payload });
  return payload;
}

function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

function renderKnowledgeBases() {
  const list = $("knowledgeBaseList");
  if (!state.knowledgeBases.length) {
    list.className = "list empty-list";
    list.textContent = "还没有知识库，请先新建。";
  } else {
    list.className = "list";
    list.innerHTML = state.knowledgeBases.map((item) => `
      <button class="list-item ${item.id === state.activeKnowledgeBaseId ? "active" : ""}" data-kb-id="${item.id}">
        <strong>${escapeHtml(item.name)}</strong><span>${formatDate(item.created_at)} · ${item.id.slice(0, 8)}</span>
      </button>`).join("");
    list.querySelectorAll("[data-kb-id]").forEach((button) => button.addEventListener("click", () => selectKnowledgeBase(button.dataset.kbId)));
  }
  $("kbCount").textContent = state.knowledgeBases.length;
}

async function loadKnowledgeBases() {
  try {
    state.knowledgeBases = (await request("/knowledge-bases")).items || [];
    renderKnowledgeBases();
    if (state.activeKnowledgeBaseId && state.knowledgeBases.some((item) => item.id === state.activeKnowledgeBaseId)) {
      await selectKnowledgeBase(state.activeKnowledgeBaseId, false);
    } else if (state.knowledgeBases[0]) {
      await selectKnowledgeBase(state.knowledgeBases[0].id, false);
    } else {
      resetWorkspace();
    }
  } catch (error) {
    setNotice(`加载知识库失败：${error.message}`, true);
    renderKnowledgeBases();
  }
}

async function selectKnowledgeBase(id, showNotice = true) {
  state.activeKnowledgeBaseId = id;
  state.activeConversationId = null;
  renderKnowledgeBases();
  const active = state.knowledgeBases.find((item) => item.id === id);
  $("activeContext").textContent = active ? `${active.name} · 正在加载文档和会话` : "正在加载…";
  try {
    const [documents, conversations] = await Promise.all([
      request(`/knowledge-bases/${id}/documents`),
      request(`/knowledge-bases/${id}/conversations`),
    ]);
    state.documents = documents.items || [];
    state.conversations = conversations.items || [];
    renderDocuments();
    renderConversations();
    if (state.conversations[0]) state.activeConversationId = state.conversations[0].id;
    updateChatState();
    if (showNotice) setNotice(`已切换到：${active?.name || id}`);
  } catch (error) {
    setNotice(`加载知识库数据失败：${error.message}`, true);
  }
}

function renderDocuments() {
  const list = $("documentList");
  $("docCount").textContent = state.documents.length;
  if (!state.documents.length) {
    list.className = "list empty-list";
    list.textContent = "暂无文档，请上传制度文件。";
    return;
  }
  list.className = "list";
  list.innerHTML = state.documents.map((item) => `
    <div class="list-item"><strong>${escapeHtml(item.name)}</strong><span>${item.status} · ${formatDate(item.created_at)}</span></div>`).join("");
}

function renderConversations() {
  const select = $("conversationSelect");
  select.innerHTML = state.conversations.length
    ? state.conversations.map((item) => `<option value="${item.id}">${escapeHtml(item.title || "未命名会话")} · ${formatDate(item.created_at)}</option>`).join("")
    : "<option value=\"\">暂无会话，请新建</option>";
  select.disabled = !state.conversations.length;
  if (state.activeConversationId) select.value = state.activeConversationId;
  $("conversationCount").textContent = state.conversations.length;
}

function updateChatState() {
  const enabled = Boolean(state.activeKnowledgeBaseId && state.activeConversationId);
  $("newConversationButton").disabled = !state.activeKnowledgeBaseId;
  $("questionInput").disabled = !enabled;
  $("sendButton").disabled = !enabled;
  const active = state.knowledgeBases.find((item) => item.id === state.activeKnowledgeBaseId);
  $("activeContext").textContent = enabled ? `${active?.name || "当前知识库"} · 会话已就绪` : "请选择知识库并创建会话";
}

async function createConversation() {
  if (!state.activeKnowledgeBaseId) return;
  try {
    const result = await request(`/knowledge-bases/${state.activeKnowledgeBaseId}/conversations`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: "联调会话" }),
    });
    state.conversations.unshift(result);
    state.activeConversationId = result.id;
    renderConversations();
    updateChatState();
    setNotice("会话已创建，可以开始提问。", false);
  } catch (error) {
    setNotice(`创建会话失败：${error.message}`, true);
  }
}

function appendMessage(role, content, sources = []) {
  const list = $("messageList");
  const welcome = list.querySelector(".welcome-message");
  if (welcome) welcome.remove();
  const item = document.createElement("div");
  item.className = `message ${role}`;
  const sourceText = sources.length ? `<div class="sources">引用 ${sources.length} 个片段：${sources.map((source) => escapeHtml(source.source || "未命名文档")).join("、")}</div>` : "";
  item.innerHTML = `<div class="avatar">${role === "user" ? "我" : "星"}</div><div><div class="bubble">${escapeHtml(content)}${sourceText}</div></div>`;
  list.appendChild(item);
  list.scrollTop = list.scrollHeight;
}

function createStreamingAssistant() {
  const list = $("messageList");
  const welcome = list.querySelector(".welcome-message");
  if (welcome) welcome.remove();
  const item = document.createElement("div");
  item.className = "message assistant";
  item.innerHTML = '<div class="avatar">星</div><div><div class="bubble streaming-answer"></div></div>';
  list.appendChild(item);
  return item.querySelector(".streaming-answer");
}

async function consumeSse(response, onEvent) {
  if (!response.ok || !response.body) throw new Error(`${response.status}: 无法建立流式连接`);
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() || "";
    for (const frame of frames) {
      const event = frame.match(/^event:\s*(.+)$/m)?.[1] || "message";
      const dataLine = frame.match(/^data:\s*(.+)$/m)?.[1] || "{}";
      try { onEvent(event, JSON.parse(dataLine)); } catch { /* ignore malformed keep-alive frames */ }
    }
    if (done) break;
  }
}

async function sendQuestion(question) {
  if (!question.trim() || !state.activeKnowledgeBaseId || !state.activeConversationId) return;
  appendMessage("user", question.trim());
  $("questionInput").value = "";
  $("sendButton").disabled = true;
  try {
    const response = await fetch(`${apiBase()}/rag/chat/stream`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ knowledge_base_id: state.activeKnowledgeBaseId, conversation_id: state.activeConversationId, question: question.trim(), top_k: 3 }),
    });
    const answerNode = createStreamingAssistant();
    let answer = "";
    let sources = [];
    await consumeSse(response, (event, data) => {
      if (event === "delta") {
        answer += data.content || "";
        answerNode.textContent = answer;
        $("messageList").scrollTop = $("messageList").scrollHeight;
      } else if (event === "sources") {
        sources = data.sources || [];
        const sourceNode = document.createElement("div");
        sourceNode.className = "sources";
        sourceNode.textContent = sources.length ? `引用 ${sources.length} 个片段：${sources.map((source) => source.source || "未命名文档").join("、")}` : "";
        answerNode.appendChild(sourceNode);
      } else if (event === "error") {
        throw new Error(data.message || "流式问答失败");
      }
      renderDebug({ path: "/rag/chat/stream", event, data });
    });
    if (!answer) answerNode.textContent = "根据当前知识库无法确定。";
    setNotice("回答完成。可在下方 DEBUG 区查看原始响应。", false);
  } catch (error) {
    appendMessage("assistant", `请求失败：${error.message}`);
    setNotice(`问答失败：${error.message}`, true);
  } finally {
    updateChatState();
  }
}

async function healthCheck() {
  const pill = $("healthStatus");
  pill.textContent = "检查中";
  pill.className = "status-pill status-idle";
  try {
    const result = await request("/health");
    pill.textContent = result.status === "ok" ? "服务正常" : "服务异常";
    pill.className = `status-pill ${result.status === "ok" ? "status-ok" : "status-error"}`;
    setNotice(`后端连接成功：${result.service || "API"} ${result.version || ""}`);
  } catch (error) {
    pill.textContent = "连接失败";
    pill.className = "status-pill status-error";
    setNotice(`后端连接失败：${error.message}`, true);
  }
}

function resetWorkspace() {
  state.documents = [];
  state.conversations = [];
  state.activeKnowledgeBaseId = null;
  state.activeConversationId = null;
  renderDocuments();
  renderConversations();
  updateChatState();
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

$("healthButton").addEventListener("click", healthCheck);
$("refreshKbButton").addEventListener("click", loadKnowledgeBases);
$("newConversationButton").addEventListener("click", createConversation);
$("conversationSelect").addEventListener("change", (event) => { state.activeConversationId = event.target.value || null; updateChatState(); });
$("clearChatButton").addEventListener("click", () => { $("messageList").innerHTML = "<div class=\"welcome-message\"><div class=\"welcome-icon\">✦</div><h3>消息已清空</h3><p>继续向星云知识助手提问吧。</p></div>"; });
$("copyDebugButton").addEventListener("click", async () => { if (state.lastDebug) await navigator.clipboard.writeText(JSON.stringify(state.lastDebug, null, 2)); setNotice("DEBUG JSON 已复制。", false); });
$("createKbForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = $("kbName").value.trim();
  if (!name) return;
  try {
    const result = await request("/knowledge-bases", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, description: "星云科技有限公司联调知识库" }) });
    $("kbName").value = "星云科技有限公司知识库";
    await loadKnowledgeBases();
    await selectKnowledgeBase(result.id);
    setNotice(`知识库“${result.name}”创建成功。`);
  } catch (error) { setNotice(`创建知识库失败：${error.message}`, true); }
});
$("uploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = $("documentFile").files[0];
  if (!state.activeKnowledgeBaseId || !file) return;
  const formData = new FormData();
  formData.append("file", file);
  try {
    const result = await request(`/knowledge-bases/${state.activeKnowledgeBaseId}/documents`, { method: "POST", body: formData });
    $("documentFile").value = "";
    await selectKnowledgeBase(state.activeKnowledgeBaseId, false);
    setNotice(`文档已提交索引：${result.document?.name || file.name}，任务 ID：${result.task_id || "-"}`);
  } catch (error) { setNotice(`上传失败：${error.message}`, true); }
});
$("chatForm").addEventListener("submit", (event) => { event.preventDefault(); sendQuestion($("questionInput").value); });
$("questionInput").addEventListener("keydown", (event) => { if ((event.ctrlKey || event.metaKey) && event.key === "Enter") { event.preventDefault(); sendQuestion(event.target.value); } });
document.querySelectorAll(".suggestion").forEach((button) => button.addEventListener("click", () => { $("questionInput").value = button.textContent; $("questionInput").focus(); }));

healthCheck();
loadKnowledgeBases();
