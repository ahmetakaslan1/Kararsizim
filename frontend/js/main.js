/* ============================================================
   main.js — Kararsız | Ana Feed Sayfası Mantığı
   ============================================================ */

let currentCategory = 'all';
let currentSort = 'newest';

document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  updateNavbar();

  // Filtreleme ve Sıralama Event Listener'ları
  const sortTabs = document.querySelectorAll('.sort-tab');
  sortTabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      sortTabs.forEach(t => {
        t.classList.remove('active');
        t.style.backgroundColor = 'transparent';
        t.style.borderColor = 'transparent';
        t.style.opacity = '0.7';
      });
      const target = e.currentTarget;
      target.classList.add('active');
      target.style.backgroundColor = 'var(--surface-light)';
      target.style.borderColor = 'var(--border)';
      target.style.opacity = '1';
      
      currentSort = target.dataset.sort;
      loadPolls(currentCategory, currentSort);
    });
  });

  const catSelect = document.getElementById('category-select');
  if(catSelect) {
    catSelect.addEventListener('change', (e) => {
      currentCategory = e.target.value;
      loadPolls(currentCategory, currentSort);
    });
  }

  await loadPolls(currentCategory, currentSort);
});

// ---------- Skeleton yükleyici ----------
function renderSkeletons(count = 4) {
  const grid = document.getElementById('polls-grid');
  grid.innerHTML = Array(count).fill('')
    .map(() => `<div class="skeleton skeleton-card"></div>`)
    .join('');
}

// ---------- Anket kartı oluştur ----------
function buildPollCard(poll) {
  const total = poll.total_votes || 0;
  const creator = poll.creator?.username || 'anonim';

  const optionsHtml = poll.options.map(opt => {
    const pct = calcPercent(opt.vote_count, total);
    const label = opt.text.length > 20 ? opt.text.slice(0, 18) + '…' : opt.text;
    return `
      <div class="vote-bar-wrap">
        <span class="vote-bar-label" title="${opt.text}">${label}</span>
        <div class="vote-bar-track">
          <div class="vote-bar-fill" style="width:0%" data-target="${pct}"></div>
        </div>
        <span class="vote-bar-pct">${pct}%</span>
      </div>
    `;
  }).join('');

  const card = document.createElement('article');
  card.className = 'poll-card';
  card.dataset.pollId = poll.id;
  card.setAttribute('role', 'button');
  card.setAttribute('tabindex', '0');
  card.setAttribute('aria-label', poll.question);
  card.innerHTML = `
    <div class="poll-card-header">
      <p class="poll-question">${poll.question}</p>
    </div>
    <div class="poll-options-preview">${optionsHtml}</div>
    <div class="poll-meta" style="flex-wrap: wrap;">
      <div class="poll-meta-avatar" aria-hidden="true">${avatarLetter(creator)}</div>
      <span>@${creator}</span>
      <span>·</span>
      <span>${timeAgo(poll.created_at)}</span>
      <span class="poll-total-votes">🗳️ ${total} oy</span>
      ${poll.category && poll.category !== 'genel' ? `<span style="background: var(--primary); color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-left: auto;">#${poll.category.toUpperCase()}</span>` : ''}
    </div>
  `;

  // Tıklama — detay sayfasına git
  const navigate = () => { window.location.href = `poll-detail.html?id=${poll.id}`; };
  card.addEventListener('click', navigate);
  card.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') navigate(); });

  return card;
}

// ---------- Anketleri yükle ----------
async function loadPolls(category = 'all', sort = 'newest') {
  const grid = document.getElementById('polls-grid');
  const emptyState = document.getElementById('empty-state');

  renderSkeletons(5);

  const { ok, data } = await apiGetPolls(category, sort);

  grid.innerHTML = '';

  if (!ok || data.length === 0) {
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';
  const fragment = document.createDocumentFragment();

  data.forEach(poll => {
    fragment.appendChild(buildPollCard(poll));
  });

  grid.appendChild(fragment);

  // Bar animasyonlarını başlat (sayfa render'dan sonra)
  requestAnimationFrame(() => {
    document.querySelectorAll('.vote-bar-fill').forEach(bar => {
      const target = bar.dataset.target;
      setTimeout(() => { bar.style.width = target + '%'; }, 100);
    });
  });
}
