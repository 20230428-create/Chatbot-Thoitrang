// Store & Cart State
let cart = JSON.parse(localStorage.getItem('fashion_cart') || '[]');

document.addEventListener('DOMContentLoaded', () => {
  updateCartCounter();
});

// Cart Counter
function updateCartCounter() {
  const counter = document.getElementById('cart-counter');
  const totalItems = cart.reduce((acc, item) => acc + item.qty, 0);
  if (counter) {
    counter.innerText = totalItems;
  }
}

// Add to Cart
function addToCart(id, name, price, image, size = 'M') {
  const existing = cart.find(item => item.id === id && item.size === size);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ id, name, price, image, size, qty: 1 });
  }
  localStorage.setItem('fashion_cart', JSON.stringify(cart));
  updateCartCounter();
  showToast(`Đã thêm "${name}" (Size ${size}) vào giỏ hàng!`);
}

// Toggle Cart Drawer
function toggleCartDrawer() {
  const overlay = document.getElementById('cart-drawer-overlay');
  if (!overlay) return;

  if (overlay.classList.contains('active')) {
    overlay.classList.remove('active');
  } else {
    overlay.classList.add('active');
    renderCartList();
  }
}

function renderCartList() {
  const list = document.getElementById('cart-items-list');
  const totalElem = document.getElementById('cart-total-price');
  if (!list) return;

  if (cart.length === 0) {
    list.innerHTML = `<div style="text-align: center; color: #94a3b8; padding: 40px;">Giỏ hàng của bạn đang trống.</div>`;
    if (totalElem) totalElem.innerText = "0đ";
    return;
  }

  let total = 0;
  list.innerHTML = cart.map((item, index) => {
    total += item.price * item.qty;
    return `
      <div style="display: flex; gap: 12px; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px; margin-bottom: 12px;">
        <img src="${item.image}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;">
        <div style="flex: 1; min-width: 0;">
          <h4 style="font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${item.name}</h4>
          <div style="font-size: 12px; color: #64748b;">Size: <strong>${item.size}</strong> | ${Number(item.price).toLocaleString()}đ</div>
          <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
            <button onclick="changeCartQty(${index}, -1)" style="padding: 2px 8px; border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 4px; cursor: pointer;">-</button>
            <span style="font-size: 12px; font-weight: 700;">${item.qty}</span>
            <button onclick="changeCartQty(${index}, 1)" style="padding: 2px 8px; border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 4px; cursor: pointer;">+</button>
          </div>
        </div>
        <button onclick="removeCartItem(${index})" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 16px;">🗑️</button>
      </div>
    `;
  }).join('');

  if (totalElem) totalElem.innerText = `${total.toLocaleString()}đ`;
}

function changeCartQty(index, delta) {
  if (cart[index]) {
    cart[index].qty += delta;
    if (cart[index].qty <= 0) {
      cart.splice(index, 1);
    }
    localStorage.setItem('fashion_cart', JSON.stringify(cart));
    updateCartCounter();
    renderCartList();
  }
}

function removeCartItem(index) {
  cart.splice(index, 1);
  localStorage.setItem('fashion_cart', JSON.stringify(cart));
  updateCartCounter();
  renderCartList();
}

function simulateCheckout() {
  if (cart.length === 0) {
    alert("Giỏ hàng của bạn đang trống!");
    return;
  }
  alert("🎉 Cảm ơn bạn đã đặt hàng thành công! AI Stylist luôn sẵn sàng đồng hành cùng bạn.");
  cart = [];
  localStorage.setItem('fashion_cart', JSON.stringify(cart));
  updateCartCounter();
  toggleCartDrawer();
}

// Product Detail Modal
let selectedModalProductSize = 'M';

async function viewProductDetail(productId) {
  const modal = document.getElementById('product-detail-modal');
  const modalBody = document.getElementById('modal-body-content');
  if (!modal || !modalBody) return;

  modalBody.innerHTML = `<div style="padding: 40px; text-align: center; grid-column: 1/-1;">Đang tải chi tiết...</div>`;
  modal.classList.add('active');

  try {
    const res = await fetch(`/api/products/${productId}`);
    const data = await res.json();
    const p = data.product;
    selectedModalProductSize = p.sizes[0] || 'M';

    modalBody.innerHTML = `
      <div style="background: #f8fafc; padding: 20px; display: flex; align-items: center; justify-content: center;">
        <img src="${p.image}" alt="${p.name}" style="max-width: 100%; max-height: 380px; object-fit: contain; border-radius: 12px;">
      </div>
      <div style="padding: 24px; display: flex; flex-direction: column;">
        <div style="font-size: 12px; color: var(--accent); font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">
          ${p.gender} • ${p.category_name}
        </div>
        <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 10px; line-height: 1.3;">${p.name}</h2>
        <div style="font-size: 22px; font-weight: 800; color: #b8860b; margin-bottom: 14px;">
          ${Number(p.price).toLocaleString()}đ
        </div>
        <p style="font-size: 13.5px; color: #475569; line-height: 1.5; margin-bottom: 16px;">
          ${p.description}
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; margin-bottom: 16px; background: #f8fafc; padding: 10px; border-radius: 8px;">
          <div>🎨 Màu: <strong>${p.color}</strong></div>
          <div>✨ Phong cách: <strong>${p.style.split(',')[0]}</strong></div>
          <div>🧵 Chất liệu: <strong>${p.material || 'Cao cấp'}</strong></div>
          <div>🎯 Dịp: <strong>${p.occasion.split(',')[0]}</strong></div>
        </div>
        
        <div style="margin-bottom: 16px;">
          <div style="font-size: 12px; font-weight: 600; margin-bottom: 6px;">Chọn Size:</div>
          <div style="display: flex; gap: 6px;" id="modal-sizes-group">
            ${p.sizes.map((s, idx) => `
              <button class="size-choice-btn" onclick="selectModalSize(this, '${s}')" style="padding: 4px 12px; border: 1px solid #cbd5e1; background: ${idx === 0 ? '#111' : '#fff'}; color: ${idx === 0 ? '#fff' : '#111'}; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 12px;">
                ${s}
              </button>
            `).join('')}
          </div>
        </div>

        <div style="display: flex; gap: 10px; margin-top: auto;">
          <button class="btn-submit-modal" onclick="addToCartFromModal(${p.id}, '${p.name}', ${p.price}, '${p.image}')" style="flex: 1; margin: 0; padding: 10px;">
            🛒 Thêm Vào Giỏ
          </button>
          <button class="btn-submit-modal" onclick="closeModal('product-detail-modal'); openChatWithPrompt('Mẫu ${p.name} này có thể phối với quần hoặc phụ kiện gì đẹp nhất?');" style="flex: 1; margin: 0; padding: 10px; background: #fff8e7; color: #856404; border-color: var(--accent);">
            ✨ Hỏi Stylist
          </button>
        </div>
      </div>
    `;
  } catch (err) {
    modalBody.innerHTML = `<div style="padding: 30px; color: red;">Lỗi tải chi tiết: ${err.message}</div>`;
  }
}

function selectModalSize(btn, size) {
  document.querySelectorAll('#modal-sizes-group button').forEach(b => {
    b.style.background = '#fff';
    b.style.color = '#111';
  });
  btn.style.background = '#111';
  btn.style.color = '#fff';
  selectedModalProductSize = size;
}

function addToCartFromModal(id, name, price, image) {
  addToCart(id, name, price, image, selectedModalProductSize);
  closeModal('product-detail-modal');
}

// Toast
function showToast(msg) {
  const toast = document.createElement('div');
  toast.className = 'toast-msg';
  toast.style.cssText = `
    position: fixed;
    bottom: 24px;
    left: 24px;
    background: #111;
    color: #fad02c;
    border: 1px solid #d4af37;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 13.5px;
    font-weight: 600;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    z-index: 3000;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: fadeIn 0.25s ease;
  `;
  toast.innerHTML = `<span>✨</span><span>${msg}</span>`;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 2800);
}
