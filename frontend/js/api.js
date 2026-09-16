/* ============================================================
   api.js — Kararsız | Backend API İletişim Katmanı
   ============================================================ */

// Vercel'de çalışırken /api'ye, lokalde ise localhost:8000/api'ye gitsin
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://localhost:8000/api' 
  : '/api';
// ---------- Token Yönetimi ----------
const Auth = {
  getAccess:  () => localStorage.getItem('kararsiz_access'),
  getRefresh: () => localStorage.getItem('kararsiz_refresh'),
  getUser:    () => JSON.parse(localStorage.getItem('kararsiz_user') || 'null'),
  isLoggedIn: () => !!localStorage.getItem('kararsiz_access'),

  save(access, refresh, username) {
    localStorage.setItem('kararsiz_access',  access);
    localStorage.setItem('kararsiz_refresh', refresh);
    localStorage.setItem('kararsiz_user',    JSON.stringify({ username }));
  },

  clear() {
    localStorage.removeItem('kararsiz_access');
    localStorage.removeItem('kararsiz_refresh');
    localStorage.removeItem('kararsiz_user');
  },
};

// ---------- Anonim Oy Token ----------
function getVoterToken() {
  let token = localStorage.getItem('kararsiz_voter_token');
  if (!token) {
    token = crypto.randomUUID();
    localStorage.setItem('kararsiz_voter_token', token);
  }
  return token;
}

// ---------- Fetch Wrapper ----------
async function apiFetch(endpoint, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };

  if (Auth.isLoggedIn()) {
    headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  // 401 → token yenilemeyi dene
  if (res.status === 401 && Auth.getRefresh()) {
    const refreshed = await refreshToken();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
      return fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    } else {
      Auth.clear();
      window.location.href = '/frontend/login.html';
      return;
    }
  }

  return res;
}

async function refreshToken() {
  try {
    const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: Auth.getRefresh() }),
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('kararsiz_access', data.access);
      return true;
    }
    return false;
  } catch { return false; }
}

// ============================================================
// AUTH ENDPOİNTLERİ
// ============================================================
async function apiRegister(email, username, password) {
  const res = await apiFetch('/auth/register/', {
    method: 'POST',
    body: JSON.stringify({ email, username, password }),
  });
  const data = await res.json();
  if (res.ok) {
    // Token dönmez, hesap henüz inaktif
    return { ok: true, data };
  }
  return { ok: false, errors: data };
}

async function apiVerifyEmail(uid, token) {
  const res = await apiFetch('/auth/verify-email/', {
    method: 'POST',
    body: JSON.stringify({ uid, token }),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

async function apiPasswordResetRequest(email) {
  const res = await apiFetch('/auth/password-reset/', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

async function apiPasswordResetConfirm(uid, token, new_password) {
  const res = await apiFetch('/auth/password-reset-confirm/', {
    method: 'POST',
    body: JSON.stringify({ uid, token, new_password }),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

async function apiLogin(email, password) {
  const res = await apiFetch('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (res.ok) {
    Auth.save(data.access, data.refresh, data.username);
    return { ok: true, data };
  }
  return { ok: false, errors: data };
}

async function apiLogout() {
  const refresh = Auth.getRefresh();
  if (refresh) {
    await apiFetch('/auth/logout/', {
      method: 'POST',
      body: JSON.stringify({ refresh }),
    });
  }
  Auth.clear();
}

async function apiGetMe() {
  const res = await apiFetch('/auth/me/');
  if (!res || !res.ok) return { ok: false, data: null };
  return { ok: true, data: await res.json() };
}

// ============================================================
// POLL ENDPOİNTLERİ
// ============================================================
async function apiGetPolls(category = 'all', sort = 'newest') {
  const res = await apiFetch(`/polls/?category=${category}&sort=${sort}`);
  if (!res || !res.ok) return { ok: false, data: [] };
  return { ok: true, data: await res.json() };
}

async function apiGetPoll(id) {
  const res = await apiFetch(`/polls/${id}/`);
  if (!res || !res.ok) return { ok: false, data: null };
  return { ok: true, data: await res.json() };
}

async function apiCreatePoll(question, category, options) {
  const res = await apiFetch('/polls/', {
    method: 'POST',
    body: JSON.stringify({ question, category, options }),
  });
  const data = await res.json();
  return { ok: res.ok, data, status: res.status };
}

async function apiVote(pollId, optionId) {
  const body = Auth.isLoggedIn()
    ? { option_id: optionId }
    : { option_id: optionId, voter_token: getVoterToken() };

  const res = await apiFetch(`/polls/${pollId}/vote/`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  const data = await res.json();
  return { ok: res.ok, data, status: res.status };
}

async function apiDeletePoll(pollId) {
  const res = await apiFetch(`/polls/${pollId}/`, {
    method: 'DELETE',
  });
  if (res && res.status === 204) {
    return { ok: true };
  }
  return { ok: false, status: res ? res.status : null };
}
