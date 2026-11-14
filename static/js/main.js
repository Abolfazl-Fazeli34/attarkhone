// ==========================================================================
// عطارخونه - اسکریپت جامع، بهینه و پرسرعت فرانت‌اند (Vanilla JS بدون وابستگی)
// ==========================================================================

// ۱. توابع کمکی سراسری (Global Utilities)

// تبدیل ارقام انگلیسی به فارسی
function toPersianDigits(num) {
  if (num === null || num === undefined) return '';
  const farsiDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  return String(num).replace(/[0-9]/g, d => farsiDigits[+d]);
}

// فرمت پول با جداکننده سه رقمی و پسوند تومان
function formatToman(amount) {
  return Number(amount).toLocaleString('fa-IR') + ' تومان';
}

// دریافت ایمن توکن CSRF
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

// سامانه نمایش نوتیفیکیشن‌های شناور (Toast Notification)
window.showToast = function (message, type = 'success', duration = 3500) {
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
    success: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
    error: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    info: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    warning: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
  };

  toast.innerHTML = `
    <span class="toast-icon">${iconMap[type] || '•'}</span>
    <span class="toast-message">${message}</span>
    <button type="button" class="toast-close" aria-label="بستن"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
  `;

  container.appendChild(toast);

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
};

// تابع به‌روزرسانی مرتب‌سازی کاتالوگ با حفظ پارامترهای فیلتر (کارگاه ۱۸)
window.updateCatalogSort = function (sortVal) {
  const url = new URL(window.location.href);
  url.searchParams.set('sort', sortVal);
  url.searchParams.delete('page');
  window.location.href = url.toString();
};


// ۲. اجرای تعاملات پس از بارگذاری سند (DOM Ready)
document.addEventListener('DOMContentLoaded', function () {
  const csrftoken = getCookie('csrftoken') || (document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '');

  // ----------------------------------------------------
  // الف) ناوبری و منوهای هدر (Header Menus)
  // ----------------------------------------------------
  const menuToggle = document.getElementById('mobileMenuToggle');
  const siteNav = document.getElementById('siteNav');
  if (menuToggle && siteNav) {
    menuToggle.addEventListener('click', function () {
      siteNav.classList.toggle('mobile-active');
    });
  }

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

  // ----------------------------------------------------
  // ب) صفحه جزئیات کالا (Product Details & Variants - کارگاه ۱۳ و ۱۴)
  // ----------------------------------------------------
  const variantButtons = document.querySelectorAll('.variant-chips-wrap .variant-chip-btn[data-id]');
  const selectedVariantInput = document.getElementById('selectedVariantId');
  const dynamicPriceDisplay = document.getElementById('dynamicProductPrice');
  const dynamicOldPriceDisplay = document.getElementById('dynamicOldPrice');

  if (variantButtons.length > 0) {
    variantButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        variantButtons.forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');

        const variantId = this.dataset.id;
        const variantPrice = Number(this.dataset.price);

        if (selectedVariantInput) {
          selectedVariantInput.value = variantId;
        }

        if (dynamicPriceDisplay && !isNaN(variantPrice)) {
          dynamicPriceDisplay.textContent = variantPrice.toLocaleString('fa-IR') + ' تومان';

          const discount = parseInt(dynamicPriceDisplay.dataset.discount || '0', 10);
          if (discount > 0 && dynamicOldPriceDisplay) {
            const oldPrice = Math.round((variantPrice * 100) / (100 - discount) / 1000) * 1000;
            dynamicOldPriceDisplay.textContent = oldPrice.toLocaleString('fa-IR') + ' تومان';
          }
        }
      });
    });
  }

  // انتخاب نوع آسیاب / فرآوری
  const grindChips = document.querySelectorAll('#grindTypeChips .variant-chip-btn');
  const selectedGrindInput = document.getElementById('selectedGrindType');
  if (grindChips.length > 0) {
    grindChips.forEach(function (btn) {
      btn.addEventListener('click', function () {
        grindChips.forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');
        if (selectedGrindInput) {
          selectedGrindInput.value = this.dataset.grind || this.textContent.trim();
        }
      });
    });
  }

  // تصویر بندانگشتی کالا
  const thumbBoxes = document.querySelectorAll('.thumbnails-row .thumb-box');
  const mainProductImg = document.getElementById('mainProductImage');
  if (thumbBoxes.length > 0 && mainProductImg) {
    thumbBoxes.forEach(function (thumb) {
      thumb.addEventListener('click', function () {
        thumbBoxes.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        const img = this.querySelector('img');
        if (img) {
          mainProductImg.src = img.src;
        }
      });
    });
  }

  // تب‌های تخصصی (COA آزمایشگاهی، شیوه مصرف، پرسش و پاسخ)
  const tabButtons = document.querySelectorAll('.tab-nav-btn');
  const tabPanels = document.querySelectorAll('.tab-content-panel');
  if (tabButtons.length > 0) {
    tabButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        tabButtons.forEach(b => b.classList.remove('active'));
        tabPanels.forEach(p => p.classList.remove('active'));

        this.classList.add('active');
        const targetId = this.dataset.tab;
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) {
          targetPanel.classList.add('active');
        }
      });
    });
  }

  // فرم ثبت نظر و پرسش تخصصی کالا با ایجکس
  const qaForm = document.getElementById('expertQuestionForm');
  if (qaForm) {
    qaForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(qaForm);
      const submitBtn = qaForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      fetch(qaForm.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          window.showToast(data.message || 'دیدگاه شما با موفقیت ثبت شد.', 'success');
          qaForm.reset();
          setTimeout(() => { window.location.reload(); }, 1200);
        } else {
          window.showToast(data.message || 'خطا در ثبت دیدگاه', 'error');
        }
      })
      .catch(() => {
        qaForm.submit();
      })
      .finally(() => {
        if (submitBtn) submitBtn.disabled = false;
      });
    });
  }

  // ----------------------------------------------------
  // ج) اسلایدرها و کاروسل‌ها (Sliders & Carousels - کارگاه ۷)
  // ----------------------------------------------------
  const heroSlider = document.getElementById('heroSlider');
  const heroSlides = document.querySelectorAll('.hero-slide');
  const heroDots = document.querySelectorAll('.hero-dot');
  const heroPrev = document.getElementById('heroPrevBtn');
  const heroNext = document.getElementById('heroNextBtn');

  if (heroSlides.length > 0) {
    let currentSlide = 0;
    let autoPlayTimer = null;

    function goToSlide(index) {
      heroSlides[currentSlide].classList.remove('active');
      if (heroDots[currentSlide]) heroDots[currentSlide].classList.remove('active');

      currentSlide = (index + heroSlides.length) % heroSlides.length;

      heroSlides[currentSlide].classList.add('active');
      if (heroDots[currentSlide]) heroDots[currentSlide].classList.add('active');
    }

    function nextSlide() { goToSlide(currentSlide + 1); }
    function prevSlide() { goToSlide(currentSlide - 1); }

    if (heroNext) heroNext.addEventListener('click', nextSlide);
    if (heroPrev) heroPrev.addEventListener('click', prevSlide);

    heroDots.forEach(function (dot) {
      dot.addEventListener('click', function () {
        const slideIdx = parseInt(this.dataset.slide, 10);
        goToSlide(slideIdx);
      });
    });

    function startAutoPlay() {
      if (heroSlides.length > 1 && !autoPlayTimer) {
        autoPlayTimer = setInterval(nextSlide, 6000);
      }
    }

    function stopAutoPlay() {
      if (autoPlayTimer) {
        clearInterval(autoPlayTimer);
        autoPlayTimer = null;
      }
    }

    startAutoPlay();
    if (heroSlider) {
      heroSlider.addEventListener('mouseenter', stopAutoPlay);
      heroSlider.addEventListener('mouseleave', startAutoPlay);
    }
  }

  // اسلایدر افقی فرآورده‌های محبوب
  const carouselTrack = document.getElementById('popularCarouselTrack');
  const prodPrevBtn = document.getElementById('prodCarouselPrev');
  const prodNextBtn = document.getElementById('prodCarouselNext');

  if (carouselTrack && prodPrevBtn && prodNextBtn) {
    function getScrollStep() {
      const card = carouselTrack.querySelector('.carousel-product-item');
      return card ? card.offsetWidth + 16 : 280;
    }

    prodNextBtn.addEventListener('click', function () {
      const step = getScrollStep();
      carouselTrack.scrollBy({ left: -step, behavior: 'smooth' });
    });

    prodPrevBtn.addEventListener('click', function () {
      const step = getScrollStep();
      carouselTrack.scrollBy({ left: step, behavior: 'smooth' });
    });

    // اسکرول نرم با درگ ماوس
    let isDown = false;
    let startX = 0;
    let scrollStart = 0;

    carouselTrack.addEventListener('mousedown', function (e) {
      isDown = true;
      carouselTrack.classList.add('is-dragging');
      startX = e.pageX - carouselTrack.offsetLeft;
      scrollStart = carouselTrack.scrollLeft;
    });

    carouselTrack.addEventListener('mouseleave', function () {
      isDown = false;
      carouselTrack.classList.remove('is-dragging');
    });

    carouselTrack.addEventListener('mouseup', function () {
      isDown = false;
      carouselTrack.classList.remove('is-dragging');
    });

    carouselTrack.addEventListener('mousemove', function (e) {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - carouselTrack.offsetLeft;
      const walk = (x - startX) * 1.5;
      carouselTrack.scrollLeft = scrollStart - walk;
    });
  }

  // ----------------------------------------------------
  // د) عملیات بلادرنگ سبد خرید و علاقه‌مندی‌ها (AJAX Cart & Wishlist)
  // ----------------------------------------------------
  
  // ۱. افزودن به سبد خرید بدون رفرش (.ajax-add-cart-form)
  const addCartForms = document.querySelectorAll('.ajax-add-cart-form');
  addCartForms.forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const submitBtn = this.querySelector('button[type="submit"]');
      const origContent = submitBtn ? submitBtn.innerHTML : '';

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner-inline"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10"/></svg></span><span>در حال ثبت...</span>';
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
          const cartBadge = document.getElementById('headerCartBadge');
          if (cartBadge) {
            cartBadge.textContent = toPersianDigits(data.cart_count);
            cartBadge.classList.add('badge-bump');
            setTimeout(() => cartBadge.classList.remove('badge-bump'), 400);
          }
          window.showToast(data.message, 'success');
        } else {
          window.showToast(data.message || 'خطا در افزودن به سبد خرید', 'error');
        }
      })
      .catch(() => {
        window.showToast('خطا در برقراری ارتباط با سرور', 'error');
      })
      .finally(() => {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = origContent;
        }
      });
    });
  });

  // ۲. افزودن / حذف از علاقه‌مندی‌ها (.btn-wishlist-toggle)
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
        window.showToast('برای نشان کردن کالاها، لطفاً ابتدا وارد حساب خود شوید.', 'warning');
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
          const wishlistCard = document.getElementById(`wishlist-card-${productId}`);
          if (wishlistCard) {
            wishlistCard.style.opacity = '0';
            wishlistCard.style.transform = 'scale(0.9)';
            setTimeout(() => wishlistCard.remove(), 250);
          }
        }

        const badge = document.getElementById('headerWishlistBadge');
        if (badge) {
          if (data.wishlist_count > 0) {
            badge.style.display = 'flex';
            badge.textContent = toPersianDigits(data.wishlist_count);
          } else {
            badge.style.display = 'none';
          }
        }

        window.showToast(data.message, 'success');
      }
    })
    .catch(() => {
      window.showToast('خطا در تغییر وضعیت علاقه‌مندی‌ها', 'error');
    });
  });

  // ۳. استپر تعداد در سبد خرید (.ajax-cart-stepper)
  document.addEventListener('click', function (e) {
    const stepperBtn = e.target.closest('.ajax-cart-stepper');
    if (!stepperBtn) return;

    const itemId = stepperBtn.dataset.itemId;
    const action = stepperBtn.dataset.action;
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
          window.showToast(data.message || 'کالا از سبد حذف شد', 'info');
        } else {
          const valEl = document.getElementById(`stepper-val-${itemId}`);
          if (valEl) valEl.textContent = toPersianDigits(data.quantity);

          const priceEl = document.getElementById(`item-price-${itemId}`);
          if (priceEl) priceEl.textContent = `${toPersianDigits(data.item_total)} تومان`;
        }

        const totalPayableEl = document.getElementById('cartTotalPayable');
        if (totalPayableEl) {
          totalPayableEl.textContent = `${toPersianDigits(data.cart_subtotal)} تومان`;
        }

        const headerBadge = document.getElementById('headerCartBadge');
        if (headerBadge) {
          headerBadge.textContent = toPersianDigits(data.cart_count);
        }
      }
    })
    .catch(() => {
      window.showToast('خطا در به‌روزرسانی تعداد کالا', 'error');
    })
    .finally(() => {
      stepperBtn.disabled = false;
    });
  });

  // ۴. حذف ردیف سبد خرید با ایجکس (.ajax-remove-form)
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

          window.showToast(data.message, 'info');
        }
      })
      .catch(() => {
        window.showToast('خطا در حذف کالا', 'error');
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

  // ۵. محاسبه بلادرنگ هزینه حامل و کادوپیچی در مرحله تسویه حساب (Checkout Live Carrier & Gift Calculations)
  const carrierRadios = document.querySelectorAll('.carrier-radio');
  const shippingDisplay = document.getElementById('checkoutShippingCostDisplay');
  const grandTotalDisplay = document.getElementById('checkoutGrandTotalDisplay');
  const giftCheckbox = document.getElementById('checkoutGiftCheckbox');
  const giftMessageBox = document.getElementById('checkoutGiftMessageBox');
  const giftSummaryRow = document.getElementById('checkoutGiftWrapSummaryRow');
  const giftCostDisplay = document.getElementById('checkoutGiftCostDisplay');
  const giftWrapLabel = document.getElementById('checkoutGiftWrapLabel');

  if (carrierRadios.length > 0 && shippingDisplay && grandTotalDisplay) {
    function updateCheckoutCalculations() {
      const selected = document.querySelector('.carrier-radio:checked') || carrierRadios[0];
      const shippingCost = parseInt(selected.dataset.cost) || 0;
      const subtotal = parseInt(document.getElementById('rawSubtotal').value) || 0;
      const discount = parseInt(document.getElementById('rawDiscountAmount').value) || 0;

      let currentGiftCost = 0;
      if (giftCheckbox) {
        const unitCost = parseInt(giftCheckbox.dataset.unitCost) || 25000;
        if (giftCheckbox.checked) {
          currentGiftCost = unitCost;
          if (giftMessageBox) giftMessageBox.style.display = 'block';
          if (giftSummaryRow) giftSummaryRow.style.display = 'flex';
          if (giftCostDisplay) giftCostDisplay.textContent = formatToman(currentGiftCost);
          if (giftWrapLabel) {
            giftWrapLabel.style.borderColor = 'var(--primary)';
            giftWrapLabel.style.background = '#f7faf8';
          }
        } else {
          currentGiftCost = 0;
          if (giftMessageBox) giftMessageBox.style.display = 'none';
          if (giftSummaryRow) giftSummaryRow.style.display = 'none';
          if (giftWrapLabel) {
            giftWrapLabel.style.borderColor = 'var(--border)';
            giftWrapLabel.style.background = '#fafafa';
          }
        }
        const rawGiftCostInput = document.getElementById('rawGiftCost');
        if (rawGiftCostInput) rawGiftCostInput.value = currentGiftCost;
      } else {
        currentGiftCost = parseInt(document.getElementById('rawGiftCost')?.value) || 0;
      }

      if (shippingCost === 0) {
        shippingDisplay.innerHTML = '<span style="color: #15803d; font-weight: 700;">رایگان</span>';
      } else {
        shippingDisplay.textContent = formatToman(shippingCost);
      }

      const grandTotal = Math.max(0, subtotal - discount + currentGiftCost + shippingCost);
      grandTotalDisplay.textContent = formatToman(grandTotal);
    }

    carrierRadios.forEach(radio => {
      radio.addEventListener('change', updateCheckoutCalculations);
    });

    if (giftCheckbox) {
      giftCheckbox.addEventListener('change', updateCheckoutCalculations);
    }

    updateCheckoutCalculations();
  }
});
