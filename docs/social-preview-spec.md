# Social Preview Image Spec

## Dimensions

- **Size:** 1280 × 640 px (2:1 ratio, standard for GitHub/Open Graph/Twitter)
- **Format:** PNG
- **File:** `docai-social-preview.png`

## Layout

```
┌─────────────────────────────────────┬──────────────────────────────┐
│                                     │                              │
│         DARK NAVY BACKGROUND        │     CODE SNIPPET PANEL       │
│                                     │                              │
│     DocAI Verify                    │     {                        │
│     Income Verification API         │       "verification_score":  │
│     for Indonesian Fintech          │         82,                  │
│                                     │       "detected_monthly_     │
│                                     │         income": 12500000,   │
│                                     │       "income_source":       │
│                                     │         "salary",            │
│                                     │       "consistency_score":   │
│                                     │         95,                  │
│     docaiid.pythonanywhere.com      │       "balance_valid": true  │
│                                     │     }                        │
│                                     │                              │
└─────────────────────────────────────┴──────────────────────────────┘
```

## Text (Left Side)

| Element | Content | Font Size | Weight |
|---------|---------|-----------|--------|
| Title | **DocAI Verify** | 48px | Bold |
| Subtitle | Income Verification API for Indonesian Fintech | 24px | Regular |
| URL | docaiid.pythonanywhere.com | 16px | Regular |

## Code Snippet (Right Side)

```json
{
  "verification_score": 82,
  "detected_monthly_income": 12500000,
  "income_source": "salary",
  "consistency_score": 95,
  "balance_valid": true
}
```

## Colors

| Element | Color | Hex |
|---------|-------|-----|
| Background (left) | Dark navy | `#0b1f3a` |
| Text | White | `#ffffff` |
| Code panel background | Darker navy | `#0f172a` |
| Code text | Light gray | `#94a3b8` |
| Syntax highlight (keys) | Slate | `#64748b` |
| Syntax highlight (strings) | Green | `#4ade80` |
| Syntax highlight (numbers) | Yellow | `#facc15` |
| Syntax highlight (booleans) | Cyan | `#22d3ee` |
| Accent border/line | Green | `#4ade80` |

## Typography

- **Title:** Sans-serif, bold (Inter, Helvetica, or system default)
- **Subtitle:** Sans-serif, regular weight
- **Code:** Monospace (JetBrains Mono, Fira Code, or system monospace)

## Notes

- The code snippet is the visual hook — it immediately communicates "API" and "structured data"
- The green accent (`#4ade80`) ties to the "verification passed" / "score" concept
- Keep the code panel slightly darker than the left panel for visual separation
- No logo image needed — the text treatment is the brand mark for now
- Export at 2x if targeting Retina displays (2560 × 1280)
