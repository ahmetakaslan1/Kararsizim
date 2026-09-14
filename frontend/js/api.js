/* ============================================================
   api.js — Kararsız | Backend API İletişim Katmanı
   ============================================================ */

const API_BASE = 'http://localhost:8000/api';

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
    Auth.save(data.access, data.refresh, data.username);
    return { ok: true, data };
  }
  return { ok: false, errors: data };
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

// ============================================================
// POLL ENDPOİNTLERİ
// ============================================================
async function apiGetPolls() {
  const res = await apiFetch('/polls/');
  if (!res || !res.ok) return { ok: false, data: [] };
  return { ok: true, data: await res.json() };
}

async function apiGetPoll(id) {
  const res = await apiFetch(`/polls/${id}/`);
  if (!res || !res.ok) return { ok: false, data: null };
  return { ok: true, data: await res.json() };
}

async function apiCreatePoll(question, options) {
  const res = await apiFetch('/polls/', {
    method: 'POST',
    body: JSON.stringify({ question, options }),
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
