# Naija Trend-to-Cash Design Specification

## Complete Frontend Design Document

---

# Table of Contents

1. [Overview](#1-overview)
2. [Design System](#2-design-system)
3. [Layout Architecture](#3-layout-architecture)
4. [Component Library](#4-component-library)
5. [Page Specifications](#5-page-specifications)
6. [Responsive Design](#6-responsive-design)
7. [Interaction Patterns](#7-interaction-patterns)
8. [Accessibility Guidelines](#8-accessibility-guidelines)
9. [Animation & Motion](#9-animation--motion)
10. [Iconography](#10-iconography)

---

# 1. Overview

## 1.1 Product Description

**Naija Trend-to-Cash (NTC)** is a Growth Optimization Platform designed to help content-driven websites discover trending topics, generate SEO-optimized content, and track performance metrics.

## 1.2 Target Users

| User Role | Primary Goals |
|-----------|---------------|
| Content Manager | Discover trends, manage content workflow |
| SEO Analyst | Track performance, optimize content |
| Publisher | Review and publish content to multiple sites |
| Administrator | Manage users, sites, settings |

## 1.3 Design Principles

1. **Clarity Over Complexity** - Every element should answer "What do I do next?"
2. **Proactive Intelligence** - Show insights, not just data
3. **Progressive Disclosure** - Essential first, details on demand
4. **Mobile-First** - Design for smallest screen, scale up
5. **Dark-First** - Primary theme is dark mode

## 1.4 Brand Identity

- **Brand Name**: NTC (Naija Trend-to-Cash)
- **Tagline**: From Trends to Traffic
- **Personality**: Intelligent, Efficient, Authoritative, Modern
- **Visual Metaphor**: "The Obsidian Lens" - Looking through layers of polished stone to reveal insights

---

# 2. Design System

## 2.1 Color Palette

### Primary Colors

| Token | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `primary` | `#c65d2a` | `#ffb596` | CTAs, active states, links |
| `primary-container` | `#ffdbcd` | `#e1713d` | Button backgrounds, highlights |
| `on-primary` | `#ffffff` | `#581e00` | Text on primary |

### Secondary Colors

| Token | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `secondary` | `#2d8cf0` | `#fbb79a` | Secondary actions, info |
| `secondary-container` | `#e8f4ff` | `#693a25` | Secondary backgrounds |
| `on-secondary` | `#ffffff` | `#4e2511` | Text on secondary |

### Semantic Colors

| Token | Value | Usage |
|-------|-------|-------|
| `success` | `#059669` | Positive metrics, published status |
| `success-container` | `#d1fae5` | Success backgrounds |
| `warning` | `#D97706` | Draft status, alerts |
| `warning-container` | `#fef3c7` | Warning backgrounds |
| `error` | `#DC2626` | Errors, failed status |
| `error-container` | `#fee2e2` | Error backgrounds |
| `info` | `#0891B2` | Informational elements |
| `info-container` | `#e0f2fe` | Info backgrounds |

### Surface Colors (Dark Theme Primary)

| Token | Value | Usage |
|-------|-------|-------|
| `background` | `#0f131b` | Main app background |
| `surface` | `#0f131b` | Base surface |
| `surface-container-lowest` | `#0a0e15` | Deepest layer |
| `surface-container-low` | `#181c23` | Section wrappers |
| `surface-container` | `#1c2027` | Cards, active elements |
| `surface-container-high` | `#262a32` | Elevated cards |
| `surface-container-highest` | `#31353d` | Highest elevation |
| `surface-bright` | `#353941` | Hover states |
| `surface-variant` | `#31353d` | Glassmorphism base |

### Text Colors

| Token | Value | Usage |
|-------|-------|-------|
| `on-background` | `#dfe2ec` | Primary text |
| `on-surface` | `#dfe2ec` | Text on surfaces |
| `on-surface-variant` | `#ddc1b6` | Secondary text |
| `outline` | `#a58b81` | Borders, dividers |
| `outline-variant` | `#56423a` | Subtle borders |

### Gradient Definitions

```css
/* Primary CTA Gradient */
--gradient-primary: linear-gradient(135deg, #e1713d 0%, #ffb596 100%);

/* Glassmorphism Background */
--gradient-glass: linear-gradient(180deg, rgba(49, 53, 61, 0.6) 0%, rgba(49, 53, 61, 0.4) 100%);

/* Hero Background */
--gradient-hero: radial-gradient(ellipse at top, #1a1a2e 0%, #0f131b 50%);

/* Ambient Glow */
--glow-primary: 0 0 30px rgba(198, 93, 42, 0.15);
--glow-success: 0 0 20px rgba(5, 150, 105, 0.2);
```

## 2.2 Typography

### Font Stack

```css
--font-headline: 'Space Grotesk', sans-serif;
--font-body: 'Inter', sans-serif;
--font-mono: 'JetBrains Mono', monospace;
```

### Type Scale

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| `display-lg` | 56px | 700 | 1.1 | -0.02em | Hero metrics |
| `display-md` | 48px | 700 | 1.1 | -0.02em | Page titles |
| `headline-lg` | 32px | 600 | 1.2 | -0.01em | Section headers |
| `headline-md` | 24px | 600 | 1.3 | 0 | Card titles |
| `headline-sm` | 20px | 600 | 1.3 | 0 | Subsection headers |
| `title-lg` | 18px | 600 | 1.4 | 0 | List item titles |
| `title-md` | 16px | 600 | 1.4 | 0 | Button text, labels |
| `title-sm` | 14px | 600 | 1.4 | 0 | Small labels |
| `body-lg` | 16px | 400 | 1.5 | 0 | Primary body text |
| `body-md` | 14px | 400 | 1.5 | 0 | Secondary body text |
| `body-sm` | 12px | 400 | 1.5 | 0 | Captions, meta |
| `label-lg` | 14px | 600 | 1.4 | 0.05em | Form labels |
| `label-md` | 12px | 600 | 1.4 | 0.05em | Tags, chips |
| `label-sm` | 10px | 600 | 1.4 | 0.1em | Micro labels |

## 2.3 Spacing Scale

Based on 8px grid system:

| Token | Value | Usage |
|-------|-------|-------|
| `space-0` | 0 | No spacing |
| `space-1` | 4px | Tight spacing (icons) |
| `space-2` | 8px | Default gap |
| `space-3` | 12px | Medium gap |
| `space-4` | 16px | Section gap |
| `space-5` | 20px | Card internal gap |
| `space-6` | 24px | Card padding |
| `space-7` | 28px | Section padding |
| `space-8` | 32px | Large section gap |
| `space-9` | 36px | Page margins |
| `space-10` | 40px | Component separation |
| `space-12` | 48px | Section separation |
| `space-16` | 64px | Major sections |
| `space-20` | 80px | Page sections |

## 2.4 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-none` | 0 | Sharp corners |
| `radius-sm` | 4px | Chips, small elements |
| `radius-md` | 8px | Buttons, inputs |
| `radius-lg` | 12px | Cards |
| `radius-xl` | 16px | Large cards, modals |
| `radius-2xl` | 24px | Hero cards |
| `radius-full` | 9999px | Pills, avatars |

## 2.5 Elevation & Shadows

### Tonal Elevation (Dark Theme)

Instead of traditional shadows, use tonal stepping:

| Level | Background Color | Usage |
|-------|------------------|-------|
| 0 | `surface` (#0f131b) | Main canvas |
| 1 | `surface-container-low` (#181c23) | Section wrappers |
| 2 | `surface-container` (#1c2027) | Cards, inputs |
| 3 | `surface-container-high` (#262a32) | Elevated cards, dropdowns |
| 4 | `surface-container-highest` (#31353d) | Modals, popovers |

### Ghost Shadows

```css
/* Subtle lift shadow */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);

/* Card shadow */
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);

/* Floating element shadow */
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);

/* Modal shadow */
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.6);

/* Ghost glow (for glassmorphism) */
--shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.3);
```

## 2.6 Glassmorphism Effects

```css
.glass-card {
  background: rgba(49, 53, 61, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.glass-card-elevated {
  background: rgba(49, 53, 61, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

---

# 3. Layout Architecture

## 3.1 App Shell Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        APP SHELL                                │
├────────────┬────────────────────────────────────────────────────┤
│            │                    HEADER                           │
│   LEFT     │  ┌─────────────────────────────────────────────┐   │
│  SIDEBAR   │  │ Page Title │ Search │ Notifications │ User  │   │
│            │  └─────────────────────────────────────────────┘   │
│  ┌──────┐  ├────────────────────────────────────────────────────┤
│  │ Logo │  │                                                    │
│  ├──────┤  │                                                    │
│  │ Nav  │  │                 MAIN CONTENT                       │
│  │      │  │                                                    │
│  │      │  │                 (Scrollable)                       │
│  │      │  │                                                    │
│  ├──────┤  │                                                    │
│  │User  │  │                                                    │
│  └──────┘  │                                                    │
└────────────┴────────────────────────────────────────────────────┘
```

## 3.2 Sidebar Specifications

### Desktop Sidebar (>= 1024px)

```
Width: 240px (collapsed: 72px)
Position: Fixed left
Height: 100vh
Background: surface-container-low
Border-right: 1px solid outline-variant (10% opacity)
```

### Sidebar Components

```
┌─────────────────────────┐
│        LOGO AREA        │  Height: 64px
│    [Icon] NTC          │  Padding: 16px
├─────────────────────────┤
│                         │
│     NAVIGATION          │  Flex-grow: 1
│                         │
│  ┌───────────────────┐  │
│  │ ● Dashboard       │  │  Active state
│  │   Discover        │  │  - Background: primary (10%)
│  │   Create          │  │  - Left border: 3px primary
│  │   Manage          │  │  - Text: primary
│  │   Analyze         │  │
│  │   Settings        │  │  Inactive state
│  └───────────────────┘  │  - Text: on-surface-variant
│                         │  - Hover: surface-bright
├─────────────────────────┤
│      USER SECTION       │  Height: 80px
│  [Avatar] Name         │  Padding: 16px
│  Plan badge            │
└─────────────────────────┘
```

### Navigation Items

| Icon | Label | Route | Badge? |
|------|-------|-------|--------|
| `dashboard` | Dashboard | `/` | - |
| `explore` | Discover | `/discover` | New trends count |
| `add_circle` | Create | `/create` | Drafts count |
| `layers` | Manage | `/manage` | Pending count |
| `monitoring` | Analyze | `/analyze` | - |
| `settings` | Settings | `/settings` | - |

## 3.3 Header Specifications

### Desktop Header

```
Height: 64px
Position: Sticky top
Background: surface (with blur)
Border-bottom: 1px solid outline-variant (10% opacity)
Backdrop-filter: blur(12px)
```

### Header Layout

```
┌──────────────────────────────────────────────────────────────────┐
│ Page Title    │    SEARCH BAR     │  Notifications │ Avatar     │
│ (24px)        │    (360px)        │    (40px)      │  (40px)    │
│               │                   │                │            │
│ align-left    │    centered       │   align-right  │ 16px gap   │
└──────────────────────────────────────────────────────────────────┘
```

## 3.4 Content Area Specifications

```
Padding: 32px (desktop), 24px (tablet), 16px (mobile)
Max-width: 1440px (content container)
Margin: 0 auto (centered)
```

### Grid System

```css
.content-grid {
  display: grid;
  gap: 24px;
}

/* 2-column layout */
.grid-2-col {
  grid-template-columns: 1fr 1fr;
}

/* 3-column layout */
.grid-3-col {
  grid-template-columns: repeat(3, 1fr);
}

/* 4-column layout (KPI cards) */
.grid-4-col {
  grid-template-columns: repeat(4, 1fr);
}

/* 60-40 split */
.grid-60-40 {
  grid-template-columns: 1.5fr 1fr;
}

/* 70-30 split */
.grid-70-30 {
  grid-template-columns: 2fr 1fr;
}
```

## 3.5 Responsive Breakpoints

| Breakpoint | Width | Sidebar | Header | Grid |
|------------|-------|---------|--------|------|
| Mobile S | 320px | Hidden (hamburger) | Compact | 1 column |
| Mobile L | 425px | Hidden (hamburger) | Compact | 1 column |
| Tablet | 768px | Hidden (overlay) | Full | 2 columns |
| Laptop | 1024px | Collapsed (72px) | Full | 3 columns |
| Desktop | 1280px | Full (240px) | Full | 4 columns |
| Large | 1536px+ | Full (240px) | Full | 4 columns max |

---

# 4. Component Library

## 4.1 Buttons

### Button Variants

```css
/* Primary Button */
.btn-primary {
  background: linear-gradient(135deg, #e1713d 0%, #c65d2a 100%);
  color: #ffffff;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s ease;
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(198, 93, 42, 0.3);
}

/* Secondary Button */
.btn-secondary {
  background: rgba(49, 53, 61, 0.4);
  color: #dfe2ec;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 24px;
  border-radius: 8px;
}
.btn-secondary:hover {
  background: rgba(49, 53, 61, 0.6);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Ghost Button */
.btn-ghost {
  background: transparent;
  color: #ffb596;
  padding: 12px 24px;
}
.btn-ghost:hover {
  background: rgba(198, 93, 42, 0.1);
}

/* Icon Button */
.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### Button Sizes

| Size | Height | Padding | Font Size |
|------|--------|---------|-----------|
| Small | 32px | 8px 16px | 12px |
| Medium | 40px | 12px 20px | 14px |
| Large | 48px | 16px 32px | 16px |

## 4.2 Cards

### Standard Card

```css
.card {
  background: #1c2027;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #dfe2ec;
}
.card-subtitle {
  font-size: 14px;
  color: #ddc1b6;
}
```

### Glass Card

```css
.card-glass {
  background: rgba(49, 53, 61, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
}
```

### Stat Card (KPI)

```css
.card-stat {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card-stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #dfe2ec;
}
.card-stat-label {
  font-size: 14px;
  color: #ddc1b6;
}
.card-stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.card-stat-trend.positive { color: #059669; }
.card-stat-trend.negative { color: #DC2626; }
```

## 4.3 Form Elements

### Text Input

```css
.input {
  background: #262a32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px 16px;
  color: #dfe2ec;
  font-size: 14px;
  width: 100%;
}
.input:focus {
  border-color: #c65d2a;
  outline: none;
  box-shadow: 0 0 0 3px rgba(198, 93, 42, 0.2);
}
.input::placeholder {
  color: #6b7280;
}
```

### Select Dropdown

```css
.select {
  background: #262a32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px 40px 12px 16px;
  color: #dfe2ec;
  appearance: none;
  background-image: url('chevron-down.svg');
  background-repeat: no-repeat;
  background-position: right 12px center;
}
```

### Checkbox

```css
.checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: transparent;
}
.checkbox:checked {
  background: #c65d2a;
  border-color: #c65d2a;
}
```

### Toggle Switch

```css
.toggle {
  width: 48px;
  height: 28px;
  border-radius: 14px;
  background: #31353d;
  position: relative;
}
.toggle::after {
  content: '';
  width: 22px;
  height: 22px;
  border-radius: 11px;
  background: #dfe2ec;
  position: absolute;
  top: 3px;
  left: 3px;
  transition: transform 0.2s ease;
}
.toggle.active {
  background: #c65d2a;
}
.toggle.active::after {
  transform: translateX(20px);
}
```

## 4.4 Data Display

### Tables

```css
.table-container {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  background: #1c2027;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #ddc1b6;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.table td {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: #dfe2ec;
}

.table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.table tr:last-child td {
  border-bottom: none;
}
```

### Status Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.badge-success {
  background: rgba(5, 150, 105, 0.2);
  color: #34d399;
}

.badge-warning {
  background: rgba(217, 119, 6, 0.2);
  color: #fbbf24;
}

.badge-error {
  background: rgba(220, 38, 38, 0.2);
  color: #f87171;
}

.badge-info {
  background: rgba(8, 145, 178, 0.2);
  color: #22d3ee;
}

.badge-neutral {
  background: rgba(107, 114, 128, 0.2);
  color: #9ca3af;
}
```

### Chips/Tags

```css
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  background: rgba(49, 53, 61, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #dfe2ec;
}

.chip-primary {
  background: rgba(198, 93, 42, 0.2);
  border-color: rgba(198, 93, 42, 0.3);
  color: #ffb596;
}

.chip-removable {
  padding-right: 8px;
}
.chip-remove {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}
```

## 4.5 Navigation Components

### Breadcrumbs

```css
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.breadcrumb-item {
  color: #ddc1b6;
}
.breadcrumb-item:hover {
  color: #ffb596;
}
.breadcrumb-separator {
  color: #6b7280;
}
.breadcrumb-current {
  color: #dfe2ec;
}
```

### Tabs

```css
.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.tab {
  padding: 12px 20px;
  color: #ddc1b6;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.tab:hover {
  color: #dfe2ec;
}
.tab.active {
  color: #ffb596;
  border-bottom-color: #c65d2a;
}
```

### Pagination

```css
.pagination {
  display: flex;
  align-items: center;
  gap: 8px;
}
.pagination-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: #ddc1b6;
}
.pagination-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}
.pagination-btn.active {
  background: #c65d2a;
  color: #ffffff;
}
.pagination-ellipsis {
  color: #6b7280;
}
```

## 4.6 Feedback Components

### Toast Notifications

```css
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  animation: slideIn 0.3s ease;
}

.toast-success {
  background: rgba(5, 150, 105, 0.9);
  color: #ffffff;
}

.toast-error {
  background: rgba(220, 38, 38, 0.9);
  color: #ffffff;
}

.toast-warning {
  background: rgba(217, 119, 6, 0.9);
  color: #ffffff;
}

.toast-info {
  background: rgba(8, 145, 178, 0.9);
  color: #ffffff;
}
```

### Modals

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #1c2027;
  border-radius: 16px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
```

### Loading States

```css
/* Spinner */
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #c65d2a;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Skeleton */
.skeleton {
  background: linear-gradient(90deg, #1c2027 25%, #262a32 50%, #1c2027 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

## 4.7 Empty States

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  text-align: center;
}

.empty-state-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  color: #6b7280;
}

.empty-state-title {
  font-size: 20px;
  font-weight: 600;
  color: #dfe2ec;
  margin-bottom: 8px;
}

.empty-state-description {
  font-size: 14px;
  color: #ddc1b6;
  margin-bottom: 24px;
  max-width: 320px;
}
```

---

# 5. Page Specifications

## 5.1 Dashboard (Home Page)

**Route**: `/`

**Purpose**: Overview of key metrics, quick actions, and recent activity.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Dashboard │ [Search...] │ [🔔] [Avatar]                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │Trends Found  │ │Drafts        │ │Published     │ │Traffic       ││
│  │    1,284     │ │    42        │ │    156       │ │   842.5K     ││
│  │  ↑ 12%       │ │  ✏️ Edit     │ │  ✓ 94%       │ │  📊 High     ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘│
│                                                                     │
│  ┌─────────────────────────────────┐ ┌─────────────────────────────┐│
│  │ TRENDING TOPICS                 │ │ QUICK ACTIONS               ││
│  │ ──────────────────────────────  │ │ ─────────────────────────   ││
│  │ [All] [Sports] [Tech] [Finance] │ │ [+ New Draft]               ││
│  │                                 │ │ [🔗 Connect API]             ││
│  │ ┌─────────────────────────────┐ │ │ [🔍 Deep Scan]              ││
│  │ │ Topic        │ Vol │ Status │ │ │ [📤 Sync Hub]               ││
│  │ ├─────────────────────────────┤ │ │                             ││
│  │ │ Lagos Fintech│42.8K│ Rising │ │ │ RECENT ACTIVITY             ││
│  │ │ Afrobeats    │128K │ Viral  │ │ │ ─────────────────────────   ││
│  │ │ Naira Rate   │12.2K│ Steady │ │ │ • Published "Top 10..."     ││
│  │ │ Tech Talent  │35.9K│ Rising │ │ │ • New trend #ZazuuVibe      ││
│  │ └─────────────────────────────┘ │ │ • Aisha edited draft        ││
│  │                                 │ │ • API limit reached         ││
│  │ [View All Trends →]             │ │ [View All Activity →]       ││
│  └─────────────────────────────────┘ └─────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Components

| Section | Component | Data Source |
|---------|-----------|-------------|
| KPI Cards | `StatCard` x 4 | `/api/metrics/summary` |
| Trending Topics | `DataTable` with filters | `/api/trends?limit=5` |
| Quick Actions | `ActionCard` with buttons | Static |
| Recent Activity | `ActivityList` | `/api/activity?limit=5` |

### States

- **Loading**: Skeleton cards and table rows
- **Empty**: Illustration + "No trends yet" + CTA to discover
- **Error**: Error message + Retry button

---

## 5.2 Trend Discovery Page

**Route**: `/discover`

**Purpose**: Search and discover trending topics with filters and analysis.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Discover │ [Search trends...] │ [🔔] [Avatar]               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ SEARCH & FILTERS                                                ││
│  │ ┌─────────────────────────────────────────┐ ┌────────────────┐  ││
│  │ │ 🔍 Search trends...                     │ │ [Scan Trends]  │  ││
│  │ └─────────────────────────────────────────┘ └────────────────┘  ││
│  │                                                                 ││
│  │ Category: [All ▼]  Region: [Nigeria ▼]  Time: [Last 7 days ▼]  ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ RESULTS (156 trends)                           [Grid] [List]    ││
│  │ ─────────────────────────────────────────────────────────────── ││
│  │                                                                 ││
│  │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    ││
│  │ │ 🔥 Viral        │ │ 📈 Rising       │ │ ⚡ Steady       │    ││
│  │ │ #ZazuuVibe      │ │ Lagos Tech Week │ │ Naira Exchange  │    ││
│  │ │ 284K searches   │ │ 45.2K searches  │ │ 12.1K searches  │    ││
│  │ │ +340% ↑        │ │ +89% ↑         │ │ +5% ↑          │    ││
│  │ │ [Create Draft]  │ │ [Create Draft]  │ │ [Create Draft]  │    ││
│  │ └─────────────────┘ └─────────────────┘ └─────────────────┘    ││
│  │                                                                 ││
│  │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    ││
│  │ │ 📈 Rising       │ │ 🔥 Viral        │ │ 📈 Rising       │    ││
│  │ │ Afrobeats Tour  │ │ Premier League  │ │ Job Search NG   │    ││
│  │ │ 128K searches   │ │ 562K searches   │ │ 38.5K searches  │    ││
│  │ │ +156% ↑        │ │ +520% ↑        │ │ +45% ↑         │    ││
│  │ └─────────────────┘ └─────────────────┘ └─────────────────┘    ││
│  │                                                                 ││
│  │ [Load More]                                                    ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| `SearchBar` | Large search input with scan button |
| `FilterChips` | Category, Region, Time range filters |
| `TrendCard` | Grid card showing trend details |
| `TrendTable` | Alternative list view |
| `ViewToggle` | Grid/List view switcher |

### Filter Options

| Filter | Options |
|--------|---------|
| Category | All, Sports, Tech, Finance, Entertainment, Politics, Health |
| Region | Nigeria, Ghana, Kenya, South Africa, Global |
| Time Range | Last 24h, Last 7 days, Last 30 days, Last 90 days |
| Status | All, Viral, Rising, Steady, Declining |

---

## 5.3 Content Creator Page

**Route**: `/create`

**Purpose**: Generate and edit AI-powered content from trends.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Create │ [Search...] │ [🔔] [Avatar]                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────┐ ┌───────────────────────────────┐│
│  │ CONTENT GENERATOR             │ │ PREVIEW                       ││
│  │ ─────────────────────────────│ │ ─────────────────────────────  ││
│  │                               │ │                               ││
│  │ Source:                       │ │ ┌───────────────────────────┐ ││
│  │ [Select Trend ▼]              │ │ │                           │ ││
│  │                               │ │ │   Article Preview         │ ││
│  │ Title:                        │ │ │                           │ ││
│  │ [________________________]    │ │ │   Title: "Top 10 Tech..." │ ││
│  │                               │ │ │                           │ ││
│  │ Tone: [Informative ▼]         │ │ │   Meta: 156 words         │ ││
│  │ Length: [Medium ▼]            │ │ │                           │ ││
│  │                               │ │ │   [Full Preview]          │ ││
│  │ Target Site:                  │ │ │                           │ ││
│  │ [Select Site ▼]               │ │ └───────────────────────────┘ ││
│  │                               │ │                               ││
│  │ Category:                     │ │ SEO SCORE: 85/100            ││
│  │ [Select Category ▼]           │ │ ████████░░ Good              ││
│  │                               │ │                               ││
│  │ Additional Instructions:      │ │ KEYWORDS:                     ││
│  │ [________________________]    │ │ tech, nigeria, startups...   ││
│  │ [________________________]    │ │                               ││
│  │                               │ │ READABILITY: Grade 8          ││
│  │ [🤖 Generate Content]         │ │                               ││
│  │                               │ │                               ││
│  └───────────────────────────────┘ └───────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ CONTENT EDITOR                                                  ││
│  │ ─────────────────────────────────────────────────────────────── ││
│  │ [Bold] [Italic] [H1] [H2] [Link] [Image] [List] [Quote]         ││
│  │ ─────────────────────────────────────────────────────────────── ││
│  │                                                                 ││
│  │ # Top 10 Tech Hubs in Nigeria: 2024 Guide                       ││
│  │                                                                 ││
│  │ Nigeria's tech ecosystem has experienced unprecedented...       ││
│  │                                                                 ││
│  │ ## 1. Lagos - The Silicon Valley of Africa                      ││
│  │                                                                 ││
│  │ Lagos remains the undisputed leader in Nigeria's tech...        ││
│  │                                                                 ││
│  │ [Save Draft] [Save & Continue]                                  ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| `ContentGenerator` | Form for AI content generation |
| `TrendSelector` | Dropdown to select source trend |
| `ToneSelector` | Tone options (Informative, Casual, Professional) |
| `LengthSelector` | Word count options (Short: 300, Medium: 600, Long: 1200) |
| `PreviewPanel` | Live preview of generated content |
| `SEOScoreCard` | SEO analysis score and suggestions |
| `RichTextEditor` | TinyMCE or similar WYSIWYG editor |

---

## 5.4 Content Manager Page

**Route**: `/manage`

**Purpose**: Manage content workflow from draft to published.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Manage │ [Search content...] │ [🔔] [Avatar]               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ [All] [Drafts (42)] [In Review (8)] [QC Queue (5)] [Published]  ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ CONTENT TABLE                                                   ││
│  │ ─────────────────────────────────────────────────────────────── ││
│  │ ☐ │ Title              │ Status    │ Site      │ Date    │ Acts ││
│  │───┼────────────────────┼───────────┼───────────┼─────────┼────── ││
│  │ ☐ │ Top 10 Tech Hubs   │ Draft     │ Blog A    │ Today   │ ⋮    ││
│  │ ☐ │ Afrobeats Tour     │ In Review │ Blog B    │ Today   │ ⋮    ││
│  │ ☐ │ Naira Analysis     │ QC Queue  │ Blog A    │ Yesterday│ ⋮   ││
│  │ ☐ │ Premier League     │ Published │ Blog C    │ Mar 28  │ ⋮    ││
│  │ ☐ │ Fintech Summit     │ Draft     │ -         │ Mar 27  │ ⋮    ││
│  │ ☐ │ Job Market Guide   │ Published │ Blog A    │ Mar 26  │ ⋮    ││
│  │                                                                 ││
│  │ ☐ Select All    [Bulk Actions ▼]          ← 1 2 3 ... 10 →    ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Tabs

| Tab | Description | Badge Color |
|-----|-------------|-------------|
| All | All content | None |
| Drafts | Content in draft state | Warning (amber) |
| In Review | Awaiting review | Info (cyan) |
| QC Queue | Quality check pending | Warning (amber) |
| Published | Live content | Success (green) |

### Bulk Actions

- Assign to reviewer
- Change status
- Move to site
- Delete
- Export

---

## 5.5 Sites Manager Page

**Route**: `/manage/sites`

**Purpose**: Manage connected websites and publishing destinations.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Sites │ [Search...] │ [🔔] [Avatar]                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ CONNECTED SITES                                    [+ Add Site] ││
│  │ ─────────────────────────────────────────────────────────────── ││
│  │                                                                 ││
│  │ ┌─────────────────────────────────────────────────────────────┐ ││
│  │ │ 🌐 mybettingtips.com                         ● Connected     │ ││
│  │ │ WordPress • 156 articles • Last sync: 2 mins ago            │ ││
│  │ │ ────────────────────────────────────────────────────────────│ ││
│  │ │ Categories: Tips, News, Predictions, Reviews                │ ││
│  │ │ [Sync Now] [Configure] [Disconnect]                          │ ││
│  │ └─────────────────────────────────────────────────────────────┘ ││
│  │                                                                 ││
│  │ ┌─────────────────────────────────────────────────────────────┐ ││
│  │ │ 🌐 technews.ng                               ● Connected     │ ││
│  │ │ WordPress • 89 articles • Last sync: 1 hour ago             │ ││
│  │ │ ────────────────────────────────────────────────────────────│ ││
│  │ │ Categories: Tech, Startups, Gadgets, AI                     │ ││
│  │ │ [Sync Now] [Configure] [Disconnect]                          │ ││
│  │ └─────────────────────────────────────────────────────────────┘ ││
│  │                                                                 ││
│  │ ┌─────────────────────────────────────────────────────────────┐ ││
│  │ │ 🌐 entertainmenthub.com                      ○ Disconnected  │ ││
│  │ │ Ghost • 45 articles • Last sync: 3 days ago                 │ ││
│  │ │ ────────────────────────────────────────────────────────────│ ││
│  │ │ Categories: Music, Movies, Celebrities                      │ ││
│  │ │ [Reconnect] [Configure] [Remove]                             │ ││
│  │ └─────────────────────────────────────────────────────────────┘ ││
│  │                                                                 ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Add Site Modal

```
┌─────────────────────────────────────────────────────────────────────┐
│ Add New Site                                               [✕]     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Platform:  [WordPress ▼]                                          │
│                                                                     │
│  Site URL:  [https://________________]                              │
│                                                                     │
│  API Key:   [••••••••••••••••••••••]  [Test Connection]             │
│                                                                     │
│  Site Name: [________________________]                              │
│                                                                     │
│  Categories to sync:                                                │
│  ☑ Tips  ☑ News  ☐ Reviews  ☐ Analysis                            │
│                                                                     │
│                                    [Cancel]  [Add Site]             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5.6 Source Packs Page

**Route**: `/manage/source-packs`

**Purpose**: Manage collections of trends for content generation.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Source Packs │ [Search...] │ [🔔] [Avatar]                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ SOURCE PACKS                                    [+ Create Pack] ││
│  │ ─────────────────────────────────────────────────────────────── ││
│  │                                                                 ││
│  │ ┌─────────────────────┐ ┌─────────────────────┐                ││
│  │ │ 📦 Betting Tips     │ │ 📦 Tech News        │                ││
│  │ │ 24 trends           │ │ 18 trends           │                ││
│  │ │ Updated 2h ago      │ │ Updated 1d ago      │                ││
│  │ │ ─────────────────── │ │ ─────────────────── │                ││
│  │ │ 🏈 Sports x12       │ │ 💻 Tech x10         │                ││
│  │ │ 💰 Finance x8       │ │ 🚀 Startups x5      │                ││
│  │ │ ⚽ Football x4      │ │ 🤖 AI x3            │                ││
│  │ │                     │ │                     │                ││
│  │ │ [Open] [Generate]   │ │ [Open] [Generate]   │                ││
│  │ └─────────────────────┘ └─────────────────────┘                ││
│  │                                                                 ││
│  │ ┌─────────────────────┐ ┌─────────────────────┐                ││
│  │ │ 📦 Entertainment    │ │ 📦 Financial News   │                ││
│  │ │ 32 trends           │ │ 15 trends           │                ││
│  │ │ Updated 3h ago      │ │ Updated 6h ago      │                ││
│  │ │ ─────────────────── │ │ ─────────────────── │                ││
│  │ │ 🎵 Music x15        │ │ 📈 Markets x8       │                ││
│  │ │ 🎬 Movies x10       │ │ 💱 Forex x4         │                ││
│  │ │ ⭐ Celebs x7        │ │ 🏦 Banking x3       │                ││
│  │ │                     │ │                     │                ││
│  │ │ [Open] [Generate]   │ │ [Open] [Generate]   │                ││
│  │ └─────────────────────┘ └─────────────────────┘                ││
│  │                                                                 ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Source Pack Detail View

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Source Pack / Betting Tips │ [🔔] [Avatar]                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ 📦 Betting Tips Pack                                            ││
│  │ 24 trends • Updated 2 hours ago • Created Mar 15, 2024         ││
│  │                                                                 ││
│  │ [Edit Pack] [Add Trends] [Generate All]                         ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ TRENDS IN THIS PACK                              24 trends      ││
│  │ ─────────────────────────────────────────────────────────────── ││
│  │                                                                 ││
│  │ ☐ │ Trend              │ Category │ Volume │ Status    │ Acts   ││
│  │───┼────────────────────┼──────────┼────────┼───────────┼─────── ││
│  │ ☐ │ Premier League     │ Sports   │ 562K   │ Viral     │ [⚙️]   ││
│  │ ☐ │ Champions League   │ Sports   │ 324K   │ Rising    │ [⚙️]   ││
│  │ ☐ │ Bet9ja Tips        │ Betting  │ 89K    │ Steady    │ [⚙️]   ││
│  │ ☐ │ NairaBet Bonus     │ Betting  │ 45K    │ Rising    │ [⚙️]   ││
│  │ ☐ │ La Liga Results    │ Sports   │ 128K   │ Steady    │ [⚙️]   ││
│  │                                                                 ││
│  │ [Remove Selected] [Generate Drafts]                             ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5.7 Analytics Page

**Route**: `/analyze`

**Purpose**: View performance metrics, traffic data, and content analytics.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Analyze │ [Search...] │ [🔔] [Avatar]                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Date Range: [Last 30 days ▼]    Site: [All Sites ▼]            ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │ Page Views   │ │ Visitors     │ │ Avg Time     │ │ Bounce Rate  ││
│  │   125.4K     │ │   42.8K      │ │   3m 42s     │ │   34.2%      ││
│  │  ↑ 23%       │ │  ↑ 18%       │ │  ↑ 12%       │ │  ↓ 5%        ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ TRAFFIC OVERVIEW                                                ││
│  │ ─────────────────────────────────────────────────────────────── ││
│  │                                                                 ││
│  │     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                    ││
│  │   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                  ││
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                 ││
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                               ││
│  │ Mon Tue Wed Thu Fri Sat Sun                                     ││
│  │                                                                 ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────────┐ ┌─────────────────────────────────┐│
│  │ TOP PERFORMING CONTENT      │ │ TRAFFIC SOURCES                 ││
│  │ ─────────────────────────── │ │ ─────────────────────────────── ││
│  │ 1. Premier League Tips      │ │ 🔍 Organic Search    62%        ││
│  │    12.4K views • 3m avg     │ │ 🔗 Direct            18%        ││
│  │                             │ │ 📱 Social            12%        ││
│  │ 2. NairaBet Bonus Guide     │ │ 📧 Referral          8%         ││
│  │    8.2K views • 4m avg      │ │                                 ││
│  │                             │ │                                 ││
│  │ 3. Tech Hubs Nigeria        │ │                                 ││
│  │    6.1K views • 2m avg      │ │                                 ││
│  │                             │ │                                 ││
│  │ [View All Content →]        │ │                                 ││
│  └─────────────────────────────┘ └─────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Analytics Sections

| Section | Description |
|---------|-------------|
| Overview Metrics | KPI cards with trends |
| Traffic Chart | Line/area chart over time |
| Top Content | Table of best performers |
| Traffic Sources | Donut/pie chart |
| Geographic Distribution | Map or country breakdown |
| Device Breakdown | Desktop/Mobile/Tablet |

---

## 5.8 Settings Page

**Route**: `/settings`

**Purpose**: Configure app settings, API keys, and user preferences.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Settings │ [Search...] │ [🔔] [Avatar]                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────┐ ┌──────────────────────────────────────────────────┐│
│  │            │ │ PROFILE                                          ││
│  │ PROFILE    │ │ ────────────────────────────────────────────────│ │
│  │ API Keys   │ │                                                   ││
│  │ Sites      │ │ Name:        [Tunde Adebayo_________________]    ││
│  │ Content    │ │ Email:       [tunde@example.com_____________]    ││
│  │ Notifications│ │ Timezone:    [Africa/Lagos ▼]                  ││
│  │ Appearance │ │                                                   ││
│  │ Billing    │ │ [Save Changes]                                    ││
│  │            │ │                                                   ││
│  │            │ ├──────────────────────────────────────────────────┤ │
│  │            │ │ API KEYS                                         ││
│  │            │ │ ────────────────────────────────────────────────│ │
│  │            │ │                                                   ││
│  │            │ │ Gemini API Key                                    ││
│  │            │ │ [••••••••••••••••••••••••] [Show] [Test]         ││
│  │            │ │ Status: ● Connected                               ││
│  │            │ │                                                   ││
│  │            │ │ Google Trends API                                 ││
│  │            │ │ [••••••••••••••••••••••••] [Show] [Test]         ││
│  │            │ │ Status: ● Connected                               ││
│  │            │ │                                                   ││
│  │            │ │ [+ Add API Key]                                   ││
│  │            │ │                                                   ││
│  └────────────┘ └──────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Settings Sections

| Section | Contents |
|---------|----------|
| Profile | Name, email, timezone, avatar |
| API Keys | Gemini, Google Trends, WordPress, etc. |
| Sites | Default site, publishing preferences |
| Content | Default tone, length, categories |
| Notifications | Email, push notification preferences |
| Appearance | Theme (dark/light), density, sidebar collapsed |
| Billing | Plan details, usage limits, upgrade |

---

## 5.9 Authentication Pages

### Login Page

**Route**: `/login`

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                     ┌─────────────────────┐                        │
│                     │                     │                        │
│                     │         NTC         │                        │
│                     │   Trend-to-Cash     │                        │
│                     │                     │                        │
│                     │ ───────────────────│                        │
│                     │                     │                        │
│                     │ Email:              │                        │
│                     │ [_________________]│                        │
│                     │                     │                        │
│                     │ Password:           │                        │
│                     │ [_________________]│                        │
│                     │                     │                        │
│                     │ ☐ Remember me       │                        │
│                     │                     │                        │
│                     │ [   Sign In    ]    │                        │
│                     │                     │                        │
│                     │ Forgot password?    │                        │
│                     │                     │                        │
│                     └─────────────────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Register Page

**Route**: `/register`

Similar layout with:
- Name field
- Email field
- Password field
- Confirm password field
- Terms checkbox
- Sign up button
- "Already have an account?" link

### Forgot Password Page

**Route**: `/forgot-password`

- Email input
- Submit button
- Back to login link

---

## 5.10 Error Pages

### 404 Not Found

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                         ┌───────────────┐                          │
│                         │               │                          │
│                         │      404      │                          │
│                         │               │                          │
│                         │  Page Not     │                          │
│                         │    Found      │                          │
│                         │               │                          │
│                         │  The page you │                          │
│                         │  are looking  │                          │
│                         │  for doesn't  │                          │
│                         │   exist.      │                          │
│                         │               │                          │
│                         │ [Go Home]     │                          │
│                         │               │                          │
│                         └───────────────┘                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 500 Server Error

Similar layout with:
- 500 illustration
- "Something went wrong" message
- Retry button
- Contact support link

---

# 6. Responsive Design

## 6.1 Breakpoint Definitions

```css
/* Mobile First Approach */
$breakpoint-xs: 320px;  /* Mobile S */
$breakpoint-sm: 425px;  /* Mobile L */
$breakpoint-md: 768px;  /* Tablet */
$breakpoint-lg: 1024px; /* Laptop */
$breakpoint-xl: 1280px; /* Desktop */
$breakpoint-2xl: 1536px; /* Large */

/* Media Queries */
@mixin mobile {
  @media (max-width: #{$breakpoint-md - 1px}) { @content; }
}

@mixin tablet {
  @media (min-width: #{$breakpoint-md}) and (max-width: #{$breakpoint-lg - 1px}) { @content; }
}

@mixin desktop {
  @media (min-width: #{$breakpoint-lg}) { @content; }
}

@mixin large {
  @media (min-width: #{$breakpoint-xl}) { @content; }
}
```

## 6.2 Component Responsiveness

### Sidebar

| Breakpoint | Behavior |
|------------|----------|
| Mobile | Hidden, accessible via hamburger menu |
| Tablet | Hidden, overlay when opened |
| Laptop | Collapsed (72px), icons only |
| Desktop | Full width (240px), with labels |

### Header

| Breakpoint | Behavior |
|------------|----------|
| Mobile | Title + hamburger + avatar only |
| Tablet | Title + search icon + avatar |
| Laptop+ | Full header with search bar |

### KPI Cards

| Breakpoint | Layout |
|------------|--------|
| Mobile | 1 column, stacked |
| Tablet | 2 columns |
| Laptop | 4 columns |
| Desktop | 4 columns |

### Tables

| Breakpoint | Behavior |
|------------|----------|
| Mobile | Transform to cards |
| Tablet | Horizontal scroll |
| Desktop | Full table |

### Mobile Card Transform for Tables

```
Desktop Table Row:
| Premier League | 562K | Rising | [Actions] |

Mobile Card:
┌─────────────────────────────┐
│ Premier League              │
│ Volume: 562K  •  Rising     │
│ ─────────────────────────── │
│ [View] [Create] [Actions]   │
└─────────────────────────────┘
```

## 6.3 Touch Targets

For mobile devices, ensure all interactive elements have:
- Minimum touch target: 48x48px
- Minimum spacing between targets: 8px
- Clear visual feedback on tap

---

# 7. Interaction Patterns

## 7.1 Hover States

| Element | Hover Effect |
|---------|-------------|
| Buttons | Slight lift (translateY -1px), shadow |
| Cards | Subtle glow or border highlight |
| Table rows | Background lighten |
| Links | Underline appear, color change |
| Icons | Scale 1.05, color accent |

## 7.2 Loading States

### Initial Load
1. Show skeleton screens immediately
2. Load critical content first
3. Progressive reveal of secondary content

### Action Loading
1. Show spinner on button
2. Disable button
3. Show toast on completion

### Infinite Scroll
1. Show loading indicator at bottom
2. Append new content seamlessly
3. Update URL without scroll jump

## 7.3 Error Handling

### Form Validation
- Inline validation on blur
- Error message below field
- Red border on invalid field
- Submit button disabled until valid

### API Errors
- Toast notification with error message
- Retry button for recoverable errors
- Fallback UI for critical errors

## 7.4 Confirmation Dialogs

Use for destructive actions:
- Delete content
- Disconnect site
- Bulk actions affecting multiple items

```
┌─────────────────────────────────────┐
│ Confirm Delete                      │
│ ─────────────────────────────────── │
│                                     │
│ Are you sure you want to delete     │
│ "Top 10 Tech Hubs"? This action     │
│ cannot be undone.                   │
│                                     │
│        [Cancel]  [Delete]           │
└─────────────────────────────────────┘
```

---

# 8. Accessibility Guidelines

## 8.1 WCAG 2.2 AA Compliance

### Color Contrast
- Normal text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum
- UI components: 3:1 minimum

### Test Colors
```css
/* Dark theme text colors */
--on-background: #dfe2ec; /* Against #0f131b = 13.5:1 ✓ */
--on-surface-variant: #ddc1b6; /* Against #0f131b = 9.8:1 ✓ */
```

## 8.2 Semantic HTML

```html
<!-- Navigation -->
<nav aria-label="Main navigation">
  <ul role="list">
    <li><a href="/" aria-current="page">Dashboard</a></li>
  </ul>
</nav>

<!-- Main Content -->
<main id="main-content">
  <h1>Dashboard</h1>
  <!-- Content -->
</main>

<!-- Data Table -->
<table aria-describedby="trends-caption">
  <caption id="trends-caption">Trending topics for March 2024</caption>
  <thead>
    <tr>
      <th scope="col">Topic</th>
      <th scope="col">Volume</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Premier League</td>
      <td>562K</td>
    </tr>
  </tbody>
</table>
```

## 8.3 Keyboard Navigation

| Key | Action |
|-----|--------|
| Tab | Move forward through focusable elements |
| Shift + Tab | Move backward |
| Enter/Space | Activate buttons, links |
| Escape | Close modals, dropdowns |
| Arrow keys | Navigate within dropdowns, lists |

### Focus Indicators
```css
:focus-visible {
  outline: 2px solid #ffb596;
  outline-offset: 2px;
}

/* Skip link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  padding: 8px 16px;
  background: #c65d2a;
  color: white;
  z-index: 9999;
}
.skip-link:focus {
  top: 0;
}
```

## 8.4 Screen Reader Support

- All images have meaningful alt text
- Icons have aria-label or aria-hidden
- Dynamic content updates use aria-live regions
- Form inputs have associated labels
- Error messages linked to inputs via aria-describedby

```html
<!-- Live region for notifications -->
<div aria-live="polite" aria-atomic="true" class="sr-only">
  <!-- Toast messages inserted here -->
</div>

<!-- Form field with error -->
<div class="form-group">
  <label for="title">Title</label>
  <input id="title" aria-describedby="title-error" aria-invalid="true">
  <span id="title-error" role="alert">Title is required</span>
</div>
```

---

# 9. Animation & Motion

## 9.1 Timing Functions

```css
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

## 9.2 Duration Scale

| Token | Value | Usage |
|-------|-------|-------|
| `duration-fast` | 150ms | Hover states, color changes |
| `duration-normal` | 250ms | Most transitions |
| `duration-slow` | 400ms | Page transitions, modals |

## 9.3 Animations

### Page Transition
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-enter {
  animation: fadeIn 0.3s var(--ease-out);
}
```

### Card Hover
```css
.card {
  transition: transform 0.2s var(--ease-out), 
              box-shadow 0.2s var(--ease-out);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
}
```

### Button Click
```css
.btn:active {
  transform: scale(0.98);
}
```

### Toast Slide In
```css
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast {
  animation: slideInRight 0.3s var(--ease-out);
}
```

## 9.4 Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

# 10. Iconography

## 10.1 Icon Set

Use **Material Symbols** or **Lucide Icons** for consistency.

### Navigation Icons

| Icon | Name | Usage |
|------|------|-------|
| `dashboard` | Dashboard | Main dashboard |
| `explore` | Discover | Trend discovery |
| `add_circle` | Create | Content creation |
| `layers` | Manage | Content management |
| `monitoring` | Analyze | Analytics |
| `settings` | Settings | App settings |

### Action Icons

| Icon | Name | Usage |
|------|------|-------|
| `edit` | Edit | Edit content |
| `delete` | Delete | Delete content |
| `visibility` | View | View details |
| `publish` | Publish | Publish content |
| `sync` | Sync | Synchronize |
| `refresh` | Refresh | Reload data |

### Status Icons

| Icon | Name | Usage |
|------|------|-------|
| `check_circle` | Success | Completed, published |
| `warning` | Warning | Draft, pending |
| `error` | Error | Failed, error |
| `info` | Info | Informational |
| `trending_up` | Rising | Trending up |
| `trending_down` | Declining | Trending down |

## 10.2 Icon Sizes

| Size | Value | Usage |
|------|-------|-------|
| Small | 16px | Inline, badges |
| Medium | 20px | Buttons, lists |
| Large | 24px | Navigation, headers |
| XL | 32px | Empty states, illustrations |

---

# 11. Page List Summary

## Complete Page Inventory

| # | Page Name | Route | Priority |
|---|-----------|-------|----------|
| 1 | Dashboard (Home) | `/` | P0 |
| 2 | Trend Discovery | `/discover` | P0 |
| 3 | Content Creator | `/create` | P0 |
| 4 | Content Manager | `/manage` | P0 |
| 5 | Sites Manager | `/manage/sites` | P0 |
| 6 | Source Packs | `/manage/source-packs` | P0 |
| 7 | Source Pack Detail | `/manage/source-packs/:id` | P0 |
| 8 | Analytics | `/analyze` | P0 |
| 9 | Settings | `/settings` | P1 |
| 10 | Login | `/login` | P0 |
| 11 | Register | `/register` | P1 |
| 12 | Forgot Password | `/forgot-password` | P1 |
| 13 | 404 Not Found | `*` | P1 |
| 14 | 500 Server Error | `/error` | P1 |

## Screen Variants Per Page

Each page should have the following screen variants designed:

| Page | Desktop (1280px) | Tablet (768px) | Mobile (390px) |
|------|------------------|----------------|----------------|
| Dashboard | ✓ | ✓ | ✓ |
| Discover | ✓ | ✓ | ✓ |
| Create | ✓ | ✓ | ✓ |
| Manage | ✓ | ✓ | ✓ |
| Sites | ✓ | ✓ | ✓ |
| Source Packs | ✓ | ✓ | ✓ |
| Source Pack Detail | ✓ | ✓ | ✓ |
| Analyze | ✓ | ✓ | ✓ |
| Settings | ✓ | ✓ | ✓ |
| Login | ✓ | ✓ | ✓ |
| Register | ✓ | ✓ | ✓ |
| Forgot Password | ✓ | ✓ | ✓ |
| 404 | ✓ | ✓ | ✓ |
| 500 | ✓ | ✓ | ✓ |

**Total Screens**: 14 pages × 3 breakpoints = **42 screens minimum**

---

# 12. Implementation Notes

## 12.1 Technology Stack

- **CSS Framework**: Tailwind CSS with custom design tokens
- **Component Library**: Radix UI primitives (headless)
- **Icons**: Lucide React or Material Symbols
- **Charts**: Recharts or Chart.js
- **Rich Text Editor**: TinyMCE or TipTap

## 12.2 File Structure

```
src/
├── styles/
│   ├── design-tokens.css
│   ├── globals.css
│   └── utilities.css
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Table.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── AppShell.tsx
│   │   └── ...
│   └── features/
│       ├── Dashboard/
│       ├── Discover/
│       ├── Create/
│       └── ...
├── pages/
│   ├── index.tsx
│   ├── discover.tsx
│   ├── create.tsx
│   └── ...
└── hooks/
    ├── useTheme.ts
    └── ...
```

## 12.3 CSS Custom Properties

```css
:root {
  /* Colors */
  --primary: #c65d2a;
  --primary-container: #e1713d;
  --background: #0f131b;
  --surface: #1c2027;
  /* ... */
  
  /* Typography */
  --font-headline: 'Space Grotesk', sans-serif;
  --font-body: 'Inter', sans-serif;
  
  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  /* ... */
  
  /* Radius */
  --radius-md: 8px;
  --radius-lg: 12px;
  /* ... */
}
```

---

# 13. Appendix

## A. Color Contrast Verification

All text colors verified against dark background (#0f131b):

| Color | Hex | Ratio | Status |
|-------|-----|-------|--------|
| Primary text | #dfe2ec | 13.5:1 | ✓ AA+ |
| Secondary text | #ddc1b6 | 9.8:1 | ✓ AA+ |
| Muted text | #9ca3af | 5.2:1 | ✓ AA |
| Accent text | #ffb596 | 8.4:1 | ✓ AA+ |

## B. Component Checklist

- [ ] Button (all variants and sizes)
- [ ] Card (standard, glass, stat)
- [ ] Input (text, select, checkbox, toggle)
- [ ] Table (with responsive card transform)
- [ ] Badge/Chip
- [ ] Modal
- [ ] Toast
- [ ] Tabs
- [ ] Pagination
- [ ] Breadcrumbs
- [ ] Dropdown
- [ ] Tooltip
- [ ] Skeleton
- [ ] Empty State
- [ ] Error State

## C. Accessibility Checklist

- [ ] All images have alt text
- [ ] All forms have labels
- [ ] Color contrast passes WCAG AA
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Screen reader tested
- [ ] Skip link present
- [ ] ARIA attributes correct
- [ ] Reduced motion respected

---

*Document Version: 1.0*  
*Last Updated: March 31, 2026*  
*Author: NTC Design Team*
