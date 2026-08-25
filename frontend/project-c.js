const $ = (id) => document.getElementById(id);
const api = () => ($("apiBase").value || "/api/v1").replace(/\/$/, "");
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

async function request(path, options = {}) {
  const response = await fetch(api() + path, {headers: {"Content-Type": "application/json"}, ...options});
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error((body.detail && body.detail.message) || body.detail || body.message || ("HTTP " + response.status));
  return body;
}

async function loadKnowledgeBases() {
  try {
    const result = await request("/knowledge-bases");
    const select = $("knowledgeBase");
    (result.items || []).forEach((item) => {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.name + " · " + item.id.slice(0, 8);
      select.appendChild(option);
    });
  } catch (error) {
    $("status").textContent = "知识库加载失败：" + error.message;
  }
}

function body() {
  const payload = {
    question: $("question").value.trim(),
    mode: $("mode").value,
    approve_actions: $("approve").checked,
    top_k: 5,
  };
  if ($("knowledgeBase").value) payload.knowledge_base_id = $("knowledgeBase").value;
  return payload;
}

function renderResult(result) {
  $("resultStatus").textContent = result.status === "pending_approval" ? "等待人工审批" : "执行完成";
  $("routeBadge").textContent = (result.route || "") + " · " + (result.model || "");
  $("routeBadge").className = "badge " + (result.status === "completed" ? "" : "muted");
  $("answer").textContent = result.answer || "无回答";
  $("steps").className = "steps";
  $("steps").innerHTML = (result.agent_steps || []).map((step) => "<div class=\"step\"><strong>" + esc(step.agent) + " · " + esc(step.action) + " · " + esc(step.status) + "</strong>" + esc(step.summary) + "</div>").join("") || "<div class=\"empty\">暂无步骤</div>";
  $("tools").className = "steps";
  $("tools").innerHTML = (result.tool_calls || []).map((call) => "<div class=\"step\"><strong>" + esc(call.server) + " / " + esc(call.tool) + "</strong>" + (call.success ? "成功" : "失败") + "<br>" + esc(JSON.stringify(call.result)) + "</div>").join("") || "<div class=\"empty\">暂无 MCP Tool 调用</div>";
  $("raw").textContent = JSON.stringify(result, null, 2);
  if (result.approvals && result.approvals.length) {
    $("approvalBox").hidden = false;
    $("approvalBox").innerHTML = "<h3>需要人工审批</h3>" + result.approvals.map((item) => "<div>" + esc(item.approval_id) + "：" + esc(item.reason) + "<br>重新提交时勾选“批准写操作”。</div>").join("");
  } else {
    $("approvalBox").hidden = true;
  }
  $("status").textContent = "完成 · " + ((result.usage && result.usage.total_tokens) || 0) + " tokens";
}

async function sendJson() {
  $("status").textContent = "执行中…";
  try {
    const payload = body();
    if (!payload.question) throw new Error("请输入任务");
    const endpoint = payload.mode === "agent" ? "/ai/agent" : "/ai/chat";
    renderResult(await request(endpoint, {method: "POST", body: JSON.stringify(payload)}));
  } catch (error) {
    $("status").textContent = "失败：" + error.message;
    $("answer").textContent = error.message;
  }
}

async function sendStream() {
  $("status").textContent = "SSE 连接中…";
  $("answer").textContent = "";
  $("steps").innerHTML = "";
  $("tools").innerHTML = "";
  try {
    const response = await fetch(api() + "/ai/stream", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body())});
    if (!response.ok) throw new Error("HTTP " + response.status);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const part = await reader.read();
      if (part.done) break;
      buffer += decoder.decode(part.value, {stream: true});
      const events = buffer.split("\n\n");
      buffer = events.pop();
      for (const raw of events) {
        const dataLine = raw.split("\n").find((line) => line.startsWith("data:"));
        if (!dataLine) continue;
        try {
          const data = JSON.parse(dataLine.slice(5));
          if (data.content) $("answer").textContent += data.content;
          if (data.agent) $("steps").insertAdjacentHTML("beforeend", "<div class=\"step\"><strong>" + esc(data.agent) + " · " + esc(data.action) + "</strong>" + esc(data.summary) + "</div>");
          if (data.request_id) renderResult(data);
          if (data.message) $("status").textContent = "失败：" + data.message;
        } catch (_) {}
      }
    }
    $("status").textContent = "SSE 完成";
  } catch (error) {
    $("status").textContent = "SSE 失败：" + error.message;
  }
}

$("sendBtn").addEventListener("click", sendJson);
$("streamBtn").addEventListener("click", sendStream);
$("healthBtn").addEventListener("click", async () => {
  try {
    await request("/health");
    $("status").textContent = "AI Gateway 可用";
  } catch (error) {
    $("status").textContent = "Gateway 不可用：" + error.message;
  }
});
document.querySelectorAll("[data-question]").forEach((button) => button.addEventListener("click", () => { $("question").value = button.dataset.question; }));
loadKnowledgeBases();
