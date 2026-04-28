// static/js/main.js
// سكربت عام للموقع — خفيف، يتحمل أي صفحة، وما يطلعش أخطاء لو العناصر مش موجودة.

document.addEventListener("DOMContentLoaded", function () {
  // ------------------------------
  // 1) NAVBAR TOGGLE (ـ mobile menu)
  // ------------------------------
  (function setupNavToggle() {
    const toggle = document.querySelector(".nav-toggle"); // لو ضفت زرار في الـ layout
    const navLinks = document.querySelector(".nav-links");

    if (!toggle || !navLinks) return;

    toggle.addEventListener("click", function (e) {
      e.preventDefault();
      navLinks.classList.toggle("open");
      toggle.classList.toggle("open");
    });

    // on resize: لو الشاشة كبيرة نتأكد إن الكلاس اتشال
    window.addEventListener("resize", function () {
      if (window.innerWidth > 900) {
        navLinks.classList.remove("open");
        if (toggle) toggle.classList.remove("open");
      }
    });
  })();

  // ------------------------------
  // 2) SMOOTH SCROLL FOR ANCHOR LINKS (داخل الصفحة)
  // ------------------------------
  (function smoothScrollAnchors() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        const targetId = this.getAttribute("href").slice(1);
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
          e.preventDefault();
          targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });
  })();

  // ------------------------------
  // 3) IMAGE PREVIEW for file inputs (مثلاً في صفحة Sell Your Car)
  //    يتوقع عنصر <input id="image" type="file"> و<br> مكان عرض الصورة id="image_preview"
  // ------------------------------
  (function setupImagePreview() {
    const fileInput = document.getElementById("image");
    if (!fileInput) return;

    // تأكد إن في عنصر عرض، لو مش موجود نعمل واحد تحت الفورم
    let preview = document.getElementById("image_preview");
    if (!preview) {
      preview = document.createElement("div");
      preview.id = "image_preview";
      preview.style.marginTop = "12px";
      fileInput.parentNode.insertBefore(preview, fileInput.nextSibling);
    }

    fileInput.addEventListener("change", function () {
      preview.innerHTML = ""; // نمسح
      const file = this.files && this.files[0];
      if (!file) return;

      // تأكد من نوع ملف صورة
      if (!file.type.startsWith("image/")) {
        preview.textContent = "الملف المختار ليس صورة.";
        return;
      }

      const img = document.createElement("img");
      img.style.maxWidth = "100%";
      img.style.borderRadius = "8px";
      img.alt = "معاينة الصورة";

      const reader = new FileReader();
      reader.onload = function (e) {
        img.src = e.target.result;
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  })();

  // ------------------------------
  // 4) INSTALLMENT CALCULATOR (اختياري) —
  //    لو الصفحة فيها عناصر الحساب نشتغل عليها، وإلا نتجاهل.
  //    يتوقع:
  //      - عنصر يحتوي سعر السيارة: data-price attribute على عنصر .car-summary أو عنصر id="car_price"
  //      - مدخلات: #down_payment و #installment_period
  //      - مكان للنتيجة: #monthly_payment أو عنصر له id="installment_example"
  // ------------------------------
  (function setupInstallmentCalculator() {
    const downInput = document.getElementById("down_payment");
    const monthsSelect = document.getElementById("installment_period");
    const monthlyOutput = document.getElementById("monthly_payment");
    const exampleEl = document.getElementById("installment_example");

    if (!downInput && !monthsSelect) return; // لا حاجة للاستمرار لو مش في الصفحة

    // دالة مساعدة للحصول على السعر
    function getCarPrice() {
      // 1) جرب عنصر بعينه
      const priceEl = document.querySelector(".car-summary[data-price]") || document.getElementById("car_price");
      if (priceEl) {
        const p = priceEl.dataset ? priceEl.dataset.price : priceEl.getAttribute("data-price");
        if (p) return parseFloat(p);
      }
      // 2) حاول قراءة نص داخل .car-summary .price أو غيره
      const priceText = document.querySelector(".car-summary .price") || document.querySelector(".car-summary p.price");
      if (priceText) {
        // نحاول نفلتر أي رقم من النص
        const digits = priceText.textContent.replace(/[^0-9.]/g, "");
        if (digits) return parseFloat(digits);
      }
      // fallback
      return 25000;
    }

    function computeAndRender() {
      const price = getCarPrice();
      const down = parseFloat(downInput ? downInput.value : 0) || 0;
      const months = parseInt(monthsSelect ? monthsSelect.value : 0, 10) || 0;
      if (months > 0) {
        const monthly = (Math.max(0, price - down) / months).toFixed(2);
        if (monthlyOutput) monthlyOutput.value = `$${monthly}`;
        if (exampleEl) {
          exampleEl.textContent = `مثال: المتبقي بعد الدفعة الأولى $${(price - down).toFixed(2)}, التقسيط لمدة ${months} شهر تقريبًا $${monthly}/شهر.`;
        }
      } else {
        if (monthlyOutput) monthlyOutput.value = "";
        if (exampleEl) exampleEl.textContent = "";
      }
    }

    if (downInput) downInput.addEventListener("input", computeAndRender);
    if (monthsSelect) monthsSelect.addEventListener("change", computeAndRender);

    // حساب أولي لو القيم موجودة مسبقًا
    computeAndRender();
  })();

  // ------------------------------
  // 5) FORMS WITH DATA-CONFIRM (لو عايز اتصال تأكيد قبل الإرسال)
  //    في الـ HTML تقدر تضيف attribute: data-confirm="هل أنت متأكد؟"
  // ------------------------------
  (function setupFormConfirmations() {
    document.querySelectorAll("form[data-confirm]").forEach((form) => {
      form.addEventListener("submit", function (e) {
        const message = form.dataset.confirm || "هل أنت متأكد من الإرسال؟";
        if (!window.confirm(message)) {
          e.preventDefault();
        }
      });
    });
  })();

  // ------------------------------
  // 6) SET CURRENT YEAR AUTOMATICALLY (لو Footer محتاج)
  //    ضع <span class="current-year"></span> في ال footer او layout علشان يتعرض السنة الحالية
  // ------------------------------
  (function setCurrentYear() {
    const els = document.querySelectorAll(".current-year");
    if (!els.length) return;
    const y = new Date().getFullYear();
    els.forEach((el) => {
      el.textContent = y;
    });
  })();

  // ------------------------------
  // 7) UTILITY: delegate click for elements with data-action (extensible)
  //    مثال: <button data-action="scroll-top">Top</button>
  // ------------------------------
  (function setupDataActionDelegation() {
    document.addEventListener("click", function (e) {
      const btn = e.target.closest("[data-action]");
      if (!btn) return;
      const action = btn.getAttribute("data-action");

      if (action === "scroll-top") {
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
      // هنا ممكن تضيف أفعال تانية بسهولة
    });
  })();
});
