# External Site Template

This is a sample external website that can receive content from the Naija Trend-to-Cash dashboard.

## Setup

1. Create a virtual environment:
```bash
cd external_site_template
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Set your API key:
```bash
set SITE_API_KEY=your-secret-api-key
```

3. Run the site:
```bash
python app.py
```

The site will run on `http://127.0.0.1:5001`

## Connecting to Dashboard

1. In the Naija Trend-to-Cash dashboard, go to **Sites** and click **Add New Site**
2. Enter:
   - **Name**: My External Site
   - **Slug**: my-external-site
   - **Niche**: Select the appropriate niche
   - **API URL**: `http://127.0.0.1:5001/api/content`
   - **API Key**: The value you set for `SITE_API_KEY`
3. Click **Create Site**

Now you can publish content from the dashboard to this external site.

## API Endpoints

### POST /api/content
Receives content from the dashboard.

**Headers:**
- `Authorization: Bearer <api_key>`
- `Content-Type: application/json`

**Body:**
```json
{
  "title": "Article Title",
  "content": "Full article content...",
  "slug": "article-slug",
  "category": "finance",
  "meta": {
    "excerpt": "Short excerpt..."
  }
}
```

### GET /api/health
Health check endpoint.

## Customization

To use this template for your own site:

1. Modify the HTML templates in `templates/`
2. Update the styling
3. Add your own features (comments, social sharing, etc.)
4. Deploy to your hosting provider
5. Update the API URL in the dashboard

## Production Notes

- Change the `SECRET_KEY` environment variable
- Use a proper database (PostgreSQL, MySQL) instead of SQLite
- Add HTTPS
- Add input validation and sanitization
- Add rate limiting
