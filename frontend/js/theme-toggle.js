/* ============================================================
   theme-toggle.js — Kararsız | Tema Yönetimi
   ============================================================ */

const THEME_KEY = 'kararsiz_theme';

function getSystemTheme() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);

  // İkon güncelle
  const toggles = document.querySelectorAll('.theme-toggle');
  toggles.forEach(btn => {
    btn.textContent = theme === 'dark' ? '☀️' : '🌙';
    btn.title = theme === 'dark' ? 'Açık temaya geç' : 'Karanlık temaya geç';
  });
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) || getSystemTheme();
  applyTheme(saved);
}

// DOM hazır olduğunda
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.addEventListener('click', toggleTheme);
  });
});
