## Swagger UI Upgrade — Summary

### Changes Made
- Added "🔑 Get Free API Key" green pill button in topbar (links to /signup)
- Pre-filled demo key `docai-dev-key-12345` via requestInterceptor and onComplete input finder
- Added custom dark theme: background #0b1f3a, topbar #1a1a2e, accent #4ade80
- Added "Try It" banner: demo key pre-loaded message with signup link
- Added responsive CSS for mobile (stacked topbar, padding adjustments)
- Kept all original Swagger UI config (url, dom_id, deepLinking, presets, layout)
- Kept OpenAPI Spec link in topbar

### Files Modified
- `src/docai/pa_wsgi.py` — `_SWAGGER_UI_HTML` string only (no other code changed)

### Verification
- Import OK: `from docai.pa_wsgi import application` works
- All 10 content assertions pass (CTA, demo key, Swagger UI, signup links, colors, interceptor, banner)
