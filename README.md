# NSFDC Concessional Loan Scheme Portal

A multilingual web portal that helps Scheduled Caste (SC) beneficiaries find the right concessional loan scheme, calculate their EMI, and locate nearby channel partner banks. It also includes an admin panel for managing partners, schemes, and applications.

Built with **Flask (Python)**, **SQLite**, and plain **HTML / CSS / JavaScript**.

## Features

- **Smart Scheme Recommender**: a 10-step wizard that asks about loan purpose, gender, amount, education status, and family income, then recommends the best-matching scheme.
- **Financial & EMI Calculator**: shows monthly EMI, total interest, and total repayment for the recommended scheme.
- **Geo-Spatial Partner Locator**: finds nearby channel partner banks on an interactive map (Leaflet), sorted by distance using the Haversine formula.
- **Community Success Stories**: real-world style posts for each scheme.
- **Application Guidance**: choose online or offline mode and get a final summary of documents and steps.
- **7 languages**: English, Hindi, Marathi, Tamil, Telugu, Bengali, and Gujarati.
- **Accessibility options**: font size control, skip-to-content link, and screen reader support.
- **Admin Panel** (`/admin`): login, view applications, add/edit/delete partners, post success stories, and update scheme details.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Maps | Leaflet.js |

## Project Structure

```
final/
├── app.py              # Flask server and API routes
├── database.py         # Database setup and connection
├── database.db         # SQLite database
└── static/
    ├── index.html      # Citizen-facing portal
    ├── admin.html      # Admin panel
    ├── app.js          # Frontend logic
    ├── styles.css      # Styling
    └── translations.js # Language translations
```

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Black7886/Scheme-Recommender.git
   cd Scheme-Recommender
   ```

2. Install the dependency:
   ```bash
   pip install flask
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open your browser and go to:
   - Citizen portal: http://localhost:5000
   - Admin panel: http://localhost:5000/admin

> The database is created automatically on first run if it does not exist.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/schemes` | List all loan schemes |
| POST | `/api/recommend` | Get the best scheme for a user's profile |
| POST | `/api/calculate-emi` | Calculate EMI and repayment |
| GET | `/api/partners` | Find channel partner banks |
| GET | `/api/community-posts/<scheme_code>` | Success stories for a scheme |
| POST | `/api/applications` | Submit an application |
| POST | `/api/admin/login` | Admin login |
| GET | `/api/admin/applications` | View all applications (admin) |
| GET/POST/PUT/DELETE | `/api/admin/partners` | Manage partners (admin) |
| POST | `/api/admin/posts` | Add a success story (admin) |
| POST | `/api/admin/schemes` | Update a scheme (admin) |

## Security Note

This project uses a hard-coded demo admin login and secret key for development. **Before deploying publicly**, move them to environment variables and use proper authentication.

## Disclaimer

This is a demonstration project and is not an official Government of India website. Scheme details should always be verified with the official NSFDC website or a nearby channel partner bank.

## Author

[Black7886](https://github.com/Black7886)
