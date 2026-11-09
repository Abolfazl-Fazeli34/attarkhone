// جاوااسکریپت بهینه، سریع و کلاسیک عطارخونه (Vanilla JS)

// تابع سراسری به‌روزرسانی مرتب‌سازی کاتالوگ با حفظ فیلترها (کارگاه ۱۸)
window.updateCatalogSort = function (sortVal) {
  const url = new URL(window.location.href);
  url.searchParams.set('sort', sortVal);
  url.searchParams.delete('page');
  window.location.href = url.toString();
};

document.addEventListener('DOMContentLoaded', function () {
  // ۱. کنترل منوی همبرگری موبایل (کارگاه ۲۵)
  const menuToggle = document.getElementById('mobileMenuToggle');
  const siteNav = document.getElementById('siteNav');

  if (menuToggle && siteNav) {
    menuToggle.addEventListener('click', function () {
      siteNav.classList.toggle('mobile-active');
    });
  }

  // ۲. مدیریت انتخاب مشخصه‌های وزنی و فرآوری در صفحه محصول (کارگاه ۱۳)
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

  // تعویض تصویر بندانگشتی در صفحه محصول
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

  // تب‌های صفحه جزئیات کالا (COA، دوز، پرسش و پاسخ)
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

  // ثبت دیدگاه و پرسش تخصصی کالا با اتصال واقعی به بک‌اند
  const qaForm = document.getElementById('expertQuestionForm');
  if (qaForm) {
    qaForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(qaForm);
      const submitBtn = qaForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      fetch(qaForm.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          if (typeof showToast === 'function') {
            showToast(data.message || 'دیدگاه شما با موفقیت ثبت گردید.', 'success');
          }
          qaForm.reset();
          setTimeout(() => {
            window.location.reload();
          }, 1200);
        } else {
          if (typeof showToast === 'function') {
            showToast(data.message || 'خطا در ثبت دیدگاه', 'error');
          }
        }
      })
      .catch(err => {
        qaForm.submit();
      })
      .finally(() => {
        if (submitBtn) submitBtn.disabled = false;
      });
    });
  }

  // ۳. اسلایدر چنداسلایده تعاملی و خودکار هیرو (کارگاه ۷)
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

    function nextSlide() {
      goToSlide(currentSlide + 1);
    }

    function prevSlide() {
      goToSlide(currentSlide - 1);
    }

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

  // ۴. اسلایدر افقی فرآورده‌های محبوب و برگزیده
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

    // قابلیت درگ ماوس برای اسکرول افقی دسکتاپ
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
});
