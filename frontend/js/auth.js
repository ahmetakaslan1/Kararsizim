/* ============================================================
   auth.js — Kararsız | Auth UI Yardımcıları
   ============================================================ */

// Navbar'ı auth durumuna göre güncelle
function updateNavbar() {
  const user = Auth.getUser();
  const navAuth = document.getElementById('nav-auth');
  if (!navAuth) return;

  if (user) {
    navAuth.innerHTML = `
      <a href="profile.html" style="font-size:0.85rem;color:var(--text-secondary);font-weight:600; text-decoration:none; margin-right: 0.5rem;" title="Profilime Git">
        👋 ${user.username}
      </a>
      <a href="create-poll.html" class="btn btn-primary btn-sm" id="nav-create-btn">
        + Anket Oluştur
      </a>
      <button class="btn btn-ghost btn-sm" id="nav-logout-btn">Çıkış</button>
    `;
    document.getElementById('nav-logout-btn').addEventListener('click', async () => {
      await apiLogout();
      window.location.reload();
    });
  } else {
    navAuth.innerHTML = `
      <a href="login.html" class="btn btn-ghost btn-sm">Giriş Yap</a>
      <a href="register.html" class="btn btn-primary btn-sm">Kayıt Ol</a>
    `;
  }
}

// Toast bildirimi
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  toast.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'toast-out 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Form hata gösterimi
function showFormError(inputId, message) {
  const input = document.getElementById(inputId);
  const errEl = document.getElementById(`${inputId}-error`);
  if (input) input.style.borderColor = 'var(--danger)';
  if (errEl) { errEl.textContent = message; errEl.classList.add('visible'); }
}

function clearFormErrors(formId) {
  const form = document.getElementById(formId);
  if (!form) return;
  form.querySelectorAll('.form-input, .form-textarea').forEach(el => {
    el.style.borderColor = '';
  });
  form.querySelectorAll('.form-error').forEach(el => {
    el.textContent = '';
    el.classList.remove('visible');
  });
}

// Yüzde hesapla
function calcPercent(count, total) {
  if (!total) return 0;
  return Math.round((count / total) * 100);
}

// Göreli zaman
function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const min  = Math.floor(diff / 60000);
  const hr   = Math.floor(diff / 3600000);
  const day  = Math.floor(diff / 86400000);
  if (min < 1)   return 'az önce';
  if (min < 60)  return `${min} dk önce`;
  if (hr < 24)   return `${hr} saat önce`;
  if (day < 30)  return `${day} gün önce`;
  return new Date(dateStr).toLocaleDateString('tr-TR');
}

// İlk harf avatar
function avatarLetter(username) {
  return (username || '?')[0].toUpperCase();
}

// Oy verildi mi kontrol (localStorage)
function hasVoted(pollId) {
  const voted = JSON.parse(localStorage.getItem('kararsiz_voted') || '{}');
  return voted[pollId] || null;
}

function markVoted(pollId, optionId) {
  const voted = JSON.parse(localStorage.getItem('kararsiz_voted') || '{}');
  voted[pollId] = optionId;
  localStorage.setItem('kararsiz_voted', JSON.stringify(voted));
}
