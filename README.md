# CAMPUS TRADE 🎓🛒

CAMPUS TRADE is a clean, modern, student-to-student marketplace designed exclusively for college campuses. It provides a secure, organized platform where college students can buy and sell second-hand items such as books, calculators, electronics, sports equipment, cycles, and hostel essentials directly within their campus community.

Think of it as **"OLX for college communities"** or **"Facebook Marketplace for college campuses"**.

---

## 🌟 Key Features

### 🔐 Authentication (Powered by Clerk)
* **Seamless Login**: Email, Password, and Google Sign-in integrated via Clerk CDN Components.
* **Route Protection**: Browsing is public, but creating, editing, deleting listings, marking items as sold, and viewing profiles is gated to logged-in students.
* **Security**: Backend endpoints strictly verify Clerk JWT session tokens on every transactional action.

### 🏠 Landing Page & Discovery
* **Tagline and Search**: Modern search bar supporting fuzzy string matching by item titles and descriptions.
* **Structured Categories**: Browse items by custom university-specific categories.
* **Featured Showcase**: Carousel of the latest items posted on campus.

### 📦 Marketplace Management (CRUD)
* **Create Listing**: Post new items with title, price (INR ₹), description, category selection, contact information, and an optional image.
* **Edit/Update**: Modify pricing, descriptions, or change pictures.
* **Availability Toggling**: Sellers can toggle listings between **Available** and **Sold** status.
* **Delete Listing**: Remove active posts, which automatically cleans up uploaded images from the local storage.

### 👤 Student Dashboard & Profile
* **My Listings**: A clean dashboard separated into *Active Listings* and *Sold Listings*.
* **Profile Stats**: Live counters detailing total items listed vs. items successfully sold.

---

## 🛠️ Technology Stack

* **Frontend**: HTML5, CSS3 (Custom design system), Vanilla JavaScript (ES6)
* **Backend**: Python 3, Flask
* **Database**: SQLite3 (Raw SQL, direct connections)
* **Authentication**: Clerk Vanilla JS SDK + PyJWT Token Verification

*No heavy frameworks (React, TS), bundlers (Vite), ORMs (Prisma), or complex containerizers (Docker) are used, ensuring the code is lightweight, extremely easy to explain, and ideal for interviews.*

---

## 📁 Flat Directory Structure

```
CAMPUS-TRADE/
├── console_version_archive/ # Contains the archived CLI version scripts
├── app.py                # Flask controller, JWT validator & API Router
├── models.py             # SQLite schema setup & CRUD raw queries
├── requirements.txt      # Python dependencies
├── README.md             # Developer setup instructions
├── .env.example          # Environment variables template
├── database.db           # SQLite database file (generated automatically)
├── static/
│   ├── css/
│   │   └── style.css     # Premium UI styling and system design
│   ├── js/
│   │   └── script.js     # Clerk integration & frontend REST API fetchers
│   └── uploads/          # Directory containing local uploaded item images
└── templates/            # HTML base and page sub-templates
    ├── base.html
    ├── index.html
    ├── sign_in.html
    ├── listings.html
    ├── listing_detail.html
    ├── create_listing.html
    ├── edit_listing.html
    ├── my_listings.html
    └── profile.html
```

---

## ⚙️ Installation & Local Setup

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your machine.

### 2. Clone and Prepare Project Root
```bash
git clone https://github.com/yourusername/campus-trade.git
cd campus-trade
```

### 3. Install Dependencies
It is highly recommended to set up a python virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Copy the `.env.example` file to `.env`:
```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS / Linux
```

Fill in the variables in `.env`:
* Generate a random string for `SECRET_KEY`.
* Retrieve your publishable key and secret key from the [Clerk Dashboard](https://dashboard.clerk.com/).

```ini
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secure-session-key-here
DATABASE_PATH=database.db

CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

---

## 🔑 Clerk Authentication Setup Guide

1. Sign up on [Clerk](https://clerk.com/) and create a new application named **Campus Trade**.
2. Select **Email** and **Google** as login providers.
3. Once created, go to **API Keys** in the sidebar.
4. Copy the **Publishable Key** (`pk_test_...`) and **Secret Key** (`sk_test_...`) and paste them into your `.env` file.
5. In Clerk Dashboard, go to **Paths** under **User & Authentication** (or search in the settings menu) to set redirect configurations:
   * **Sign In URL**: `/sign-in`
   * **Sign Up URL**: `/sign-in` (Clerk's Sign-In handles tab transitions natively)
6. Run your local server and check sign-in!

---

## 🚀 Running Locally

Launch the Flask development server:
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in your web browser.

Upon first load:
* SQLite will create `database.db` automatically in the project folder.
* The application will register the required schemas.
* Static image upload folders will be automatically created in `static/uploads/`.

---

## 📸 Screenshots
*(Create a screenshots folder or links here after deploying to highlight clean design, profile stats, and item listings).*

---

## 🔮 Future Enhancements
* **Campus Email Verification**: Validate user registrations against college domains (e.g. `@university.edu`).
* **Real-time Chat**: Implement a WebSocket chat system to communicate directly instead of displaying phone numbers.
* **Favorites/Wishlist**: Save items for later.
* **Multi-Campus Support**: Support student listings across multiple nearby campuses.

---

## 📝 License
This project is licensed under the MIT License. Feel free to use it for portfolio submissions, resumes, or learning projects.
