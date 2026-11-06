# CL Partners website

Static multi-page website for CL Partners Sàrl (Geneva).

## Structure
- `site/` — the deployable website (HTML, CSS, JS, assets). Deploy this folder as-is to any static host (Netlify, Vercel, GitHub Pages, etc.).
- `_build/` — page sources and the build script that assembles shared header, footer and modals into `site/`.

## Editing
1. Edit page bodies in `_build/pages/*.html` (shared header/footer/forms live in `_build/build.py`).
2. Rebuild: `python3 _build/build.py`
3. Preview locally: `cd site && python3 -m http.server 4321` then open http://localhost:4321

CSS (`site/css/styles.css`) and JS (`site/js/main.js`) are edited directly.

## Forms
Forms run in demo mode until endpoints are configured in the `CONFIG` block at the top of `site/js/main.js`
(`leadEndpoint` for Executive Field Note downloads, `contactEndpoint`, `careersEndpoint`). Each receives a JSON POST.

## Before launch
- Connect form endpoints.
- Download and self-host the Unsplash images (currently hotlinked).
- Legal review of `privacy.html`; approve team bios and case copy.
