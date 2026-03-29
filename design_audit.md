# UI/UX Design Audit — Naija Trend-to-Cash

**URL**: https://naijatrendcash.vercel.app  
**Date**: 2026-03-29  
**Overall Design Rating**: **5.5 / 10** — Clean and functional foundation, but held back by significant layout bugs, a monotone aesthetic, and missing interaction design.

---

## Global Design Patterns

| Aspect | Current State | Verdict |
|--------|---------------|---------|
| **Color palette** | Single brown/orange accent (`#C25E23`) + beige background + white cards | ⚠️ Monotone |
| **Typography** | Sans-serif (system/Inter), bold headings, ALL-CAPS table headers | ✅ Readable |
| **Layout** | Card-based, 2-column grids for forms, full-width tables | ✅ Consistent |
| **Buttons** | Rounded pill with brown fill + white text | ⚠️ One style for everything |
| **Spacing** | ~24px card padding, consistent vertical gaps | ✅ Balanced |
| **Background** | Soft gradient (beige → peach → blue tint at bottom) | ✅ Warm feel |
| **Border radius** | ~12px on cards, ~20px on buttons | ✅ Cohesive |
| **Shadows** | Very subtle card shadows | ⚠️ Almost invisible |

---

## Page-by-Page Analysis

### Dashboard (`/`)

![Dashboard page](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\dashboard_full_1774811566648.png)

| What Works | What Doesn't |
|------------|-------------|
| Stat cards with clear labels/counts | Top row cards (Candidates/Drafts/QC) are **different height** from bottom cards |
| Launch Status badge is informative | "Not locked" badge blends in — easy to miss |
| Latest Metrics table embedded nicely | Cards have **no icons** — just text and numbers, feels flat |
| | Navigation wraps "Settings" to a **second line** |
| | No visual distinction between the 3 count cards and the 2 content cards |

---

### Discover (`/discover`)

![Discover page](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\discover_page_1774811583318.png)

| What Works | What Doesn't |
|------------|-------------|
| Clean 2-column form layout | 4 numeric fields (velocity, safety, intent, evergreen) look identical — no labels explaining what 0.5 means |
| Clear section separation | "Fetch Trends" button feels undersized relative to the form card |
| Page subtitle text is helpful | No loading indicator visible during fetch (only a success banner appears after) |
| | "Explore a Keyword" section below fold is easy to miss |

---

### Trend Monitor (`/trends`)

![Trends page](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\trends_page_1774811598996.png)

| What Works | What Doesn't |
|------------|-------------|
| Dense form covers all scoring fields | "Add Candidate" button is **floated right** and visually detached from the form |
| Filter links below table are functional | Filter links are **unstyled plain text** — no active state, no pill/badge treatment |
| ALL-CAPS headers help scan columns | 8-column table is very wide — "Sources" and "Draft" columns are tiny |
| | Score fields default to 0, no sliders or visual affordance for 0-10 |

---

### Selection Gate (`/selection`)

![Selection Gate](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\selection_gate_1774811614551.png)

| What Works | What Doesn't |
|------------|-------------|
| Rubric weights are displayed transparently | "No category locked yet" is **plain text** — needs an empty-state illustration |
| "Lock Category" buttons are prominent | Avg Score column shows "0.5" for everything — no bar/sparkline visual |
| Clean table layout | No explanation of what "locking" does for first-time users |

---

### Drafts (`/drafts`)

![Drafts list](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\drafts_list_1774811631037.png)

| What Works | What Doesn't |
|------------|-------------|
| Status badge ("approved") with peach background | **Raw ISO timestamp** (`2026-03-29T19:06:08.860328+00:00`) — unreadable |
| Filter links (All / Draft / QC / Approved / Published) | Filter links are **plain underlined text** with no active state indicator |
| Clean single-row table | "Edit" action is a plain text link — easily missed |
| | Empty page below the single row — wasted space |

---

### QC Dashboard (`/qc`)

![QC page](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\quality_control_1774811647267.png)

| What Works | What Doesn't |
|------------|-------------|
| "All checks must pass" instruction is clear | Empty state ("No drafts waiting for QC") is **bare plain text** — no icon or illustration |
| | Page is ~80% empty white space |
| | No visual pipeline/progress indicator showing workflow stage |

---

### Publish (`/publish`)

![Publish page](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\publish_page_1774811666220.png)

| What Works | What Doesn't |
|------------|-------------|
| "Publish to Site" column has inline dropdown + button | Title text is **truncated** (`...Should K...`) with no tooltip |
| Publish History section is informative | "Failed" badge is red but **tiny** — needs more visual weight |
| | **Raw ISO timestamp** again in Publish History |
| | Dropdown + Button crammed into one table cell — feels cluttered |

---

### Sites (`/sites`)

![Sites page](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\sites_management_1774811689688.png)

| What Works | What Doesn't |
|------------|-------------|
| "How to Connect" instructional card is helpful | "Edit" and "Delete" are **outlined pill buttons** — different style from all other buttons in the app |
| Niche badge (green "technology") adds color | "Add New Site" button is at **top-right** — far from the table content it affects |
| Clean table layout | API URL column takes too much horizontal space with long URLs |
| | Slug shown under site name in small text — good data, but low visual hierarchy |

---

### Settings (`/settings`)

![Settings page](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\settings_page_top_1774811711037.png)

| What Works | What Doesn't |
|------------|-------------|
| Helper text under API key field ("Get your key from Google AI Studio") | **Two separate "Save" buttons** for two sections on the same page — confusing |
| Checkbox for auto-fetch is clear | Settings vs Source Fetching split feels arbitrary |
| | No visual grouping (tabs, accordion, or sidebar) for settings categories |
| | "Gemini API Key" field stretches full width — should be shorter for a key input |

---

### Metrics (`/metrics`)

![Metrics page](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\metrics_page_1774811740092.png)

| What Works | What Doesn't |
|------------|-------------|
| Clean 2-column form with clear labels | **No charts or graphs** — metrics page is just a form + table |
| History table is scannable | No trend lines, sparklines, or any data visualization |
| Notes field allows context | Table has no sorting or date range filtering |

---

## Categorized Issues

### 🔴 Critical (Breaks Layout)

| Issue | Location | Details |
|-------|----------|---------|
| **Navigation wrapping** | Global header | "Settings" drops to a second line — breaks the horizontal nav bar on all pages |
| **Raw ISO timestamps** | `/drafts`, `/publish` | `2026-03-29T19:06:08.860328+00:00` displayed to users — unreadable |

### 🟠 High (Degrades UX Significantly)

| Issue | Location | Details |
|-------|----------|---------|
| **No active nav state** | Global header | User can't tell which page they're currently on |
| **Empty states are bare text** | `/qc`, `/selection` | "No drafts waiting for QC" with no icon or CTA — feels broken |
| **No data visualization** | `/metrics`, Dashboard | Metrics page has zero charts despite being a data page |
| **Monotone color palette** | Global | Single brown accent for every button, badge, and interactive element |

### 🟡 Medium (Noticeable Quality Gap)

| Issue | Location | Details |
|-------|----------|---------|
| **Filter links unstyled** | `/drafts`, `/trends` | Plain underlined text — no pill, no active state, no hover feedback |
| **Button style inconsistency** | `/sites` vs everywhere else | Edit/Delete use outlined pills; everything else uses solid fills |
| **Dashboard card sizes uneven** | `/` | Top 3 stat cards vs bottom 2 content cards are visually mismatched |
| **Two Save buttons** | `/settings` | Confusing — should be one unified action |
| **No icons anywhere** | Global | Zero icons in nav, cards, buttons, or tables — pure text |
| **No table row hover** | Global | Tables have no hover highlight — feels static and unresponsive |

### 🟢 Low (Polish Items)

| Issue | Location | Details |
|-------|----------|---------|
| Score inputs lack affordance | `/discover`, `/trends` | 0-10 scores should use sliders or star ratings |
| Title truncation with no tooltip | `/publish` | Truncated text with `...` but no way to see full title |
| Long API URLs in table | `/sites` | URL column eats horizontal space |
| No loading skeletons | Global | Content appears suddenly — no skeleton placeholder animation |

---

## What Works Well ✅

- **Warm, distinctive brand feel** — the beige/brown palette is unique and feels intentional
- **Card-based layout** — consistent container pattern across all pages
- **2-column form grids** — efficient use of space for data entry
- **ALL-CAPS table headers** — good scanability for data tables
- **Rounded corners** — cohesive border-radius across cards and buttons
- **Gradient background** — subtle beige-to-blue adds depth
- **The NTC logo** — square brown logo with white text is simple and memorable
- **Helper text under inputs** — Settings page does this well

---

## What Needs Work ❌

- **Zero interaction feedback** — no hover states, no transitions, no active indicators
- **No micro-animations** — everything is static; no fade-ins, no skeleton loading
- **Pure text UI** — no icons, no illustrations, no visual affordances
- **Single accent color** — brown is used for literally everything interactive
- **Timestamps are raw** — ISO strings shown to users
- **No data visualization** — a metrics page without charts is a missed opportunity
- **Empty states feel broken** — just a line of grey text

---

## Recommended Upgrades (Priority Order)

### 1. Fix Navigation (Critical)
```
- Make nav a proper flexbox row with `flex-wrap: nowrap`
- Add active page indicator (bold text + underline or background pill)
- Consider a sidebar layout for 10+ nav items
- Add icons next to each nav label (📊 Dashboard, 🔍 Discover, etc.)
```

### 2. Format Timestamps (Critical)
```
- Replace ISO strings with human-readable format: "Mar 29, 2026 · 7:06 PM"
- Use relative time for recent items: "2 hours ago"
```

### 3. Add a Secondary Color (High)
```
- Introduce a teal/blue-green accent (#0891B2 or #059669) for:
  - Status badges (approved = green, failed = red, draft = blue)
  - Secondary buttons
  - Links and interactive elements
- Keep brown for primary CTAs and brand identity
```

### 4. Design Proper Empty States (High)
```
- Add an illustration or icon + heading + subtext + CTA button
- Example for QC: 📋 icon + "No drafts in QC" + "Drafts will appear here once moved to review" + "Go to Drafts →"
```

### 5. Add Icons Everywhere (Medium)
```
- Use Lucide or Phosphor icon set
- Nav: Dashboard 📊, Discover 🔍, Drafts 📝, QC ✅, Publish 🚀, Sites 🌐, Settings ⚙️, Metrics 📈
- Buttons: + Add, ✏️ Edit, 🗑️ Delete, 💾 Save
- Stat cards: add a colored icon to each (trending arrow, document, checkmark)
```

### 6. Add Charts to Metrics (Medium)
```
- Line chart for Indexing Rate over time
- Bar chart for Queries volume
- Small sparklines in the dashboard's Latest Metrics card
- Use Chart.js or Recharts
```

### 7. Style Filter Links as Pills (Medium)
```css
.filter-link {
  padding: 6px 16px;
  border-radius: 20px;
  background: #f0f0f0;
  transition: all 0.2s;
}
.filter-link.active {
  background: #C25E23;
  color: white;
}
```

### 8. Add Interaction Feedback (Medium)
```css
/* Table row hover */
tr:hover { background: #fdf6f0; transition: background 0.15s; }

/* Button hover */
button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }

/* Card entrance animation */
.card { animation: fadeInUp 0.3s ease-out; }
```

### 9. Unify Dashboard Cards (Low)
```
- Make all stat cards the same height using CSS Grid with equal rows
- Add a colored left border or icon to differentiate (green for approved, orange for candidates)
- Move "Latest Metrics" into a dedicated sparkline widget
```

### 10. Add Loading Skeletons (Low)
```
- Replace blank → content flash with animated skeleton placeholders
- Pulse animation on grey rectangles matching content layout
- Apply to tables, cards, and form sections
```

---

## Session Recording

![Full design audit browser session](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\ui_audit_dashboard_1774811541307.webp)

---

## Mobile View (375px)

![Mobile responsiveness issues](C:\Users\USER\.gemini\antigravity\brain\78c317d6-a673-48dc-9f8c-c26932c0ed84\mobile_view_1774811290566.png)

**Mobile issues**: Navigation wraps into 3 lines, tables clip right columns, no hamburger menu, forms need stacked layout at narrow widths.
