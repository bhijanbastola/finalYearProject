let cart = [];
let totalCost = 0;

// ===== ADD / REMOVE BUTTON =====
document.querySelectorAll(".cart-btn").forEach(btn => {
  btn.addEventListener("click", () => {

    const card = btn.closest(".equipment-card");
    const id = card.dataset.id;
    const name = card.dataset.name;
    const price = parseFloat(card.dataset.price);

    let item = cart.find(i => i.id === id);

    if (item) {
      cart = cart.filter(i => i.id !== id);
      btn.textContent = "Add to Cart";
      btn.classList.remove("added");
    } else {
      cart.push({ id, name, price, qty: 1 });
      btn.textContent = "Remove";
      btn.classList.add("added");
    }

    renderCart();
  });
});


// ===== INCREASE =====
function increase(id) {
  let item = cart.find(i => i.id === id);
  if (item) {
    item.qty++;
    renderCart();
  }
}

// ===== DECREASE =====
function decrease(id) {
  let item = cart.find(i => i.id === id);

  if (!item) return;

  item.qty--;

  if (item.qty <= 0) {
    cart = cart.filter(i => i.id !== id);

    // reset button UI
    let btn = document.querySelector(
      `.equipment-card[data-id='${id}'] .cart-btn`
    );
    if (btn) {
      btn.textContent = "Add to Cart";
      btn.classList.remove("added");
    }
  }

  renderCart();
}


// ===== RENDER CART =====
function renderCart() {
  let container = document.getElementById("cartList");
  let totalEl = document.getElementById("total");

  container.innerHTML = "";
  totalCost = 0;

  cart.forEach(item => {
    totalCost += item.price * item.qty;

    container.innerHTML += `
      <div class="cart-item">
        <div>
          ${item.name} <br>
          $${item.price} × ${item.qty}
        </div>

        <div class="qty-controls">
          <button onclick="decrease('${item.id}')">-</button>
          <span>${item.qty}</span>
          <button onclick="increase('${item.id}')">+</button>
        </div>
      </div>
    `;
  });

  totalEl.textContent = totalCost;
}


// ===== SAVE CART BEFORE NAVIGATION =====
document.querySelector(".package-btn")?.addEventListener("click", () => {
  localStorage.setItem("cart", JSON.stringify(cart));
  localStorage.setItem("totalCost", totalCost);
});