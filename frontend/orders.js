const $ = (id) => document.getElementById(id);
const api = () => ($('apiBase').value || '/api/v1').replace(/\/$/, '');
let selectedOrder = null;
let ticketCount = 0;
let approvalId = null;

const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const money = (value) => `¥${Number(value || 0).toLocaleString('zh-CN')}`;
const statusClass = (status) => status === 'shipping' || status === 'delivered' ? '' : 'muted';

async function request(path, options = {}) {
  const response = await fetch(`${api()}${path}`, {headers:{'Content-Type':'application/json'}, ...options});
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || body.message || `HTTP ${response.status}`);
  return body;
}

function renderOrders(items) {
  $('orderList').innerHTML = items.length ? items.map((order) => `<div class="order-row${selectedOrder?.order_id === order.order_id ? ' active' : ''}" data-order-id="${esc(order.order_id)}"><div class="order-main"><strong>${esc(order.order_id)}</strong><span>${esc(order.product)} · ${esc(order.created_at || '').slice(0,10)}</span><span>${esc(order.customer_name)} · ${esc(order.carrier || '—')}</span></div><div class="order-price"><span class="badge ${statusClass(order.status)}">${esc(order.status_label || order.status)}</span><div>${money(order.amount)}</div></div></div>`).join('') : '<div class="empty">没有符合条件的模拟订单</div>';
  document.querySelectorAll('.order-row').forEach((row) => row.addEventListener('click', () => selectOrder(row.dataset.orderId)));
}

async function loadOrders() {
  $('statusText').textContent = '加载中…';
  try {
    const params = new URLSearchParams();
    if ($('status').value) params.set('status', $('status').value);
    if ($('query').value.trim()) params.set('query', $('query').value.trim());
    const result = await request(`/orders?${params}`);
    renderOrders(result.items);
    $('totalCount').textContent = result.total;
    $('shippingCount').textContent = result.items.filter((item) => item.status === 'shipping').length;
    $('amountTotal').textContent = money(result.items.reduce((sum, item) => sum + Number(item.amount || 0), 0));
    $('ticketCount').textContent = ticketCount;
    $('statusText').textContent = `已加载 ${result.total} 条`;
    if (!selectedOrder && result.items[0]) await selectOrder(result.items[0].order_id);
  } catch (error) {
    $('orderList').innerHTML = `<div class="empty">加载失败：${esc(error.message)}</div>`;
    $('statusText').textContent = '请求失败';
  }
}

async function selectOrder(orderId) {
  try {
    const [order, logistics] = await Promise.all([
      request(`/orders/${encodeURIComponent(orderId)}`),
      request(`/orders/${encodeURIComponent(orderId)}/logistics`),
    ]);
    selectedOrder = order;
    $('detailTitle').textContent = order.order_id;
    $('detailStatus').textContent = order.status_label || order.status;
    $('detailStatus').className = `badge ${statusClass(order.status)}`;
    $('detailBody').innerHTML = `<div class="detail-grid"><div class="detail-item"><label>商品</label><strong>${esc(order.product)}</strong></div><div class="detail-item"><label>订单金额</label><strong>${money(order.amount)}</strong></div><div class="detail-item"><label>客户</label><strong>${esc(order.customer_name)} · ${esc(order.phone_masked)}</strong></div><div class="detail-item"><label>下单时间</label><strong>${esc(order.created_at)}</strong></div><div class="detail-item"><label>收货地址</label><strong>${esc(order.delivery_address_masked)}</strong></div><div class="detail-item"><label>预计送达</label><strong>${esc(order.eta || '不适用')}</strong></div></div>`;
    const events = logistics.events || [];
    $('logistics').innerHTML = `<h3>物流轨迹 · ${esc(logistics.carrier || '—')} / ${esc(logistics.tracking_no || '—')}</h3>${events.length ? `<div class="timeline">${events.map((event) => `<div class="event"><time>${esc(event.time)}</time><p>${esc(event.description)}</p><small>${esc(event.location)}</small></div>`).join('')}</div>` : '<div class="empty">暂无物流节点，可能是待付款或线上交付订单。</div>'}`;
    $('ticketPanel').hidden = false;
    $('ticketReason').value = '';
    $('ticketOutput').textContent = '';
    approvalId = null;
    document.querySelectorAll('.order-row').forEach((row) => row.classList.toggle('active', row.dataset.orderId === orderId));
  } catch (error) {
    $('detailBody').innerHTML = `<div class="empty">订单详情加载失败：${esc(error.message)}</div>`;
  }
}

async function submitTicket(approved) {
  if (!selectedOrder) return;
  const reason = $('ticketReason').value.trim();
  if (reason.length < 2) { $('ticketOutput').textContent = '请先填写至少 2 个字的售后原因。'; return; }
  try {
    const result = await request(`/orders/${encodeURIComponent(selectedOrder.order_id)}/tickets`, {method:'POST', body:JSON.stringify({reason, approved, approval_id: approvalId})});
    if (result.approval_id) approvalId = result.approval_id;
    $('ticketOutput').textContent = JSON.stringify(result, null, 2);
    if (result.success) { ticketCount += 1; $('ticketCount').textContent = ticketCount; }
  } catch (error) { $('ticketOutput').textContent = `失败：${error.message}`; }
}

$('refreshBtn').addEventListener('click', loadOrders);
$('status').addEventListener('change', loadOrders);
$('userId').addEventListener('change', () => { selectedOrder = null; loadOrders(); });
$('query').addEventListener('keydown', (event) => { if (event.key === 'Enter') loadOrders(); });
$('ticketPreviewBtn').addEventListener('click', () => submitTicket(false));
$('ticketApproveBtn').addEventListener('click', () => submitTicket(true));
loadOrders();
