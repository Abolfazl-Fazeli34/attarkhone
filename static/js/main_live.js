/**
 * عطارخونه - تعاملات پویا و بلادرنگ (Live & Dynamic AJAX Interactions)
 * شامل: سبد خرید ایجکس، اعلانات توست شناور، مدیریت علاقه‌مندی‌ها و استپر تعداد
 */

// تابع کمکی تبدیل ارقام انگلیسی به فارسی
function toPersianDigits(num) {
  const farsiDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  return String(num).replace(/[0-9]/g, function (d) {
    return farsiDigits[+d];
  });
}

// تابع کمکی فرمت پول با جداکننده سه رقمی
function formatToman(amount) {
  return Number(amount).toLocaleString('fa-IR') + ' تومان';
}

// دریافت توکن CSRF از کوکی یا فرم
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// سامانه نمایش نوتیفیکیشن‌های توست شناور (Toast Notification)
function showToast(message, type = 'success', duration = 3500) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-item toast-${type}`;

  const iconMap = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
    warning: '⚠'
  };

  toast.innerHTML = `
    <span class="toast-icon">${iconMap[type] || '•'}</span>
    <span class="toast-message">${message}</span>
    <button type="button" class="toast-close" aria-label="بستن">✕</button>
  `;

  container.appendChild(toast);

  // نمایش نرم
  requestAnimationFrame(() => {
    toast.classList.add('toast-show');
  });

  const closeBtn = toast.querySelector('.toast-close');
  const removeToast = () => {
    toast.classList.remove('toast-show');
    toast.classList.add('toast-hide');
    setTimeout(() => toast.remove(), 300);
  };

  closeBtn.addEventListener('click', removeToast);

  if (duration > 0) {
    setTimeout(removeToast, duration);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const csrftoken = getCookie('csrftoken') || (document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '');

  // ۱. منوی کاربری کشویی هدر (User Dropdown Menu)
  const userBtn = document.getElementById('userMenuBtn');
  const userDropdown = document.getElementById('userDropdownMenu');

  if (userBtn && userDropdown) {
    userBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      const isOpen = userDropdown.classList.contains('show');
      userDropdown.classList.toggle('show');
      userBtn.setAttribute('aria-expanded', !isOpen);
    });

    document.addEventListener('click', function (e) {
      if (!userDropdown.contains(e.target) && !userBtn.contains(e.target)) {
        userDropdown.classList.remove('show');
        userBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // ۲. افزودن بلادرنگ به سبد خرید با ایجکس (.ajax-add-cart-form)
  const addCartForms = document.querySelectorAll('.ajax-add-cart-form');
  addCartForms.forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const submitBtn = this.querySelector('button[type="submit"]');
      const origContent = submitBtn ? submitBtn.innerHTML : '';

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>⏳</span><span>در حال ثبت...</span>';
      }

      const formData = new FormData(this);

      fetch(`/orders/cart/add-ajax/${productId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // به‌روزرسانی نشانگر سبد خرید هدر
          const cartBadge = document.getElementById('headerCartBadge');
          if (cartBadge) {
            cartBadge.textContent = toPersianDigits(data.cart_count);
            cartBadge.classList.add('badge-bump');
            setTimeout(() => cartBadge.classList.remove('badge-bump'), 400);
          }
          showToast(data.message, 'success');
        } else {
          showToast(data.message || 'خطا در افزودن به سبد خرید', 'error');
        }
      })
      .catch(err => {
        console.error(err);
        showToast('خطا در برقراری ارتباط با سرور', 'error');
      })
      .finally(() => {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = origContent;
        }
      });
    });
  });

  // ۳. کلید افزودن/حذف از لیست علاقه‌مندی‌ها (.btn-wishlist-toggle)
  document.addEventListener('click', function (e) {
    const toggleBtn = e.target.closest('.btn-wishlist-toggle, .btn-wishlist-toggle-round');
    if (!toggleBtn) return;

    e.preventDefault();
    const productId = toggleBtn.dataset.productId;
    if (!productId) return;

    fetch(`/shop/wishlist/toggle/${productId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
      }
    })
    .then(async res => {
      const data = await res.json();
      if (res.status === 401 || data.require_login) {
        showToast('برای نشان کردن کالاها، لطفاً ابتدا وارد حساب خود شوید.', 'warning');
        setTimeout(() => {
          window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
        }, 1200);
        return;
      }

      if (data.success) {
        if (data.is_added) {
          toggleBtn.classList.add('active');
          const svg = toggleBtn.querySelector('svg');
          if (svg) {
            svg.setAttribute('fill', '#ef4444');
            svg.setAttribute('stroke', '#ef4444');
          }
        } else {
          toggleBtn.classList.remove('active');
          const svg = toggleBtn.querySelector('svg');
          if (svg) {
            svg.setAttribute('fill', 'none');
            svg.setAttribute('stroke', 'currentColor');
          }
          // اگر در صفحه لیست علاقه‌مندی‌ها هستیم، کارت را حذف کن
          const wishlistCard = document.getElementById(`wishlist-card-${productId}`);
          if (wishlistCard) {
            wishlistCard.style.opacity = '0';
            wishlistCard.style.transform = 'scale(0.9)';
            setTimeout(() => wishlistCard.remove(), 250);
          }
        }

        // به‌روزرسانی بج علاقه‌مندی‌ها در هدر
        const badge = document.getElementById('headerWishlistBadge');
        if (badge) {
          if (data.wishlist_count > 0) {
            badge.style.display = 'flex';
            badge.textContent = toPersianDigits(data.wishlist_count);
          } else {
            badge.style.display = 'none';
          }
        }

        showToast(data.message, 'success');
      }
    })
    .catch(err => {
      console.error(err);
      showToast('خطا در تغییر وضعیت علاقه‌مندی‌ها', 'error');
    });
  });

  // ۴. مدیریت استپر تعداد در سبد خرید (.ajax-cart-stepper)
  document.addEventListener('click', function (e) {
    const stepperBtn = e.target.closest('.ajax-cart-stepper');
    if (!stepperBtn) return;

    const itemId = stepperBtn.dataset.itemId;
    const action = stepperBtn.dataset.action; // 'increase' or 'decrease'
    if (!itemId || !action) return;

    stepperBtn.disabled = true;

    const formData = new FormData();
    formData.append('action', action);

    fetch(`/orders/cart/update-ajax/${itemId}/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        if (data.is_deleted) {
          const row = document.getElementById(`cart-item-${itemId}`);
          if (row) {
            row.style.opacity = '0';
            row.style.transform = 'translateX(20px)';
            setTimeout(() => {
              row.remove();
              checkEmptyCartState(data.cart_count);
            }, 250);
          }
          showToast(data.message || 'کالا از سبد حذف شد', 'info');
        } else {
          const valEl = document.getElementById(`stepper-val-${itemId}`);
          if (valEl) valEl.textContent = toPersianDigits(data.quantity);

          const priceEl = document.getElementById(`item-price-${itemId}`);
          if (priceEl) priceEl.textContent = `${toPersianDigits(data.item_total)} تومان`;
        }

        // به‌روزرسانی جمع کل سبد
        const totalPayableEl = document.getElementById('cartTotalPayable');
        if (totalPayableEl) {
          totalPayableEl.textContent = `${toPersianDigits(data.cart_subtotal)} تومان`;
        }

        // به‌روزرسانی بج هدر
        const headerBadge = document.getElementById('headerCartBadge');
        if (headerBadge) {
          headerBadge.textContent = toPersianDigits(data.cart_count);
        }
      }
    })
    .catch(err => {
      console.error(err);
      showToast('خطا در به‌روزرسانی تعداد کالا', 'error');
    })
    .finally(() => {
      stepperBtn.disabled = false;
    });
  });

  // ۵. حذف ردیف سبد خرید با ایجکس (.ajax-remove-form)
  const removeForms = document.querySelectorAll('.ajax-remove-form');
  removeForms.forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const itemId = this.dataset.itemId;
      if (!itemId) return;

      fetch(`/orders/cart/remove-ajax/${itemId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const row = document.getElementById(`cart-item-${itemId}`);
          if (row) {
            row.style.opacity = '0';
            row.style.transform = 'translateX(20px)';
            setTimeout(() => {
              row.remove();
              checkEmptyCartState(data.cart_count);
            }, 250);
          }

          const totalPayableEl = document.getElementById('cartTotalPayable');
          if (totalPayableEl) {
            totalPayableEl.textContent = `${toPersianDigits(data.cart_subtotal)} تومان`;
          }

          const headerBadge = document.getElementById('headerCartBadge');
          if (headerBadge) {
            headerBadge.textContent = toPersianDigits(data.cart_count);
          }

          showToast(data.message, 'info');
        }
      })
      .catch(err => {
        console.error(err);
        showToast('خطا در حذف کالا', 'error');
      });
    });
  });

  function checkEmptyCartState(cartCount) {
    if (cartCount === 0) {
      const container = document.querySelector('.cart-mockup-container');
      if (container) {
        container.innerHTML = `
          <div style="text-align: center; padding: 40px; background: #fff; border-radius: var(--radius-md); border: 1px dashed var(--border);">
            <p style="color: #64748b; font-size: 13px; margin-bottom: 12px;">سبد خرید شما در حال حاضر خالی است.</p>
            <a href="/shop/" class="btn-wide-dark-green-checkout" style="max-width: 200px; margin: 0 auto; padding: 8px;">
              مشاهده فروشگاه
            </a>
          </div>
        `;
      }
    }
  }

  // ۶. محاسبه بلادرنگ هزینه حامل در مرحله تسویه حساب (Checkout Live Carrier Cost)
  const carrierRadios = document.querySelectorAll('.carrier-radio');
  const shippingDisplay = document.getElementById('checkoutShippingCostDisplay');
  const grandTotalDisplay = document.getElementById('checkoutGrandTotalDisplay');

  if (carrierRadios.length > 0 && shippingDisplay && grandTotalDisplay) {
    function updateCheckoutCalculations() {
      const selected = document.querySelector('.carrier-radio:checked') || carrierRadios[0];
      const shippingCost = parseInt(selected.dataset.cost) || 0;
      const subtotal = parseInt(document.getElementById('rawSubtotal').value) || 0;
      const giftCost = parseInt(document.getElementById('rawGiftCost').value) || 0;
      const discount = parseInt(document.getElementById('rawDiscountAmount').value) || 0;

      if (shippingCost === 0) {
        shippingDisplay.innerHTML = '<span style="color: #15803d; font-weight: 700;">رایگان</span>';
      } else {
        shippingDisplay.textContent = formatToman(shippingCost);
      }

      const grandTotal = Math.max(0, subtotal - discount + giftCost + shippingCost);
      grandTotalDisplay.textContent = formatToman(grandTotal);
    }

    carrierRadios.forEach(radio => {
      radio.addEventListener('change', updateCheckoutCalculations);
    });

    updateCheckoutCalculations();
  }
});
