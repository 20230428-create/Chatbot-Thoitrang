// Chat State
let chatSessionId = localStorage.getItem('fashion_chat_session') || ('user_' + Math.random().toString(36).substring(2, 9));
localStorage.setItem('fashion_chat_session', chatSessionId);

let isWaitingResponse = false;
let currentRecommendedProducts = [];
let wardrobeTab = 'recommended';

document.addEventListener('DOMContentLoaded', () => {
  setupChatInputEvents();
  updateRecommendedCount();
});

function setupChatInputEvents() {
  const input = document.getElementById('chat-textarea');
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });

    // Auto-expand textarea
    input.addEventListener('input', () => {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    });
  }
}

function startNewChat() {
  chatSessionId = 'user_' + Math.random().toString(36).substring(2, 9);
  localStorage.setItem('fashion_chat_session', chatSessionId);
  currentRecommendedProducts = [];
  updateRecommendedCount();

  const container = document.getElementById('chat-messages');
  if (container) {
    container.innerHTML = `
      <div class="chat-welcome-hero" id="chat-welcome-hero">
        <div class="welcome-avatar-wrap">👔</div>
        <h2 class="welcome-headline">Hôm nay bạn muốn mặc phong cách gì?</h2>
        <p class="welcome-sub">
          Tôi là AI Stylist riêng của bạn. Tôi có thể tư vấn trang phục theo dịp, phân tích size chuẩn theo số đo chiều cao/cân nặng và gợi ý set đồ phối màu hoàn hảo.
        </p>
        <div class="welcome-cards-grid">
          <div class="welcome-card-prompt" onclick="openChatWithPrompt('Tôi cần áo nam màu đen dưới 500k để đi dự tiệc')">
            <div class="card-icon">👔</div>
            <div class="card-title">Áo nam đen đi dự tiệc</div>
            <div class="card-desc">Tìm áo sơ mi hoặc polo đen sang trọng dưới 500k</div>
          </div>
          <div class="welcome-card-prompt" onclick="openChatWithPrompt('Tôi cao 1m70, nặng 65kg nên mặc size gì?')">
            <div class="card-icon">📏</div>
            <div class="card-title">Tư vấn size theo vóc dáng</div>
            <div class="card-desc">Phân tích thể trạng, chỉ số BMI và tư vấn form dáng vừa vặn</div>
          </div>
          <div class="welcome-card-prompt" onclick="openChatWithPrompt('Có váy nữ nào dưới 500 nghìn không?')">
            <div class="card-icon">👗</div>
            <div class="card-title">Váy đầm nữ thanh lịch</div>
            <div class="card-desc">Đề xuất đầm dạ hội, váy xòe vintage hoặc chân váy công sở</div>
          </div>
          <div class="welcome-card-prompt" onclick="openChatWithPrompt('Màu đen có hợp với quần jean xanh không?')">
            <div class="card-icon">🎨</div>
            <div class="card-title">Tư vấn phối màu sắc</div>
            <div class="card-desc">Quy tắc phối màu tương phản, bánh xe màu sắc và phong cách phối đồ</div>
          </div>
        </div>
      </div>
    `;
  }

  // Update wardrobe content
  const wardrobe = document.getElementById('wardrobe-content');
  if (wardrobe) {
    wardrobe.innerHTML = `
      <div style="text-align: center; color: #94a3b8; padding: 40px 10px; font-size: 13px;">
        Trò chuyện cùng AI Stylist để các món đồ đề xuất tự động xuất hiện tại đây!
      </div>
    `;
  }
  showToast("Đã khởi tạo cuộc trò chuyện mới!");
}

function openChatWithPrompt(promptText) {
  const input = document.getElementById('chat-textarea');
  if (input) {
    input.value = promptText;
    input.style.height = 'auto';
    handleSendMessage();
  }
}

async function handleSendMessage() {
  const input = document.getElementById('chat-textarea');
  if (!input) return;
  const text = input.value.trim();
  if (!text || isWaitingResponse) return;

  input.value = '';
  input.style.height = '42px';

  // Hide welcome hero if first message
  const hero = document.getElementById('chat-welcome-hero');
  if (hero) hero.remove();

  appendUserMessage(text);
  showTypingIndicator();
  isWaitingResponse = true;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: chatSessionId,
        message: text
      })
    });

    removeTypingIndicator();
    isWaitingResponse = false;

    if (!res.ok) {
      const errText = await res.text();
      console.error("API Error:", res.status, errText);
      appendAssistantMessage(`⚠️ Máy chủ phản hồi mã lỗi (${res.status}). Vui lòng thử lại!`);
      return;
    }

    const data = await res.json();

    if (data.reply) {
      appendAssistantMessage(data.reply, data.recommended_products);
      
      // Update quick chips if provided
      if (data.quick_replies && data.quick_replies.length > 0) {
        updateQuickChips(data.quick_replies);
      }

      // Update right wardrobe panel with newly recommended products
      if (data.recommended_products && data.recommended_products.length > 0) {
        updateWardrobeProducts(data.recommended_products);
      }
    }
  } catch (err) {
    removeTypingIndicator();
    isWaitingResponse = false;
    console.error("Chat error:", err);
    appendAssistantMessage(`⚠️ Lỗi xử lý (${err.message || 'kết nối'}). Vui lòng gửi lại câu hỏi!`);
  }
}

function appendUserMessage(text) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const row = document.createElement('div');
  row.className = 'chat-message-row user';
  row.innerHTML = `<div class="msg-bubble">${escapeHtml(text)}</div>`;
  container.appendChild(row);
  scrollToBottom();
}

function appendAssistantMessage(markdownText, products = []) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const formattedHtml = formatMarkdown(markdownText);
  let productsHtml = '';

  if (products && products.length > 0) {
    productsHtml = `
      <div class="chat-product-cards">
        ${products.map(p => `
          <div class="chat-prod-card" onclick="viewProductDetail(${p.id})">
            <img src="${p.image}" class="chat-prod-thumb" alt="${p.name}">
            <div class="chat-prod-meta">
              <div class="chat-prod-title">${p.name}</div>
              <div class="chat-prod-price">${Number(p.price).toLocaleString()}đ</div>
              <div class="chat-prod-tag">${p.color} • ${p.style ? p.style.split(',')[0] : 'Thời trang'}</div>
            </div>
            <div class="chat-prod-actions-row">
              <button class="chat-prod-action" onclick="event.stopPropagation(); viewProductDetail(${p.id})">Chi tiết</button>
              <button class="chat-prod-action" style="background: var(--accent); color: #111;" onclick="event.stopPropagation(); addToCart(${p.id}, '${p.name}', ${p.price}, '${p.image}')">+ Giỏ</button>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  const row = document.createElement('div');
  row.className = 'chat-message-row assistant';
  row.innerHTML = `
    <div class="msg-avatar">✨</div>
    <div class="msg-bubble">
      <div>${formattedHtml}</div>
      ${productsHtml}
    </div>
  `;
  container.appendChild(row);
  scrollToBottom();
}

function showTypingIndicator() {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const row = document.createElement('div');
  row.id = 'chat-typing-row';
  row.className = 'chat-message-row assistant';
  row.innerHTML = `
    <div class="msg-avatar">✨</div>
    <div class="msg-bubble typing-bubble">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  container.appendChild(row);
  scrollToBottom();
}

function removeTypingIndicator() {
  const row = document.getElementById('chat-typing-row');
  if (row) row.remove();
}

function updateQuickChips(replies) {
  const bar = document.getElementById('quick-prompts-bar');
  if (!bar) return;

  bar.innerHTML = replies.map(q => `
    <button class="quick-chip" onclick="openChatWithPrompt('${q.replace(/'/g, "\\'")}')">
      ${q}
    </button>
  `).join('');
}

function scrollToBottom() {
  const container = document.getElementById('chat-messages');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function formatMarkdown(text) {
  if (!text) return '';
  let str = text;
  str = str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  str = str.replace(/^[*-]\s+(.*)$/gm, '<li style="margin-left: 18px;">$1</li>');
  str = str.replace(/^(\d+)\.\s+(.*)$/gm, '<li style="margin-left: 18px; list-style-type: decimal;">$2</li>');
  str = str.split('\n\n').map(p => {
    p = p.trim();
    if (!p) return '';
    if (p.startsWith('<li')) return `<ul style="margin-bottom: 8px;">${p}</ul>`;
    return `<p style="margin-bottom: 8px;">${p.replace(/\n/g, '<br>')}</p>`;
  }).join('');
  return str;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

// Right Wardrobe Panel Functions
function updateWardrobeProducts(products) {
  currentRecommendedProducts = products;
  updateRecommendedCount();
  if (wardrobeTab === 'recommended') {
    renderWardrobeRecommended();
  }
}

function updateRecommendedCount() {
  const counter = document.getElementById('recommended-count');
  if (counter) {
    counter.innerText = currentRecommendedProducts.length;
  }
}

function toggleWardrobePanel(tab = 'recommended') {
  const panel = document.getElementById('wardrobe-panel');
  if (!panel) return;

  if (panel.classList.contains('collapsed')) {
    panel.classList.remove('collapsed');
    switchWardrobeTab(tab);
  } else {
    if (tab && tab !== wardrobeTab) {
      switchWardrobeTab(tab);
    } else {
      panel.classList.add('collapsed');
    }
  }
}

function switchWardrobeTab(tab) {
  wardrobeTab = tab;
  const btnRec = document.getElementById('tab-btn-recommended');
  const btnCat = document.getElementById('tab-btn-catalog');
  if (btnRec && btnCat) {
    btnRec.classList.toggle('active', tab === 'recommended');
    btnCat.classList.toggle('active', tab === 'catalog');
  }

  if (tab === 'recommended') {
    renderWardrobeRecommended();
  } else {
    renderWardrobeCatalog();
  }
}

function renderWardrobeRecommended() {
  const container = document.getElementById('wardrobe-content');
  if (!container) return;

  if (currentRecommendedProducts.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; color: #94a3b8; padding: 40px 10px; font-size: 13px;">
        Chưa có gợi ý nào. Hãy nhắn tin để AI Stylist tìm trang phục phù hợp cho bạn!
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Stylist vừa đề xuất ${currentRecommendedProducts.length} món đồ:</div>
    ${currentRecommendedProducts.map(p => `
      <div class="chat-prod-card" onclick="viewProductDetail(${p.id})">
        <img src="${p.image}" class="chat-prod-thumb" alt="${p.name}">
        <div class="chat-prod-meta">
          <div class="chat-prod-title">${p.name}</div>
          <div class="chat-prod-price">${Number(p.price).toLocaleString()}đ</div>
          <div class="chat-prod-tag">${p.color} • ${p.category_name || ''}</div>
        </div>
        <div class="chat-prod-actions-row">
          <button class="chat-prod-action" onclick="event.stopPropagation(); viewProductDetail(${p.id})">Xem</button>
          <button class="chat-prod-action" style="background: var(--accent); color: #111;" onclick="event.stopPropagation(); addToCart(${p.id}, '${p.name}', ${p.price}, '${p.image}')">+ Giỏ</button>
        </div>
      </div>
    `).join('')}
  `;
}

async function renderWardrobeCatalog() {
  const container = document.getElementById('wardrobe-content');
  if (!container) return;

  container.innerHTML = `<div style="text-align: center; color: #94a3b8; padding: 20px;">Đang tải bộ sưu tập...</div>`;

  try {
    const res = await fetch(`/api/products?limit=100&t=${Date.now()}`);
    const data = await res.json();
    const prods = data.products || [];

    container.innerHTML = `
      <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Toàn bộ ${prods.length} sản phẩm cửa hàng:</div>
      ${prods.map(p => `
        <div class="chat-prod-card" onclick="viewProductDetail(${p.id})">
          <img src="${p.image}" class="chat-prod-thumb" alt="${p.name}">
          <div class="chat-prod-meta">
            <div class="chat-prod-title">${p.name}</div>
            <div class="chat-prod-price">${Number(p.price).toLocaleString()}đ</div>
            <div class="chat-prod-tag">${p.gender} • ${p.color}</div>
          </div>
          <div class="chat-prod-actions-row">
            <button class="chat-prod-action" onclick="event.stopPropagation(); viewProductDetail(${p.id})">Xem</button>
            <button class="chat-prod-action" style="background: var(--accent); color: #111;" onclick="event.stopPropagation(); addToCart(${p.id}, '${p.name}', ${p.price}, '${p.image}')">+ Giỏ</button>
          </div>
        </div>
      `).join('')}
    `;
  } catch (err) {
    container.innerHTML = `<div style="color: red; padding: 20px;">Lỗi tải dữ liệu</div>`;
  }
}

// Modal Handlers
function openSizeAdvisorModal() {
  const m = document.getElementById('modal-size-advisor');
  if (m) m.classList.add('active');
}

function openOutfitAdvisorModal() {
  const m = document.getElementById('modal-outfit-advisor');
  if (m) m.classList.add('active');
}

function openColorAdvisorModal() {
  const m = document.getElementById('modal-color-advisor');
  if (m) m.classList.add('active');
}

function openConfigKeyModal() {
  const m = document.getElementById('modal-config-key');
  if (m) m.classList.add('active');
}

function showSystemInfoModal() {
  const m = document.getElementById('modal-system-info');
  if (m) m.classList.add('active');
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.remove('active');
}

async function submitModalSizeAdvisor() {
  const height = parseFloat(document.getElementById('modal-size-height').value);
  const weight = parseFloat(document.getElementById('modal-size-weight').value);
  const gender = document.getElementById('modal-size-gender').value;
  const fit = document.getElementById('modal-size-fit').value;

  closeModal('modal-size-advisor');
  const query = `Tôi cao ${height}cm, nặng ${weight}kg, giới tính ${gender}, thích form ${fit}. Tư vấn size cho tôi nhé!`;
  openChatWithPrompt(query);
}

async function submitModalOutfitAdvisor() {
  const gender = document.getElementById('modal-outfit-gender').value;
  const occasion = document.getElementById('modal-outfit-occasion').value;
  const style = document.getElementById('modal-outfit-style').value;

  closeModal('modal-outfit-advisor');
  const query = `Gợi ý set đồ cho ${gender} đi ${occasion} theo phong cách ${style}`;
  openChatWithPrompt(query);
}

async function submitConfigKeyModal() {
  const key = document.getElementById('config-api-key').value.trim();
  const model = document.getElementById('config-model-name').value.trim();

  try {
    const res = await fetch('/api/config/llm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key, model: model })
    });
    const data = await res.json();
    closeModal('modal-config-key');
    showToast(data.message || "Cập nhật cấu hình thành công!");
    appendAssistantMessage(`✅ **Hệ thống AI đã cập nhật!**\nTrạng thái: ${key ? 'Kết nối LLM OpenRouter (' + model + ')' : 'Chế độ Offline AI Stylist & RAG TF-IDF'}.`);
  } catch (err) {
    alert("Lỗi: " + err.message);
  }
}
