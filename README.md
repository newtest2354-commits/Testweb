<div align="center">

<img src="assets/logo/readme.png" alt="Arista DNS Hub" width="220">

# 🌐 Arista DNS Hub

### سامانه جمع‌آوری، استخراج، تحلیل و نمایش DNS

<p>
جمع‌آوری DNSهای عمومی از منابع مختلف، استخراج اطلاعات، تحلیل، دسته‌بندی،
حذف موارد تکراری و انتشار خودکار در یک رابط وب سریع و ساده.
</p>

<br>

<a href="https://t.me/aristapanel">
<img src="https://img.shields.io/badge/Telegram-229ED9?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
</a>

<a href="https://github.com/aristapanell-cell/AriataPanel">
<img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
</a>

<a href="https://aristapanell-cell.github.io/AristaDns/">
<img src="https://img.shields.io/badge/GitHub%20Pages-222222?style=for-the-badge&logo=githubpages&logoColor=white" alt="GitHub Pages">
</a>

<a href="https://aristadns.arista-panel.workers.dev/">
<img src="https://img.shields.io/badge/Cloudflare%20Workers-F38020?style=for-the-badge&logo=cloudflare&logoColor=white" alt="Cloudflare Workers">
</a>

<br><br>

<img src="https://img.shields.io/badge/Status-Active-00C853?style=flat-square" alt="Status">
<img src="https://img.shields.io/badge/DNS-DoH%20%7C%20DoT-4285F4?style=flat-square" alt="DNS">
<img src="https://img.shields.io/badge/IPv4-Supported-2196F3?style=flat-square" alt="IPv4">
<img src="https://img.shields.io/badge/IPv6-Supported-673AB7?style=flat-square" alt="IPv6">

</div>

---

## 📖 درباره پروژه

**Arista DNS Hub** یک پروژه متن‌باز برای جمع‌آوری، استخراج، تحلیل و مدیریت DNSهای عمومی از منابع مختلف است.

هدف پروژه ایجاد یک بانک اطلاعاتی پویا از DNSهاست؛ به‌گونه‌ای که اطلاعات DNS از منابع عمومی جمع‌آوری شده، بدون تغییر در ساختار اصلی استخراج، بررسی و دسته‌بندی شوند و در نهایت از طریق یک رابط وب در اختیار کاربران قرار بگیرند.

فرآیند کلی پروژه:

**جمع‌آوری → استخراج → تحلیل → اعتبارسنجی → دسته‌بندی → حذف موارد تکراری → تولید آمار → انتشار**

---

## ✨ قابلیت‌ها

- 🔎 جمع‌آوری DNS از منابع عمومی
- 🧩 استخراج DNS از ساختارهای مختلف صفحات وب
- 🌐 پشتیبانی از DNS over HTTPS
- 🔐 پشتیبانی از DNS over TLS
- 4️⃣ پشتیبانی از IPv4
- 6️⃣ پشتیبانی از IPv6
- 🔢 پشتیبانی از DNSهای دارای پورت
- 🌍 پشتیبانی از DNSهای بدون پورت
- 🏷️ دسته‌بندی DNSها
- ♻️ شناسایی و حذف موارد تکراری
- 🧠 تحلیل اطلاعات استخراج‌شده
- 🧪 اعتبارسنجی داده‌ها
- 📊 تولید آمار
- 🔄 بروزرسانی خودکار
- 🔍 جست‌وجوی DNS
- 🎛️ فیلتر بر اساس دسته و پروتکل
- 📋 کپی سریع DNS
- 🌐 انتشار روی GitHub Pages
- ⚡ انتشار روی Cloudflare Workers

---

## 📡 استخراج DNS

استخراج‌کننده برای شناسایی DNSهایی با ساختارهای مختلف طراحی شده است.

نمونه‌های قابل استخراج:

    example.com

    example.com:853

    tls://example.com

    tls://example.com:853

    https://example.com/dns-query

    https://example.com/resolve

DNS ممکن است در جدول، لینک، متن، `article`، `section`، `li`، `div`، `pre`، `code` یا سایر ساختارهای HTML قرار داشته باشد.

سیستم تلاش می‌کند DNS موجود در منبع را شناسایی و استخراج کند.

---

## 🔐 DNS over TLS

Arista DNS Hub قابلیت شناسایی و استخراج DNSهای **DoT** را دارد.

نمونه:

    tls://dns.example.com

یا:

    tls://dns.example.com:853

همچنین Endpointهایی که بدون پیشوند `tls://` در منابع معرفی شده‌اند نیز قابل شناسایی هستند.

---

## 🌐 DNS over HTTPS

DNSهای **DoH** نیز از منابع استخراج می‌شوند.

نمونه:

    https://dns.example.com/dns-query

    https://dns.example.com/resolve

    https://dns.example.com/doh

اطلاعات مربوط به URL، Hostname و Path در داده استخراج‌شده نگهداری می‌شود.

---

## 🧬 حفظ اطلاعات استخراج‌شده

یکی از اصول اصلی پروژه این است که **استخراج‌کننده نباید فرمت DNS موجود در منبع را تغییر دهد.**

اگر منبع DNS را بدون پورت ارائه کند:

    dns.example.com

هیچ پورتی به آن اضافه نمی‌شود.

اگر منبع DNS را همراه پورت ارائه کند:

    dns.example.com:853

پورت حفظ می‌شود.

اگر منبع از ساختار زیر استفاده کند:

    tls://dns.example.com:853

همان ساختار حفظ می‌شود.

اگر URL دارای مسیر باشد:

    https://dns.example.com/custom-query

مسیر نیز حفظ می‌شود.

### اصل مهم پروژه

> **استخراج انجام می‌شود، نه بازنویسی DNS.**

سیستم نباید برای استانداردسازی یا تغییر رفتار:

- پورت اضافه کند
- پورت حذف کند
- لینک را کوتاه کند
- مسیر URL را تغییر دهد
- پروتکل را تغییر دهد
- Endpoint را بازسازی کند
- فرمت اصلی DNS را تغییر دهد

**داده منبع، مرجع اصلی است.**

تحلیل و نرمال‌سازی فقط در بخش‌هایی که برای شناسایی، دسته‌بندی و تشخیص موارد تکراری لازم است انجام می‌شود و نباید باعث تغییر مقدار اصلی استخراج‌شده شود.

---

## 🧠 تحلیل DNS

پس از استخراج، اطلاعات DNS برای شناسایی مشخصات آن بررسی می‌شود.

موارد قابل تحلیل شامل:

- Provider
- Hostname
- Address
- Protocol
- Type
- Port
- Path
- Category
- Source
- IPv4 / IPv6

---

## 🏷️ دسته‌بندی DNSها

DNSها بر اساس اطلاعات موجود در منابع می‌توانند در دسته‌های مختلف قرار بگیرند.

دسته‌ها:

- Standard
- AdBlock
- Family
- Security
- Malware
- Adult Filter
- Unfiltered
- FreeShekan
- Private

پروتکل‌ها:

- DoH
- DoT
- DNSCrypt

نوع آدرس:

- IPv4
- IPv6

---

## ♻️ حذف موارد تکراری

ممکن است یک DNS در چند منبع مختلف وجود داشته باشد.

سیستم پس از استخراج، رکوردها را بررسی کرده و موارد تکراری را شناسایی می‌کند تا یک DNS چندین بار در خروجی نهایی ثبت نشود.

روند کلی:

    منابع عمومی
         │
         ▼
      استخراج
         │
         ▼
       تحلیل
         │
         ▼
    اعتبارسنجی
         │
         ▼
   تشخیص تکراری
         │
         ▼
     داده نهایی

---

## 🧪 تست و اعتبارسنجی

اطلاعات استخراج‌شده بررسی می‌شوند تا داده‌های نامعتبر یا خراب وارد خروجی نهایی نشوند.

بررسی‌ها می‌توانند شامل موارد زیر باشند:

- ساختار URL
- Hostname
- IPv4
- IPv6
- Protocol
- Endpoint
- ساختار DoH
- ساختار DoT
- داده‌های نامعتبر
- موارد تکراری

---

## 📊 آمار

Arista DNS Hub برای داده‌های نهایی آمار تولید می‌کند.

| مورد | توضیح |
|---|---|
| Total | تعداد کل DNSها |
| IPv4 | تعداد DNSهای IPv4 |
| IPv6 | تعداد DNSهای IPv6 |
| DoH | تعداد DNSهای DoH |
| DoT | تعداد DNSهای DoT |
| AdBlock | تعداد DNSهای AdBlock |
| Family | تعداد DNSهای Family |
| Security | تعداد DNSهای Security |

---

## 🔎 جست‌وجو

رابط وب دارای جست‌وجوی داخلی است.

امکان جست‌وجو بر اساس اطلاعات مختلف از جمله:

- DNS
- Provider
- Name
- Hostname
- Address
- DoH URL
- DoT
- Protocol
- Category
- Port

وجود دارد.

---

## 🎛️ فیلترها

DNSها را می‌توان بر اساس دسته‌بندی، نوع آدرس و پروتکل فیلتر کرد.

فیلترهای موجود:

    All
    Standard
    AdBlock
    Family
    Security
    Malware
    Adult Filter
    Unfiltered
    FreeShekan
    Private
    IPv4
    IPv6
    DoH
    DoT
    DNSCrypt

---

## 📋 نمایش DNS

هر DNS در رابط وب به‌صورت یک کارت نمایش داده می‌شود.

اطلاعات اصلی:

- آدرس DNS
- Provider
- Category
- Protocol
- Type
- وضعیت
- دکمه Copy

---

## 📋 کپی سریع

هر رکورد دارای دکمه **Copy** است.

با انتخاب آن، مقدار DNS مستقیماً در Clipboard دستگاه قرار می‌گیرد.

---

## 🔄 بروزرسانی خودکار

چرخه کلی پروژه:

    ┌─────────────────────┐
    │     منابع عمومی     │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │      جمع‌آوری       │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │       استخراج       │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │        تحلیل        │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │     اعتبارسنجی      │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ حذف موارد تکراری     │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │     تولید آمار      │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │      انتشار         │
    └──────────┬──────────┘
               │
          ┌────┴────┐
          ▼         ▼
       GitHub    Cloudflare
       Pages      Workers

---

## 📁 ساختار داده

اطلاعات DNS در قالب JSON ذخیره می‌شوند.

نمونه یک رکورد DoT:

    {
      "provider": "Example DNS",
      "address": "dns.example.com",
      "name": "Example DNS",
      "source": "curl",
      "type": "DoT",
      "hostname": "dns.example.com",
      "protocol": "DoT",
      "dot": "tls://dns.example.com:853"
    }

برای DNSهای DoH نیز اطلاعات مربوط به URL، Hostname و Path نگهداری می‌شود.

---

## 🌍 وب‌سایت پروژه

### GitHub Pages

نسخه وب پروژه روی GitHub Pages:

**https://aristapanell-cell.github.io/AristaDns/**

[ورود به Arista DNS Hub](https://aristapanell-cell.github.io/AristaDns/)

### Cloudflare Workers

نسخه وب اجراشده روی Cloudflare Workers:

**https://aristadns.arista-panel.workers.dev/**

[ورود به نسخه Cloudflare](https://aristadns.arista-panel.workers.dev/)

---

## 🐙 مخزن GitHub

کد و فایل‌های پروژه در GitHub:

**https://github.com/aristapanell-cell/AriataPanel**

[مشاهده مخزن در GitHub](https://github.com/aristapanell-cell/AriataPanel)

---

## 🛠️ فناوری‌ها

### Backend

- Python
- Requests
- BeautifulSoup
- Regular Expressions
- URL Parsing
- IP Address Analysis

### Frontend

- HTML
- CSS
- JavaScript

### زیرساخت

- GitHub
- GitHub Actions
- GitHub Pages
- Cloudflare Workers

---

## 📂 ساختار پروژه

    AristaDns/
    │
    ├── assets/
    │   └── logo/
    │       └── readme.png
    │
    ├── data/
    │   ├── dns.json
    │   └── stats.json
    │
    ├── index.html
    ├── style.css
    ├── script.js
    │
    ├── parsers/
    │   └── ...
    │
    ├── .github/
    │   └── workflows/
    │       └── ...
    │
    └── README.md

ساختار فایل‌ها ممکن است هم‌زمان با توسعه پروژه تغییر کند.

---

## 🚀 هدف پروژه

هدف Arista DNS Hub ایجاد یک بانک اطلاعاتی بزرگ، تمیز، قابل جست‌وجو و به‌روز از DNSهای عمومی است.

تمرکز پروژه بر روی:

**جمع‌آوری → استخراج → تحلیل → تست → دسته‌بندی → حذف تکراری‌ها → انتشار**

است.

---

## 🔮 توسعه آینده

قابلیت‌های قابل توسعه پروژه:

- ⚡ تست سرعت DNS
- 📡 تست دسترسی
- 🧪 تست واقعی DoH
- 🧪 تست واقعی DoT
- 📈 رتبه‌بندی DNSها
- 🌍 تحلیل جغرافیایی
- 📊 آمار پیشرفته
- 🔄 اضافه شدن منابع بیشتر
- 🌐 API عمومی
- 📱 رابط کاربری پیشرفته‌تر

---

## 🤝 مشارکت

پروژه متن‌باز است.

برای گزارش خطا، پیشنهاد قابلیت جدید یا مشارکت در توسعه پروژه می‌توانید از مخزن GitHub استفاده کنید.

**GitHub:**

https://github.com/aristapanell-cell/AriataPanel

---

## 📢 ارتباط با آریستا

برای اخبار، بروزرسانی‌ها و پروژه‌های جدید:

<a href="https://t.me/aristapanel">
<img src="https://img.shields.io/badge/Telegram-229ED9?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
</a>

---

<div align="center">

## ❤️ توسعه داده شده توسط تیم آریستا

### Arista Team

**جمع‌آوری • استخراج • تحلیل • تست • دسته‌بندی • انتشار**

<br>

⭐ اگر پروژه برای شما مفید بود، با Star کردن مخزن GitHub از توسعه آن حمایت کنید.

</div>
