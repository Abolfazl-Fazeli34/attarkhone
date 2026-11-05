// اسکریپت تعاملی موتور عارضه‌یاب و استعلام تداخلات دارویی
document.addEventListener('DOMContentLoaded', function () {
  const drugSelect = document.getElementById('chemicalDrugSelect');
  const interactionResultsBox = document.getElementById('interactionResultsBox');

  if (drugSelect && interactionResultsBox) {
    drugSelect.addEventListener('change', function () {
      const drugId = this.value;
      if (!drugId) {
        interactionResultsBox.innerHTML = '';
        interactionResultsBox.style.display = 'none';
        return;
      }

      interactionResultsBox.innerHTML = '<p class="text-muted">در حال بررسی پایگاه داده تداخلات دارویی...</p>';
      interactionResultsBox.style.display = 'block';

      fetch(`/remedy/api/check-drug/?drug_id=${drugId}`)
        .then(response => response.json())
        .then(data => {
          if (data.status === 'ok') {
            if (data.interactions_count === 0) {
              interactionResultsBox.innerHTML = `
                <div class="interaction-box warning" style="background:#e8f5e9; border-color:#81c784; color:#1b5e20;">
                  <div>
                    <strong>وضعیت ایمن:</strong> تداخل خطرناکی بین داروی <b>${data.drug_name}</b> و گیاهان استاندارد عطارخونه ثبت نشده است. با خیال آسوده می‌توانید طبق دستور مصرف نمایید.
                  </div>
                </div>`;
            } else {
              let html = `<div style="margin-bottom:10px;"><b>هشدارهای بالینی شناسایی‌شده برای داروی «${data.drug_name}» (${data.drug_category}):</b></div>`;
              data.interactions.forEach(inter => {
                const boxClass = inter.severity === 'danger' ? 'danger' : 'warning';
                html += `
                  <div class="interaction-box ${boxClass}">
                    <div>
                      <div style="font-weight:bold; margin-bottom:4px;">⛔ گیاه دارویی حساس: ${inter.product_name} (${inter.severity_display})</div>
                      <div style="font-size:13px;">${inter.warning_text}</div>
                    </div>
                  </div>`;
              });
              interactionResultsBox.innerHTML = html;
            }
          } else {
            interactionResultsBox.innerHTML = `<p class="text-danger">${data.message}</p>`;
          }
        })
        .catch(err => {
          interactionResultsBox.innerHTML = '<p class="text-danger">خطا در برقراری ارتباط با سامانه بررسی تداخلات.</p>';
        });
    });
  }
});
