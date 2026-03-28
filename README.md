# Naija Trend-to-Cash

A content operations dashboard for aggregating trending data, managing content workflow, and publishing to multiple external websites.

## Features

- **Trend Discovery** - Fetch trending topics from Google Trends (Nigeria, US, UK, Global)
- **Content Workflow** - Manage candidates → source packs → drafts → QC → publish pipeline
- **AI Content Generation** - Powered by Google Gemini for article generation, headlines, excerpts, and FAQs
- **Multi-Site Publishing** - Connect and publish to multiple external websites via API
- **Quality Control** - Built-in QC checklist for content review
- **Metrics Tracking** - Track Search Console metrics over time

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (local) / Turso (production)
- **AI**: Google Gemini API
- **Trends**: Google Trends via pytrends
- **Deployment**: Vercel (serverless)

## Local Development

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/trendcash.git
   cd trendcash
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` with your settings:
   ```
   NTC_SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key
   ```

6. Run the application:
   ```bash
   python -c "from app import create_app; create_app().run(debug=True, port=5000)"
   ```

7. Open http://localhost:5000 in your browser

## Production Deployment (Vercel + Turso)

### Prerequisites

- [GitHub](https://github.com) account
- [Vercel](https://vercel.com) account (free tier works)
- [Turso](https://turso.tech) account (free tier: 9GB storage)

### Step 1: Create Turso Database

1. Install the Turso CLI:
   ```bash
   # macOS/Linux
   curl -sSfL https://get.tur.so/install.sh | bash
   
   # Windows (using PowerShell)
   iwr https://get.tur.so/install.ps1 -useb | iex
   ```

2. Login to Turso:
   ```bash
   turso auth login
   ```

3. Create a database:
   ```bash
   turso db create trendcash
   ```

4. Get your database URL:
   ```bash
   turso db show trendcash
   ```
   Copy the URL (e.g., `libsql://trendcash-xxx.turso.io`)

5. Create an auth token:
   ```bash
   turso db tokens create trendcash
   ```
   Copy this token - you'll need it for Vercel

### Step 2: Push to GitHub

1. Create a new repository on GitHub named `trendcash`

2. Initialize and push:
   ```bash
   git init
   git branch -M main
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/trendcash.git
   git push -u origin main
   ```

### Step 3: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub

2. Click "New Project"

3. Import your `trendcash` repository

4. Configure environment variables:
   
   | Variable | Value | Required |
   |----------|-------|----------|
   | `TURSO_DATABASE_URL` | `libsql://your-db.turso.io` | Yes |
   | `TURSO_AUTH_TOKEN` | Your Turso auth token | Yes |
   | `NTC_SECRET_KEY` | Random secret string | Yes |
   | `GEMINI_API_KEY` | Your Gemini API key | No |

5. Click "Deploy"

6. Wait for deployment to complete

### Step 4: Generate a Secret Key

Generate a secure secret key for `NTC_SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NTC_SECRET_KEY` | Flask secret key for sessions | Yes |
| `TURSO_DATABASE_URL` | Turso database URL (production only) | Production |
| `TURSO_AUTH_TOKEN` | Turso auth token (production only) | Production |
| `GEMINI_API_KEY` | Google Gemini API key for AI features | No |
| `GOOGLE_API_KEY` | Alternative to GEMINI_API_KEY | No |
| `NTC_DB_PATH` | Custom SQLite path (local only) | No |

## External Site Integration

To connect an external website for publishing:

1. The external site must have an API endpoint that accepts POST requests
2. Add the site in the "Sites" section of the dashboard
3. Provide:
   - Site name and slug
   - API URL (e.g., `https://yoursite.com/api/content`)
   - API key (if required)

### API Specification

Your external site should accept:

```
POST /api/content
Headers: Authorization: Bearer <api_key>
Body: {
  "title": "Article Title",
  "content": "Article content in markdown",
  "slug": "article-slug",
  "category": "Category Name",
  "meta": {
    "excerpt": "Short excerpt"
  }
}

Response: {
  "success": true,
  "post_id": "123",
  "url": "https://yoursite.com/article-slug"
}
```

### Example External Site

See `external_site_template/` for a sample Flask site with the required API.

## Project Structure

```
trendcash/
├── api/
│   └── index.py          # Vercel serverless entry point
├── app/
│   ├── __init__.py
│   ├── app.py            # Main Flask application
│   ├── db.py             # SQLite database (local)
│   ├── db_turso.py       # Turso database (production)
│   ├── trends_api.py     # Google Trends integration
│   ├── ai_writer.py      # Gemini AI integration
│   ├── publisher.py      # External site publishing
│   ├── sites.py          # Site management routes
│   ├── static/
│   │   └── style.css
│   └── templates/
│       └── *.html
├── scripts/
│   ├── fetch_trends.py   # Scheduled trend fetching
│   └── import_trends.py  # CSV import utility
├── external_site_template/
│   └── ...               # Sample external site
├── data/
│   └── ntc.db            # Local SQLite database
├── requirements.txt
├── vercel.json
├── .env.example
└── README.md
```

## Workflow

```
Trend Discovery → Candidates → Source Packs (2+ required) → Drafts → QC Review → Publish → External Sites
```

## Notes

- Delete `data/ntc.db` to reset the local database
- Each site can have different niches and categories
- The dashboard tracks publish history per site

## License

MIT
