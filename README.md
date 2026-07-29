# ⚡ Visa Agency Web Service & REST API Backend

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x/6.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.15-Red?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Swagger](https://img.shields.io/badge/OpenAPI-Swagger_UI-85EA2D?logo=swagger&logoColor=black)](https://swagger.io/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media_CDN-3448C5?logo=cloudinary&logoColor=white)](https://cloudinary.com/)

An enterprise-grade RESTful API backend powering visa agency operations. Features high-precision multi-currency conversion, live & manual exchange rate engines, query optimization architectures (eliminating N+1 queries), staff slot allocation limits, money receipt generation, and automated email notifications.

---

## 🏛️ System Architecture & Data Schema

```
 +-----------------------------------------------------------------------+
 |                     Visa Agency REST API Backend                      |
 +-----------------------------------+-----------------------------------+
                                     |
    +-----------------+--------------+--------------+-----------------+
    |                 |                             |                 |
+---v----+       +----v----+                   +----v----+       +----v----+
|  user  |       | agency  |                   | staff   |       | visa    |
| (Auth) |       | (Logos, |                   | (Slots, |       | (Jobs,  |
+--------+       | Emails) |                   | Sub-St) |       | Docs)   |
                 +----+----+                   +----+----+       +---------+
                      |                             |
                      +--------------+--------------+
                                     |
                                +----v----+
                                |applicant|
                                |(Payments|
                                | Status) |
                                +---------+
```

---

## 💱 Deep Dive: Multi-Currency & Automatic Exchange Rate Engine

The backend features a robust **Multi-Currency & Exchange Rate Engine** (`applicant/services.py` & `applicant/currency.py`):

### 1. Hybrid Automatic & Manual Rate Resolution
When a payment is recorded or updated:
* **Manual Rate Mode**: If a `manual_exchange_rate` is provided by the frontend (computed as $\text{Base Amount} \div \text{Euro Amount}$), the engine uses the specified manual rate.
* **Automatic Live Rate Mode**: If no manual rate is provided, the backend automatically queries the live exchange rate provider (`get_exchange_rate(from_currency)`). If the live API is unreachable, it automatically falls back to pre-configured fallback exchange rates (`get_fallback_exchange_rate()`).

### 2. High-Precision Ratio Calculation & DB Storage
* The engine normalizes all currencies relative to **EUR**.
* Stores high-precision ratios with $10^{-8}$ decimal places (`quantize(Decimal("0.00000001"))`) to prevent rounding errors across multiple transaction log summaries.
* Validates incoming decimal inputs to guarantee compliance with DRF's `DecimalField(max_digits=18, decimal_places=8)` constraint.

---

## 🚀 Deep Dive: Database Query & N+1 Optimization Architecture

To ensure high performance under heavy load, the backend features optimized queryset selectors (`staff/selectors.py` & `applicant/selectors.py`):

### 1. Subquery Annotations for Staff Monthly Slots
* Rather than invoking `obj.applicants.count()` inside serializer loops (which previously triggered $N+1$ SQL queries for every slot of every staff member), `get_staff_queryset` pre-computes slot usage directly in SQL:
  ```python
  Prefetch(
      "monthly_slots",
      queryset=StaffMonthlySlot.objects.annotate(
          used_slots_count=Count("applicants")
      ).order_by("-allocation_month"),
  )
  ```
* Reduced database query counts on staff list endpoints (`/api/staffs/`) from hundreds of queries down to **4 batch queries total**.

### 2. Status Classification State Engine
* `get_status_classification()` dynamically categorizes active application statuses into `approved_ids` and `rejected_ids` in a single query pass.
* Automatically classifies every status occurring after the **"Visa Approved"** stage as an approved milestone for performance statistics and public profile reporting.

---

## 📧 Email Templates & Brand Logo Variations Data Model

The `agency` app manages email template definitions and brand logo assets:

### `CompanyLogo` Model
* Allows agencies to upload custom brand logo variations (e.g. *Primary Header Logo*, *Signature Seal*, *Reverse Dark Logo*, *White Logo*, *Badge Icon*) ordered by `serial_number`.

### `EmailTemplate` Model
* **Standard Status Templates**: Linked to specific `ApplicationStatus` models for automated transactional emails.
* **Generous Email Templates**: Configured with `is_generous=True`, `top_left_logo`, and `top_center_logo` fields, rendering a clean text layout without standard header/footer banners.

---

## 📑 Core API Endpoints Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/applicants/` | `GET`, `POST` | List and create visa applicants |
| `/api/applicants/{id}/` | `GET`, `PATCH`, `DELETE` | Retrieve, update, or soft-delete applicant profile |
| `/api/applicants/{id}/payments/` | `GET`, `POST` | Payment records with automatic EUR & rate conversion |
| `/api/staffs/` | `GET`, `POST` | Team members list (with pre-computed slot counts) |
| `/api/staffs/{id}/monthly-slots/` | `GET`, `POST` | Monthly slot allocations for team members |
| `/api/company-logos/` | `GET`, `POST`, `PATCH` | Company logo variations ordered by serial numbers |
| `/api/email-templates/` | `GET`, `POST`, `PATCH` | Email templates (General, Status, and Generous) |
| `/api/public/verify-staff/{id}/` | `GET` | Public staff profile credentials & QR code verification |

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.12+ |
| **Web Framework** | Django 5.x / 6.x |
| **API Framework** | Django REST Framework (DRF) |
| **Database** | PostgreSQL / SQLite3 |
| **Media Storage** | Cloudinary CDN |
| **Documentation** | drf-spectacular / OpenAPI / Swagger UI |

---

## 📂 Directory Structure

```
Visa Agency Website/
├── agency/                 # Company information, logo variations, email templates
├── applicant/              # Applicants, payments, currency conversion, selectors
├── staff/                  # Staff members, monthly slots, sub-staff allocations
├── visa/                   # Visa titles, job catalog, document requirements
├── country/                # Destination countries & guidelines
├── core/                   # Shared validators, choices, helper functions
├── api/                    # API routing, public endpoints, swagger schema
├── Visa_Web_Service/       # Django project configuration & settings
├── manage.py
└── requirements.txt
```

---

## 🚀 Setup & Local Execution

### Prerequisites
* **Python**: `3.11+` or `3.12+`

### Installation Commands

1. **Clone Repository**:
   ```bash
   git clone https://github.com/rakibIV/visa-agency.git
   cd visa-agency
   ```

2. **Setup Environment & Dependencies**:
   ```bash
   python -m venv visa-env
   # On Windows:
   visa-env\Scripts\activate
   # On Linux/macOS:
   source visa-env/bin/activate

   pip install -r requirements.txt
   ```

3. **Database Migration**:
   ```bash
   python manage.py migrate
   ```

4. **Run Server**:
   ```bash
   python manage.py runserver 8000
   ```
   * REST API Base: `http://localhost:8000/api/`
   * Swagger Documentation: `http://localhost:8000/api/docs/`

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
