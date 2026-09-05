# Jahangir Ceram Catalog

A self-contained, trilingual static product catalog for Jahangir Ceram. The production site is served from [`index.html`](index.html). Images are served as standalone WebP assets from `assets/images/`, allowing Vercel's CDN and browser cache to handle each image independently. Product-gallery images use lazy loading without changing their visual quality or layout.

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

This repository includes `vercel.json` with static-site headers. Image assets are cached for one year using immutable caching. No environment variables, database, Node.js runtime, or server-side build step is required.

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

## Generate the trilingual catalog

`catalog-source.html` is the legacy editable source used by the generator. The validated production page is already committed as `index.html`. Only regenerate it when intentionally updating the source, then run the validator before deploying:

```bash
python3 build_catalog.py
```

This writes `index.html` and creates a backup beside it. Input and output paths can also be supplied explicitly:

```bash
python3 build_catalog.py path/to/catalog-source.html --output path/to/index.html
```

## Compatibility

The catalog supports desktop and mobile layouts, light and dark themes, English/Persian/Arabic, RTL layout, device safe areas, A4 printing, and browsers without full `:has()` support. Images are standalone WebP assets with lazy loading for product galleries. Vazirmatn is loaded from Google Fonts with a system-font fallback when offline.
