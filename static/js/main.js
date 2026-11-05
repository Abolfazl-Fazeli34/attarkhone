// جاوااسکریپت بهینه و سبک عطارخونه (Vanilla JS)
document.addEventListener('DOMContentLoaded', function () {
  // ۱. کنترل منوی همبرگری موبایل (کارگاه ۲۵)
  const menuToggle = document.getElementById('mobileMenuToggle');
  const siteNav = document.getElementById('siteNav');

  if (menuToggle && siteNav) {
    menuToggle.addEventListener('click', function () {
      siteNav.classList.toggle('mobile-active');
    });
  }

  // ۲. مدیریت انتخاب مشخصه‌های وزنی در صفحه محصول (کارگاه ۱۳)
  const variantButtons = document.querySelectorAll('.variant-btn');
  const selectedVariantInput = document.getElementById('selectedVariantId');
  const dynamicPriceDisplay = document.getElementById('dynamicProductPrice');

  if (variantButtons.length > 0) {
    variantButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        variantButtons.forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');

        const variantId = this.dataset.id;
        const variantPrice = this.dataset.price;

        if (selectedVariantInput) {
          selectedVariantInput.value = variantId;
        }

        if (dynamicPriceDisplay && variantPrice) {
          const formatted = Number(variantPrice).toLocaleString('fa-IR');
          dynamicPriceDisplay.textContent = formatted + ' تومان';
        }
      });
    });
  }

  // ۳. اسلایدر صفحه نخست (کارگاه ۷)
  const slides = document.querySelectorAll('.slider-container .slide');
  if (slides.length > 1) {
    let currentSlide = 0;
    slides.forEach((s, idx) => {
      s.style.display = idx === 0 ? 'block' : 'none';
    });

    setInterval(function () {
      slides[currentSlide].style.display = 'none';
      currentSlide = (currentSlide + 1) % slides.length;
      slides[currentSlide].style.display = 'block';
    }, 6000);
  }
});
