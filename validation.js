// static/js/validation.js
// سكربت مسؤول عن التحقق من بيانات النماذج (forms) في الموقع

document.addEventListener("DOMContentLoaded", function () {

  // دالة عامة للتحقق من البريد الإلكتروني
  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  // دالة عامة للتحقق من رقم الموبايل (أرقام فقط وطوله 10-15 رقم)
  function isValidPhone(phone) {
    return /^[0-9]{10,15}$/.test(phone);
  }

  // دالة مساعدة لإظهار رسالة خطأ
  function showError(input, message) {
    let error = input.parentNode.querySelector(".error-message");
    if (!error) {
      error = document.createElement("div");
      error.classList.add("error-message");
      error.style.color = "red";
      error.style.fontSize = "0.9em";
      error.style.marginTop = "4px";
      input.parentNode.appendChild(error);
    }
    error.textContent = message;
    input.classList.add("input-error");
  }

  // دالة لإزالة رسالة الخطأ
  function clearError(input) {
    input.classList.remove("input-error");
    const error = input.parentNode.querySelector(".error-message");
    if (error) error.remove();
  }

  // التحقق من نموذج التسجيل (registration.html)
  const registrationForm = document.querySelector("#registration_form");
  if (registrationForm) {
    registrationForm.addEventListener("submit", function (e) {
      let valid = true;
      const name = registrationForm.querySelector("#name");
      const email = registrationForm.querySelector("#email");
      const password = registrationForm.querySelector("#password");
      const confirm = registrationForm.querySelector("#confirm_password");

      // الاسم
      if (name && name.value.trim().length < 3) {
        showError(name, "الاسم يجب أن يحتوي على 3 أحرف على الأقل");
        valid = false;
      } else if (name) clearError(name);

      // البريد
      if (email && !isValidEmail(email.value.trim())) {
        showError(email, "من فضلك أدخل بريد إلكتروني صحيح");
        valid = false;
      } else if (email) clearError(email);

      // الباسورد
      if (password && password.value.length < 6) {
        showError(password, "كلمة المرور يجب أن تكون 6 أحرف على الأقل");
        valid = false;
      } else if (password) clearError(password);

      // تأكيد الباسورد
      if (confirm && confirm.value !== password.value) {
        showError(confirm, "كلمة المرور غير متطابقة");
        valid = false;
      } else if (confirm) clearError(confirm);

      if (!valid) e.preventDefault();
    });
  }

  // التحقق من نموذج تسجيل الدخول (login.html)
  const loginForm = document.querySelector("#login_form");
  if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
      let valid = true;
      const email = loginForm.querySelector("#email");
      const password = loginForm.querySelector("#password");

      if (email && !isValidEmail(email.value.trim())) {
        showError(email, "البريد الإلكتروني غير صالح");
        valid = false;
      } else if (email) clearError(email);

      if (password && password.value.length < 6) {
        showError(password, "كلمة المرور قصيرة جدًا");
        valid = false;
      } else if (password) clearError(password);

      if (!valid) e.preventDefault();
    });
  }

  // التحقق من نموذج بيع العربية (sell_your_car.html)
  const sellForm = document.querySelector("#sell_car_form");
  if (sellForm) {
    sellForm.addEventListener("submit", function (e) {
      let valid = true;
      const name = sellForm.querySelector("#owner_name");
      const phone = sellForm.querySelector("#phone");
      const price = sellForm.querySelector("#price");

      if (name && name.value.trim().length < 3) {
        showError(name, "الاسم قصير جدًا");
        valid = false;
      } else if (name) clearError(name);

      if (phone && !isValidPhone(phone.value.trim())) {
        showError(phone, "أدخل رقم موبايل صحيح");
        valid = false;
      } else if (phone) clearError(phone);

      if (price && (isNaN(price.value) || Number(price.value) <= 0)) {
        showError(price, "أدخل سعر صالح");
        valid = false;
      } else if (price) clearError(price);

      if (!valid) e.preventDefault();
    });
  }

  // التحقق من نموذج الصيانة (service_maintenance.html)
  const serviceForm = document.querySelector("#service_form");
  if (serviceForm) {
    serviceForm.addEventListener("submit", function (e) {
      let valid = true;
      const name = serviceForm.querySelector("#customer_name");
      const phone = serviceForm.querySelector("#phone");
      const car = serviceForm.querySelector("#car_model");

      if (name && name.value.trim().length < 3) {
        showError(name, "الاسم غير صالح");
        valid = false;
      } else if (name) clearError(name);

      if (phone && !isValidPhone(phone.value.trim())) {
        showError(phone, "أدخل رقم موبايل صحيح");
        valid = false;
      } else if (phone) clearError(phone);

      if (car && car.value.trim() === "") {
        showError(car, "من فضلك اختر موديل السيارة");
        valid = false;
      } else if (car) clearError(car);

      if (!valid) e.preventDefault();
    });
  }

});
