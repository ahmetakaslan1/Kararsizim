/* ============================================================
   main.js — Kararsız | Ana Feed Sayfası Mantığı
   ============================================================ */

document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  updateNavbar();
  await loadPolls();
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
    <div class="poll-meta">
      <div class="poll-meta-avatar" aria-hidden="true">${avatarLetter(creator)}</div>
      <span>@${creator}</span>
      <span>·</span>
      <span>${timeAgo(poll.created_at)}</span>
      <span class="poll-total-votes">🗳️ ${total} oy</span>
    </div>
  `;

  // Tıklama — detay sayfasına git
  const navigate = () => { window.location.href = `poll-detail.html?id=${poll.id}`; };
  card.addEventListener('click', navigate);
  card.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') navigate(); });

  return card;
}

// ---------- Anketleri yükle ----------
async function loadPolls() {
  const grid = document.getElementById('polls-grid');
  const emptyState = document.getElementById('empty-state');

  renderSkeletons(5);

  const { ok, data } = await apiGetPolls();

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
