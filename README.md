# Jahangir Ceram Catalog

A self-contained, trilingual static product catalog for Jahangir Ceram. The production site is served from [`index.html`](index.html). Images are served as standalone WebP assets from `assets/images/` so the browser and Vercel CDN can cache them independently.

## Run locally

Open `index.html` directly in a modern browser, or serve the repository with any static web server:

```bash
python3 -m http.server 8000
```

Then visit <http://localhost:8000>.

## Deploy to GitHub and Vercel

1. Create a GitHub repository and push the contents of this directory.
2. In Vercel, choose **Add New → Project**, import the GitHub repository, and keep the default framework setting as **Other**.
3. Leave the build command empty and set the output directory to `.`. Vercel will serve `index.html` automatically.

This repository includes `vercel.json` with static-site headers. Image assets use long-lived immutable caching. No environment variables, database, Node.js runtime, or server-side build step is required.

## Validate the catalog

Install the validation dependencies and run the checks:

```bash
python3 -m pip install -r requirements.txt
python3 validate_catalog.py
```

To validate another HTML file:

```bash
python3 validate_catalog.py path/to/catalog.html
```

## Editing the catalog

The production `index.html` in this package is the complete catalog, including its newer catalog sections. Edit that file directly when changing catalog data or image paths, and place WebP image assets in `assets/images/`. The old generator script is intentionally not included because it could overwrite newer production sections.

## Compatibility

The catalog supports desktop and mobile layouts, light and dark themes, English/Persian/Arabic, RTL layout, device safe areas, A4 printing, and browsers without full `:has()` support. Images are standalone WebP assets, with lazy loading retained for product galleries. Vazirmatn is loaded from Google Fonts with a system-font fallback when offline.
