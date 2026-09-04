# SDM Real Estate — static website

Six-page static site. No build step, no dependencies. Drop the folder into a repo and turn on GitHub Pages.

## Files

```
index.html      Home
about.html      About us
services.html   Services + fee table
coverage.html   Service areas (map embed placeholder)
contact.html    Contact + enquiry form
faq.html        FAQ + FAQPage schema
404.html        Not-found page
robots.txt      Crawler rules
sitemap.xml     Six URLs
README.md       This file
```

Every page is standalone: its own CSS block, its own schema, relative links only.

---

## Deploy to GitHub Pages

1. Create a repo, e.g. `sdm-real-estate`. Public.
2. Upload all files to the **root** of the repo, not inside a subfolder.
3. Repo → **Settings** → **Pages**.
4. Source: **Deploy from a branch**. Branch: `main`, folder: `/ (root)`. Save.
5. Wait 1–2 minutes. Your site is at `https://YOURUSERNAME.github.io/sdm-real-estate/`.

### Custom domain (recommended)

In Settings → Pages → Custom domain, enter your domain. Then at your DNS provider add:

```
A     @    185.199.108.153
A     @    185.199.109.153
A     @    185.199.110.153
A     @    185.199.111.153
CNAME www  YOURUSERNAME.github.io
```

Tick **Enforce HTTPS** once the certificate is issued.

---

## Important: the contact form does not work on GitHub Pages

`contact.html` uses **Netlify Forms** (`data-netlify="true"`). GitHub Pages is static hosting with no form handling, so submissions will fail silently.

Pick one:

- **Deploy to Netlify instead** — drag the folder onto netlify.com/drop. The form works immediately, submissions appear under Site settings → Forms.
- **Stay on GitHub, swap the form handler.** Sign up at formspree.io, then in `contact.html` change:
  ```html
  <form name="enquiry" method="POST" data-netlify="true" netlify-honeypot="bot-field" id="enquiryForm">
  ```
  to:
  ```html
  <form method="POST" action="https://formspree.io/f/YOUR_FORM_ID" id="enquiryForm">
  ```
  and delete the hidden `form-name` input.
- **Remove the form** and rely on the call, WhatsApp and email blocks, which all work anywhere.

Phone, WhatsApp and email links work on both hosts regardless.

---

## Before you go live

**Find and replace across all files**

| Find | Replace with |
|---|---|
| `https://sdmrealestate.com/` | your live URL (canonical, OG, schema, sitemap, robots) |

**Content to replace**

- `index.html` — hero trust numbers (1,200+ / 4.9 / 60 min), three testimonials
- `about.html` — founding story, fact panel, four stats, three team names, **RERA registration number** (currently `TS/AGENT/XXXX/XXXX`)
- `services.html` — every fee in the pricing table
- `faq.html` — fee answers in **both** the visible accordion and the FAQPage JSON-LD; they must match services.html
- `coverage.html` — paste your Google Maps iframe where `<!-- MAP EMBED HERE -->` is, replacing the `.mapholder` div
- `contact.html` + `faq.html` — confirm the opening hours
- Add `og-image.jpg` (1200×630) to the folder root

**Tracking**

Paste your GTM container snippet at `<!-- GTM CODE HERE -->` in all seven HTML files. The `dataLayer` array is already initialised above it.

Events already firing:

| Event | Fires on | `cta_location` values |
|---|---|---|
| `call_now_click` | every `tel:` link | `topbar`, `header`, `hero`, `sticky`, `footer`, `final`, `map`, `coverage_banner`, `faq_stuck`, `404`, plus per-service and per-contact-block values |
| `whatsapp_click` | every WhatsApp link | always `whatsapp`; the placement is in `cta_placement` |
| `form_submit` | contact form submit | `contact_form` |

**After launch**

- Google Search Console: add the property, submit `sitemap.xml`
- Google Business Profile: make sure NAP (name, phone, address) matches the site exactly
- Test the schema at `search.google.com/test/rich-results`
- Run PageSpeed Insights on mobile

---

## Editing tips

Each page repeats its own `<style>` block, by design — that keeps every file standalone. The trade-off is that a colour or header change must be made in all seven files. The tokens live at the top of each `<style>` block:

```css
--green:#0B5D3B;   /* primary */
--ink:#101A15;     /* dark */
--stone:#ECEEE9;   /* background */
--gold:#C9A227;    /* accent / call buttons */
```

Phone number appears as `+917483736358` in `tel:` and `wa.me` links, and as `+91 74837 36358` in visible text. Change both if the number ever changes.
