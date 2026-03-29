# Naija Trend-to-Cash - Testing Guide

## Quick Status Check

| Endpoint | Status |
|----------|--------|
| `/` (Dashboard) | 200 OK |
| `/discover` | 200 OK |
| `/selection` | 200 OK |
| `/trends` | 200 OK |
| `/drafts` | 200 OK |
| `/qc` | 200 OK |
| `/publish` | 200 OK |
| `/sites` | 200 OK |
| `/metrics` | 200 OK |
| `/settings` | 200 OK |

---

## Phase 1: Settings & Configuration

### Test 1.1: Settings Page
**URL:** `/settings`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Visit `/settings` | Page loads with form | |
| 2 | Change "Publish daily limit" to 15 | Value updates | |
| 3 | Change "Default image policy" to "priority" | Value updates | |
| 4 | Add a Gemini API key (get from https://aistudio.google.com/apikey) | Key saves (masked) | |
| 5 | Click "Save Settings" | Success message appears | |

**Notes:**

---

## Phase 2: Trend Discovery

### Test 2.1: Fetch Trends from Google
**URL:** `/discover`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Visit `/discover` | Page loads with forms | |
| 2 | Select "Nigeria (NG)" region | Dropdown works | |
| 3 | Click "Fetch Trends" | Success message shows count | |
| 4 | Check "Recently Fetched Trends" table | New trends appear | |

**Known Issue:** Google Trends API may be slow or rate-limited. If it fails, the error will show.

### Test 2.2: Explore a Keyword
**URL:** `/discover`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Enter a keyword (e.g., "fuel price") | Input accepts text | |
| 2 | Click "Explore" | Page reloads with results | |
| 3 | Check "Interest Over Time" chart | Chart renders | |
| 4 | Check "Related Queries" section | Rising/Top queries show | |
| 5 | Check "Related Topics" section | Rising/Top topics show | |
| 6 | Click a suggestion chip | Navigates to explore that topic | |

**Notes:**

---

## Phase 3: Trend Management

### Test 3.1: Manual Trend Entry
**URL:** `/trends`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Visit `/trends` | Page loads with form and table | |
| 2 | Fill in Topic: "Fuel price increase 2024" | Input accepts | |
| 3 | Fill in Category: "Finance" | Input accepts | |
| 4 | Fill in Source: "Google Trends" | Input accepts | |
| 5 | Set Velocity score: 8.5 | Number input works | |
| 6 | Set Advertiser safety: 9.0 | Number input works | |
| 7 | Set Commercial intent: 7.5 | Number input works | |
| 8 | Set Evergreen: 6.0 | Number input works | |
| 9 | Click "Add Candidate" | Success message, trend appears in table | |

### Test 3.2: Filter Trends
**URL:** `/trends`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Click on a category filter link | URL changes, only that category shows | |
| 2 | Verify filtered results | Correct filtering | |

---

## Phase 4: Source Pack Management

### Test 4.1: Add Sources to Trend
**URL:** `/sources/{id}`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | From `/trends`, click "Add sources" on a trend | Navigates to sources page | |
| 2 | Enter URL: `https://example.com/article1` | Input accepts | |
| 3 | Enter Publisher: "BBC News" | Input accepts | |
| 4 | Enter Published date: "2024-01-15" | Date input works | |
| 5 | Enter Notes: "Primary source" | Textarea accepts | |
| 6 | Click "Add Source" | Source appears in table | |
| 7 | Add a second source (required for drafting) | Second source appears | |

### Test 4.2: Draft Creation Requirements
**URL:** `/trends`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Try to create draft with only 1 source | Error: "At least 2 sources required" | |
| 2 | Add 2nd source, try again | Draft created successfully | |

---

## Phase 5: Draft Editing (Rich Text Editor)

### Test 5.1: Basic Draft Editing
**URL:** `/drafts` → `/drafts/{id}`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Visit `/drafts` | List of drafts shows | |
| 2 | Click "Edit" on a draft | Opens editor page | |
| 3 | Verify TinyMCE editor loaded | Rich text toolbar visible | |
| 4 | Type/edit content in editor | Content updates | |
| 5 | Use Bold button | Text becomes bold | |
| 6 | Use Italic button | Text becomes italic | |
| 7 | Create a bulleted list | List formats correctly | |
| 8 | Insert a link | Link dialog appears, works | |
| 9 | Click "Switch to Markdown" | Shows raw textarea | |
| 10 | Click "Switch to Rich Editor" | TinyMCE returns | |
| 11 | Click "Save" | Success message | |

### Test 5.2: AI Assistant Features
**URL:** `/drafts/{id}` (sidebar)

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Click "Test AI Connection" | Shows success/failure | |
| 2 | If failed, add Gemini API key in Settings | | |
| 3 | Select headline angle, click "Generate" | Headlines appear | |
| 4 | Click a headline | Title field updates | |
| 5 | Click "Generate Excerpt" | Excerpt appears | |
| 6 | Select improvement type, click "Improve" | "Apply Changes" button appears | |
| 7 | Click "Apply Changes" | Content updates | |
| 8 | Click "Generate FAQs" | FAQs appear | |
| 9 | (If candidate linked) Click "Regenerate" | New content appears | |

---

## Phase 6: Quality Control

### Test 6.1: Send Draft to QC
**URL:** `/drafts/{id}`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Edit a draft, click "Send to QC" | Redirects to QC page | |
| 2 | Verify draft status changed | Status = "qc" | |

### Test 6.2: QC Checklist
**URL:** `/qc`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Visit `/qc` | Drafts in QC queue show | |
| 2 | Check all 4 boxes (Source valid, Unique value, Advertiser safety, Actionability) | Checkboxes work | |
| 3 | Enter Reviewer name | Input accepts | |
| 4 | Submit without checking all boxes | Error message | |
| 5 | Check all boxes and submit | Draft approved, removed from QC | |

---

## Phase 7: Site Management

### Test 7.1: Add External Site
**URL:** `/sites/`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Visit `/sites/` | Sites list shows | |
| 2 | Click "Add New Site" | Form appears | |
| 3 | Name: "Test Blog" | Input accepts | |
| 4 | Slug: "test-blog" | Input accepts | |
| 5 | Niche: "Technology" | Input accepts | |
| 6 | Description: "My test blog" | Textarea accepts | |
| 7 | API URL: `https://httpbin.org/post` (for testing) | Input accepts | |
| 8 | API Key: "test-key-123" | Input accepts | |
| 9 | Click "Save" | Site created, appears in list | |

### Test 7.2: Edit Site
**URL:** `/sites/{id}/edit`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Click "Edit" on a site | Edit form shows current values | |
| 2 | Change description | Value updates | |
| 3 | Click "Save" | Changes saved | |

### Test 7.3: Deactivate Site
**URL:** `/sites/`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Click "Deactivate" on a site | Site shows as inactive | |
| 2 | Verify inactive sites don't appear in publish dropdown | | |

---

## Phase 8: Publishing

### Test 8.1: Publish Approved Draft
**URL:** `/publish`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Visit `/publish` | Approved drafts and sites show | |
| 2 | Select an approved draft | Selection highlights | |
| 3 | Select a site from dropdown | Selection works | |
| 4 | Click "Publish to Selected Site" | Success/error message | |
| 5 | Check "Recent Publishing History" | Record appears | |

### Test 8.2: Daily Limit
**URL:** `/publish`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Set daily limit to 1 in Settings | Setting saves | |
| 2 | Publish one article | Success | |
| 3 | Try to publish second article | Error: "Daily publish limit reached" | |

---

## Phase 9: Metrics

### Test 9.1: Add Metrics
**URL:** `/metrics`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Visit `/metrics` | Metrics form and table show | |
| 2 | Enter Metric date: today's date | Date picker works | |
| 3 | Enter Indexing rate: 85 | Number input works | |
| 4 | Enter Queries: 1500 | Number input works | |
| 5 | Enter CTR: 3.5 | Number input works | |
| 6 | Enter Avg position: 12.5 | Number input works | |
| 7 | Enter Notes: "Good performance" | Textarea works | |
| 8 | Click "Add Metrics" | Success message, data appears in table | |

---

## Phase 10: Selection Gate

### Test 10.1: Category Locking
**URL:** `/selection`

| Step | Action | Expected | Pass/Fail |
|------|--------|----------|-----------|
| 1 | Visit `/selection` | Category scores show | |
| 2 | Click "Lock" on a category | Category locked message | |
| 3 | Try to create draft from different category | Error: "Candidate outside locked category" | |
| 4 | Click "Unlock" | Lock cleared | |

---

## Automated Tests

Run locally:
```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

Current status: **34 tests passing**

---

## Known Issues & Limitations

| Issue | Description | Workaround |
|-------|-------------|------------|
| Google Trends Rate Limiting | pytrends may be blocked if too many requests | Wait and retry, or use VPN |
| No Authentication | Anyone with URL can access | Add login system (future) |
| No Image Upload | Images must be hosted externally | Use image URLs |
| No Autosave | Must manually save drafts | Click Save frequently |

---

## Improvement Suggestions

| Priority | Area | Suggestion |
|----------|------|------------|
| High | Security | Add authentication/login |
| High | Validation | Add form validation and sanitization |
| Medium | UX | Add autosave for drafts |
| Medium | Automation | Add Vercel Cron for auto-fetching trends |
| Medium | UI | Add loading spinners for slow operations |
| Low | Features | Add bulk operations |
| Low | Features | Add content scheduling |
