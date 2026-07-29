# ⚡ Visa Agency Web Service & REST API Backend

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x/6.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.15-Red?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Swagger](https://img.shields.io/badge/OpenAPI-Swagger_UI-85EA2D?logo=swagger&logoColor=black)](https://swagger.io/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media_CDN-3448C5?logo=cloudinary&logoColor=white)](https://cloudinary.com/)

A enterprise-grade RESTful API backend built for visa consulting agencies. Powers applicant lifecycle management, multi-currency conversion, money receipt generation, staff allocations, custom brand logo variations, and automated email dispatching.

---

## 🌟 Architecture & Core Modules

### 📋 `applicant`
* **Applicant Lifecycle**: State-machine tracking status transitions (Submitted, In Review, Visa Approved, Ticket Stamping, Handover, Rejected, Refunded).
* **Payment & Receipt Engine**: Automated money receipt creation, multi-currency conversion (BDT, EUR, GBP, USD), and high-precision exchange rate tracking.
* **Refund Tracking**: Agreement clause compliance, refundable amount calculations, and bank transfer record management.
* **Performance Query Selectors**: Subquery annotations and precomputed counts eliminating N+1 database queries.

### 👥 `staff`
* **Team Members & Hierarchy**: Parent staff and sub-staff allocation mappings.
* **Monthly Slot Allocation Engine**: Monthly quota limits, used slot tracking, and remaining capacity calculations.
* **Performance & Rankings**: Monthly/Yearly rank metrics and manual/dummy visa statistics (Approved, Rejected, Processing additions).
* **Public Profile Credentials**: Secure public profile endpoints and QR code payload verification.

### 🏛️ `agency`
* **Company Information & Branding**: Organization configuration, money receipt notes, and default policies.
* **Company Logo Variations**: Multi-logo asset storage (Primary Header Logo, Signature Seal, Reverse Dark Logo, White Logo, Badge Icon) ordered by serial numbers.
* **Email Templates**: Dynamic template engine supporting status-triggered automated emails and Generous Email Templates with custom header logo variations.
* **Lawyers & Branch Offices**: Legal representative details and agency office locations.

### ✈️ `visa` & `country`
* **Visa Categories & Services**: Country-wise visa types, job positions, pricing structures, and required document checklists.

---

## 🚀 Key Technical Highlights

* **High-Precision Multi-Currency Engine**: Reversible Base-to-EUR calculation supporting custom manual rates with strict 8-decimal place precision validation.
* **Database Query Optimization**: Optimized querysets utilizing `select_related`, `prefetch_related`, and subquery annotations to reduce DB queries from $N+1$ down to single-digit batch queries.
* **Media & Cloud Storage**: Seamless Cloudinary CDN integration for document attachments, applicant photos, company logos, and signature seals.
* **Automated PDF & Email Notifications**: Django HTML email templating with dynamic context variable placeholders (`{{ applicant_name }}`, `{{ current_status }}`, etc.).

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.12+ |
| **Framework** | Django 5.x / 6.x |
| **REST API** | Django REST Framework (DRF) |
| **Database** | PostgreSQL / SQLite3 |
| **Media Storage** | Cloudinary CDN |
| **Documentation** | drf-spectacular / OpenAPI / Swagger UI |
| **CORS Control** | django-cors-headers |

---

## 📂 Project Structure

```
Visa Agency Website/
├── agency/                 # Company information, logo variations, email templates
├── applicant/              # Applicants, payment receipts, status history, selectors
├── staff/                  # Team members, monthly slots, sub-staff allocations
├── visa/                   # Visa titles, job catalog, document requirements
├── country/                # Destination countries & guidelines
├── core/                   # Shared utilities, validators, choices
├── api/                    # API routing, public endpoints, swagger configuration
├── Visa_Web_Service/       # Django project configuration & settings
├── manage.py
└── requirements.txt
```

---

## 🛠️ Getting Started & Local Setup

### Prerequisites
* **Python**: `3.11+` or `3.12+`
* **pip** & **virtualenv**

### Local Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rakibIV/visa-agency.git
   cd visa-agency
   ```

2. **Create & activate virtual environment**:
   ```bash
   python -m venv visa-env
   # On Windows:
   visa-env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create administrative superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver 8000
   ```
   * Server API: `http://localhost:8000/api/`
   * Swagger Documentation: `http://localhost:8000/api/docs/`

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
