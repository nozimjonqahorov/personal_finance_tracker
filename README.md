# 💰 Personal Finance Tracker

> Django asosida qurilgan shaxsiy moliya boshqaruv tizimi — daromad, xarajat va hisoblarni bir joyda kuzatib boring.

---

## 📋 Mundarija

- [Asosiy Imkoniyatlar](#-asosiy-imkoniyatlar)
- [Texnologik Stek](#-texnologik-stek)
- [Ma'lumotlar Bazasi Strukturasi](#-malumotlar-bazasi-strukturasi)
- [O'rnatish](#-ornatish)
- [Konfiguratsiya](#-konfiguratsiya)
- [URL Manzillari](#-url-manzillari)
- [Loyiha Tuzilmasi](#-loyiha-tuzilmasi)

---

## ✨ Asosiy Imkoniyatlar

### 👤 Foydalanuvchilar Boshqaruvi
- Xavfsiz ro'yxatdan o'tish, tizimga kirish va chiqish
- Shaxsiy profil va foydalanuvchi ma'lumotlarini tahrirlash
- Parolni SMTP Email orqali tiklash

### 💳 Hisoblar va O'tkazmalar
- Ko'p sonli moliyaviy hisoblar yaratish (karta, naqd pul, hamyon)
- Bank kartasi formatini avtomatik validatsiya (`django-credit-cards`)
- Hisoblar o'rtasida pul o'tkazmalari va ularning tarixi

### 📊 Tranzaksiyalar va Analitika
- Daromad/xarajatlarni toifalar bo'yicha kiritish
- Kuchli filtrlash (`django-filter`) va sahifalash (Pagination)
- **PDF hisobot** yuklab olish (`WeasyPrint`)
- Markaziy Dashboard: umumiy balans, oylik statistika va valyuta konvertatsiyasi

---

## 🛠 Texnologik Stek

| Soha        | Texnologiya                          |
|-------------|--------------------------------------|
| Backend     | Python 3.11+ / Django 5.x            |
| Database    | SQLite3                              |
| Frontend    | HTML5, CSS3, Bootstrap               |
| PDF         | WeasyPrint                           |
| Email       | SMTP (Gmail)                         |
| Kutubxonalar | `django-filter`, `pillow`, `python-dotenv`, `django-credit-cards` |

---

## 🗂 Ma'lumotlar Bazasi Strukturasi

```
[User] ──(1:N)──> [Account]
  │                   │
  │ (1:N)             │ (1:N)
  ▼                   ▼
[Category] ──(1:N)──> [Transaction]
```

---

### 💻 O'rnatish 

### 1. Repozitoriyani yuklab oling

```bash
git clone https://github.com/nozimjonqahorov/personal_finance_tracker
cd personal_finance_tracker
```

### 2. Virtual muhit yarating va aktivlashtiring

```bash
# Yaratish
python -m venv .venv

# Aktivlashtirish — Windows
.venv\Scripts\activate

# Aktivlashtirish — Linux / macOS
source .venv/bin/activate
```

### 3. Kerakli paketlarni o'rnating

```bash
pip install -r requirements.txt
```

### 4. `.env` faylini sozlang

Quyidagi bo'limga qarang: [Konfiguratsiya](#-konfiguratsiya)

### 5. Ma'lumotlar bazasini tayyorlang

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Serverni ishga tushiring

```bash
python manage.py runserver
```

Brauzerda oching: **http://127.0.0.1:8000/**

---

## ⚙️ Konfiguratsiya

Loyiha ildiz katalogida `.env` nomli fayl yarating va quyidagi ma'lumotlarni kiriting.

> **Namuna faylidan ko'chirish:**
> ```bash
> cp .env.example .env
> ```
> Keyin `.env` ichidagi qiymatlarni o'zingiznikiga almashtiring.

### `.env` namunasi (`.env.example`)

```env
# Django asosiy sozlamalar
SECRET_KEY=your-very-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Vaqt zonasi
TIME_ZONE=Asia/Tashkent
SITE_ID=1

# Email sozlamalari (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=Finance Track <your-email@gmail.com>
```

> **💡 Gmail App Password olish:** Google Account → Security → 2-Step Verification → App Passwords

---

## 🔗 URL Manzillari

| Ilova          | Sahifa                   | URL                             |
|----------------|--------------------------|---------------------------------|
| **Shared**     | Bosh sahifa              | `/`                             |
|                | Dashboard                | `/dashboard/`                   |
| **Users**      | Ro'yxatdan o'tish        | `/users/signup/`                |
|                | Tizimga kirish           | `/users/login/`                 |
|                | Tizimdan chiqish         | `/users/logout/`                |
|                | Shaxsiy profil           | `/users/profile/`               |
|                | Profilni yangilash        | `/users/profile-update/`        |
|                | Parolni o'zgartirish     | `/users/change-password/`       |
|                | Parolni tiklash          | `/users/password-reset/`        |
| **Accounts**   | Hisoblar ro'yxati        | `/accounts/hisoblar/`           |
|                | Yangi hisob yaratish     | `/accounts/hisob-yaratish/`     |
|                | Hisob tafsilotlari       | `/accounts/hisob-detal/<id>/`   |
|                | Hisobni tahrirlash       | `/accounts/hisob-tahrir/<id>/`  |
|                | Hisobni o'chirish        | `/accounts/hisob-uchirish/<id>/`|
|                | Pul o'tkazmasi           | `/accounts/make-transfer/`      |
|                | O'tkazmalar tarixi       | `/accounts/transfer-list/`      |
| **Transactions**| Tranzaksiyalar monitori  | `/transactions/`                |
|                | Kategoriya qo'shish      | `/transactions/category/add/`   |

---

## 📂 Loyiha Tuzilmasi

```
personal_finance_tracker/
├── accounts/           # Hisoblar va o'tkazmalar ilovasi
├── transactions/       # Daromad/xarajat va kategoriyalar ilovasi
├── users/              # Foydalanuvchi autentifikatsiyasi va profili
├── shared/             # Dashboard va umumiy sahifalar
├── config/             # Loyiha konfiguratsiyasi (settings, urls, wsgi)
├── static/             # Statik fayllar (CSS, JS)
├── media/              # Yuklanadigan media fayllar
├── templates/          # HTML shablonlar
├── db.sqlite3          # SQLite ma'lumotlar bazasi
├── manage.py
├── requirements.txt
├── .env                # ⚠️ Maxfiy — git'ga qo'shilmaydi
└── .env.example        # Namuna konfiguratsiya fayli
```

---

## 🔒 Xavfsizlik

- `.env` fayli git'ga commit qilinmasin — `.gitignore`'da mavjud ✅
- `.env.example` faylida haqiqiy ma'lumot bo'lmasin ✅
- `DEBUG=False` holida ishga tushiring (production'da)
- Gmail uchun **App Password** ishlating, asosiy parolni emas
- `SECRET_KEY`ni hech kim bilan ulashmang

---

## 📄 Litsenziya

Bu loyiha o'quv maqsadlarida yaratilgan.
