# Kararsız 🤔

[![Vercel](https://img.shields.io/badge/Vercel-Canlı_Demo-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://kararsizim-kappa.vercel.app/)


> Karar veremeyenler için anket platformu. Günlük hayattaki "ne yapalım?" sorularını ankete dönüştür, herkesin oyunu al.

---

## ✨ Özellikler

- **Herkese açık oy kullanımı** — Üyelik olmadan da oy verilebilir
- **Anket oluşturma** — Kayıtlı kullanıcılar 2-5 seçenekli anket açabilir
- **Canlı oy oranları** — Progress bar ile anlık sonuçlar
- **Mükerrer oy engeli** — Token + IP kombinasyonu ile korumalı
- **Açık / Karanlık tema** — Sistem tercihi ile otomatik, localStorage'da saklı
- **Mobil uyumlu** — Responsive tasarım

---

## 🛠️ Teknoloji Yığını

| Katman     | Teknoloji                                       |
| ---------- | ----------------------------------------------- |
| Backend    | Python + Django + Django REST Framework         |
| Auth       | JWT (djangorestframework-simplejwt)             |
| Veritabanı | Supabase (PostgreSQL)                           |
| Frontend   | Vanilla HTML / CSS / JavaScript                 |
| Deployment | Vercel (frontend) + Vercel Serverless (backend) |

---

## 📁 Klasör Yapısı

```
Kararsizim/
├── backend/
│   ├── kararsiz_backend/    # Django proje ayarları
│   ├── users/               # Kullanıcı & auth app
│   ├── polls/               # Anket app
│   ├── requirements.txt
│   └── .env.example         # Ortam değişkeni şablonu
├── frontend/
│   ├── index.html           # Anket akışı
│   ├── poll-detail.html     # Tek anket + oy verme
│   ├── create-poll.html     # Anket oluşturma
│   ├── login.html
│   ├── register.html
│   ├── css/
│   │   ├── style.css
│   │   └── theme.css
│   └── js/
│       ├── api.js
│       ├── auth.js
│       ├── main.js
│       └── theme-toggle.js
└──
```

---

## 🚀 Yerel Kurulum

### Backend

```bash
cd backend

# Sanal ortam oluştur
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS/Linux

# Bağımlılıkları yükle
pip install -r requirements.txt

# Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle (DB şifresi vs.)

# Veritabanını hazırla
python manage.py migrate

# Sunucuyu başlat
python manage.py runserver
```

### Frontend

Frontend saf HTML/CSS/JS — ekstra kurulum gerekmez.

```bash
# Seçenek 1: Tarayıcıda direkt aç
# frontend/index.html dosyasına çift tıkla

# Seçenek 2: Python ile basit sunucu
python -m http.server 5500 --directory frontend
# → http://localhost:5500
```

> ⚠️ Backend `localhost:8000`'de çalışırken frontend'i aç.

---

## ⚙️ Ortam Değişkenleri

`backend/.env.example` dosyasını `backend/.env` olarak kopyala ve doldur:

```env
SECRET_KEY=django-secret-key-buraya
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=postgres
DB_USER=postgres.PROJE_REF
DB_PASSWORD=supabase-db-sifresi
DB_HOST=aws-0-eu-central-1.pooler.supabase.com
DB_POOLER_PORT=6543

SUPABASE_URL=https://PROJE_REF.supabase.co
SUPABASE_ANON_KEY=anon-key-buraya

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:5500
```

---

## 🔐 Güvenlik Notları

- `email` alanı **hiçbir API yanıtında** dönülmez — sadece `username` görünür
- Parolalar Django'nun varsayılan hash mekanizmasıyla saklanır
- `.env` dosyası `.gitignore`'a eklidir, repoya **gitmez**
- CORS production'da yalnızca Vercel domain'ine izin verir

---

## 📋 API Endpoint'leri

| Method | Endpoint                | Açıklama      | Auth |
| ------ | ----------------------- | ------------- | ---- |
| POST   | `/api/auth/register/`   | Kayıt ol      | —    |
| POST   | `/api/auth/login/`      | Giriş yap     | —    |
| POST   | `/api/auth/logout/`     | Çıkış yap     | ✅   |
| GET    | `/api/polls/`           | Tüm anketler  | —    |
| POST   | `/api/polls/`           | Anket oluştur | ✅   |
| GET    | `/api/polls/<id>/`      | Anket detayı  | —    |
| POST   | `/api/polls/<id>/vote/` | Oy ver        | —    |

---

## 📌 Geliştirme Yol Haritası

- [x] Faz 1 — Backend temel yapı (Django + Supabase + Auth)
- [x] Faz 2 — Anket backend (Poll, Vote endpoint'leri)
- [x] Faz 3 — Frontend sayfalar
- [x] Faz 4 — Tema sistemi (açık/karanlık)
- [ ] Faz 5 — Vercel deployment

---

## 👤 Geliştirici

**Ahmet Akaslan** — [@ahmetakaslan1](https://github.com/ahmetakaslan1)
