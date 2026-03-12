# Credit Underwriting Platform - Backend

FastAPI backend for the Credit Underwriting Platform with PostgreSQL/SQLite database.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python)

## Features

- Entity onboarding with CIN/PAN validation
- Document upload with auto-classification
- OCR/NLP data extraction from PDF/Excel
- Rule-based credit recommendation engine
- PDF report generation with ReportLab

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLAlchemy
- **PDF**: ReportLab
- **Data Processing**: pandas, PyPDF2

## Quick Start

### Prerequisites

- Python 3.8+

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Create `.env` file:

```env
DATABASE_URL=sqlite:///./credit_underwriting.db
DEBUG=True
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/onboard` | Entity onboarding |
| POST | `/api/v1/onboard/validate` | Validate CIN/PAN |
| POST | `/api/v1/upload` | Upload document |
| GET | `/api/v1/extract/{entity_id}` | Get extracted data |
| POST | `/api/v1/recommend` | Get recommendation |
| GET | `/api/v1/report/{entity_id}` | Get report data |
| GET | `/api/v1/report/{entity_id}/pdf` | Download PDF |

## Database Schema

### Entities
- `id`: Primary key
- `cin`: Corporate Identity Number
- `pan`: Permanent Account Number
- `name`: Company name
- `sector`: Industry sector
- `turnover`: Annual turnover
- `loan_type`, `loan_amount`, `tenure_months`, `interest_rate`

### Annual Reports
- `entity_id`: Foreign key
- `year`: Fiscal year
- `revenue`, `ebitda`, `net_profit`
- `total_debt`, `total_equity`
- `debt_to_equity`: Calculated ratio

### Borrowing Profiles
- `entity_id`: Foreign key
- `loan_amount`, `tenure_months`, `interest_rate`, `emi`

## Credit Scoring Rules

| Metric | Threshold | Status |
|--------|-----------|--------|
| Debt to Equity | < 2.0 | Good |
| Debt to Equity | 2.0 - 2.5 | Borderline |
| Debt to Equity | > 2.5 | High Risk |
| Interest Coverage | > 2.0 | Good |
| Interest Coverage | < 1.5 | Low |

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Deployment

### Railway
```bash
# Connect GitHub repo to Railway
# Set DATABASE_URL for PostgreSQL
```

### Render
```bash
# Create runtime.txt: python-3.10.0
# Create Procfile: web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

## Project Structure

```
backend/
├── app/
│   ├── config.py          # Configuration
│   ├── database.py        # Database setup
│   ├── main.py           # FastAPI app
│   ├── models/           # SQLAlchemy models
│   ├── routers/          # API endpoints
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
├── requirements.txt
├── tests/                # Unit tests
└── README.md
```

## License

MIT License - see LICENSE file
