# Lakshyha Academy — Class 10 Coaching Landing Pages (Bhopal)

Static site. No build step on Vercel — push to GitHub, import, done.
Live at **https://vercel-test.sdmlabs.in**

---

## URL map → ad group

One page per ad group. Keep it that way; a shared page across ad groups is the
main reason Quality Score drops on coaching accounts.

| URL | Ad group | Keyword theme |
|---|---|---|
| `/` | Brand / broad | lakshyha academy, coaching classes bhopal |
| `/10th-class-coaching-bhopal` | Core | 10th class coaching bhopal, class 10 coaching near me |
| `/mp-board-10th-coaching-bhopal` | MP Board | mp board 10th coaching, mpbse class 10 tuition |
| `/cbse-class-10-coaching-bhopal` | CBSE | cbse class 10 coaching bhopal, cbse 10th tuition |
| `/class-10-maths-science-coaching-bhopal` | Subject | class 10 maths coaching, science tuition for 10th |
| `/class-10-tuition-near-me-bhopal` | Location / near me | 10th tuition near me, class 10 tuition bhopal timings |
| `/class-10-crash-course-bhopal` | Crash course | 10th crash course, board exam preparation classes |

`cleanUrls` is on, so `10th-class-coaching-bhopal.html` serves at
`/10th-class-coaching-bhopal`. Use the clean URL as the Final URL in Ads.

Short vanity paths are redirected for offline use (pamphlets, WhatsApp forwards):
`/mp-board`, `/cbse`, `/crash-course`, `/near-me`, `/maths-science`.

---

## Files

```
lakshyha-academy/
├── build/generate.py           ← *** EDIT COPY HERE, then re-run ***
├── index.html                                  ← generated
├── 10th-class-coaching-bhopal.html             ← generated
├── mp-board-10th-coaching-bhopal.html          ← generated
├── cbse-class-10-coaching-bhopal.html          ← generated
├── class-10-maths-science-coaching-bhopal.html  ← generated
├── class-10-tuition-near-me-bhopal.html        ← generated
├── class-10-crash-course-bhopal.html           ← generated
├── thank-you.html   privacy.html   terms.html
├── assets/config.js            ← *** EDIT PHONE / IDs HERE *** (source, inlined at build)
├── assets/styles.css   assets/app.js   ← source, inlined at build
├── apps-script/Code.gs         ← Google Sheet lead endpoint
├── vercel.json   robots.txt   sitemap.xml   ← robots + sitemap are generated
```

### Self-contained pages (why nothing is linked from /assets/)

`SITE["inline_assets"] = True`, so `generate.py` writes the CSS and JS **into
every .html file**. Each page works on its own — if the `assets/` folder never
makes it to the server, the page still renders and the form still works.

You keep editing `assets/styles.css`, `assets/app.js` and `assets/config.js` as
normal. They are the source; the build copies them in. Re-run `generate.py`
after any change to them, or the deployed pages keep the old version.

Set `inline_assets` to `False` if you'd rather link them externally (needs the
`assets/` folder present at the deployed root, and gives shared browser caching
across the seven pages).

The one thing still loaded externally is the GTB click-capture script, which is
commented out until you add the file.

### How to change page copy

The seven landing pages are generated from one template so shared sections
(fees table, subjects, proof strip, base FAQ, footer) live in a single place.

```bash
# edit build/generate.py  →  SITE, PAGES, or the shared blocks
python3 build/generate.py
git add . && git commit -m "copy update" && git push
```

Editing a generated `.html` by hand works, but the next `generate.py` run
overwrites it. Shared changes belong in the blocks; per-page changes belong in
that page's entry in `PAGES`.

To add a page: copy any dict in `PAGES`, change `slug`, `path`, `variant`,
title, H1 and the `focus` block, then re-run. The sitemap updates itself.

---

## 1. Fill in the blanks before spending anything

**`assets/config.js`** — phone, WhatsApp, address, Maps URL, board exam date,
GTM ID, Ads conversion IDs, Apps Script URL.

**`build/generate.py`** — search for `__` and `[Replace` / `[List` / `[Describe`:
- proof strip: years teaching, % above 75, practice paper count
- fees table: timings, seats, amounts
- 3 real parent/student quotes
- areas of Bhopal on the near-me page
- `SITE["gtm"]` — the GTM container ID

**`privacy.html` / `terms.html`** — replace `[ADD EMAIL]`, `[ADD PHONE]`.

Nothing may still read `__` at launch. Google's editorial review rejects
placeholder text, and parents bounce off it faster than the reviewer does.

---

## 2. Lead capture

Deploy `apps-script/Code.gs` (steps inside the file), paste the `/exec` URL into
`config.js` → `formEndpoint`. The sheet carries **`page_variant`**, so you can
see which URL each lead came from without touching Ads reports.

Blank `formEndpoint` = the form hands off to WhatsApp instead. Fine for day one,
useless for reporting.

---

## 3. GitHub

```bash
cd lakshyha-academy
git init
git add .
git commit -m "Lakshyha Academy Class 10 landing pages"
git branch -M main
git remote add origin https://github.com/<username>/lakshyha-academy.git
git push -u origin main
```

## 4. Vercel

1. vercel.com → **Add New → Project** → import the repo
2. Framework preset **Other**, build command empty, output directory empty
3. Deploy
4. Project → Settings → **Domains** → add `vercel-test.sdmlabs.in`
5. At the DNS host for `sdmlabs.in`:

| Type  | Name          | Value                  |
|-------|---------------|------------------------|
| CNAME | `vercel-test` | `cname.vercel-dns.com` |

Every `git push` to `main` redeploys automatically.

**When you move to the client's own domain:** update `SITE["domain"]` in
`generate.py`, set `SITE["noindex"] = False`, re-run, push.

---

## 5. Indexing — a deliberate choice

`SITE["noindex"] = True`, so every page carries `noindex,nofollow` and
`robots.txt` blocks general crawlers while explicitly allowing
`AdsBot-Google` and `AdsBot-Google-Mobile`.

Reason: `vercel-test.sdmlabs.in` is your test subdomain. If it gets indexed it
competes with the client's real site and puts your subdomain into search results
for their brand. Google Ads serves noindex landing pages without any problem —
but AdsBot must stay allowed or Ads can't check the page and the ads get
disapproved.

Flip `noindex` to `False` only on the client's own domain.

---

## 6. Tracking — GTB v1.2.1, Path A + Method A

- Drop the blueprint's click-capture JS at `assets/gtb-click-capture.js`, then
  uncomment the `<script>` tag in the `<head>` block inside `generate.py` and
  re-run so all seven pages get it.
- The 9 hidden fields are in every form. **Confirm the names against the
  blueprint's Method A list** — if they differ, rename in `generate.py` and in
  `apps-script/Code.gs` `HEADERS`.
- `app.js` fills those fields from the URL as a fallback, so nothing lands blank.

**dataLayer events** (all carry `page_variant`):

| Event | When |
|---|---|
| `page_variant` push | on page load, before GTM fires |
| `gtb_form_start` | first keystroke in the form |
| `gtb_form_submit` | valid submit (also carries `board`, `area`) |
| `gtb_call_click` | any tel: link tapped |
| `gtb_whatsapp_click` | any WhatsApp link tapped |
| `gtb_thank_you_view` | thank-you page loads |

Import the blueprint's GTM container, map these to the conversion actions, fill
the Conversion ID/Labels in the CONST variables. If conversions fire through GTM
only, leave `adsConversionId` as `AW-XXXXXXXXXX` — the direct `gtag` fallback in
`app.js` stays dormant unless real IDs are present, so no double counting.

Register `page_variant` as a dataLayer variable in GTM and pass it to GA4 as a
custom dimension — that's per-URL conversion rate with no extra setup.

Run the 29-check pre-launch audit before go-live. No campaign changes for 30 days after.

---

## 7. If a page renders as plain text

Unstyled page, no phone number in the header, countdown stuck on `—`, blank
address: that is not a CSS bug. It means the browser got the HTML but nothing
else. Check in this order:

1. Open `/assets/styles.css` on the live domain. A 404 means the folder isn't
   deployed. With `inline_assets = True` this can't happen — re-run
   `generate.py` and push the regenerated `.html` files.
2. **Vercel → Settings → Build & Deployment → Root Directory** must be empty or
   `./`. If the repo has everything inside a `lakshyha-academy/` folder, either
   set Root Directory to that folder or move the files up to the repo root.
3. If you uploaded through the GitHub web UI, check the repo actually shows an
   `assets/` folder. Drag-and-drop often drops folders silently. `git push` from
   the command line is safer.
4. Case matters on Vercel. `Assets/` is not `assets/`.

## 8. Pre-launch checklist

- [ ] Every `__` and `[Replace ...]` gone from all seven pages
- [ ] Phone tested on a real mobile (tap-to-call works)
- [ ] Form submits → row in the Sheet with the right `page_variant` → thank-you page
- [ ] `gclid` lands in the sheet (test with `?gclid=test123`)
- [ ] Each ad group's Final URL points at its own page, not the homepage
- [ ] Privacy policy link visible above the fold on mobile
- [ ] `robots.txt` allows AdsBot (check at `/robots.txt` after deploy)
- [ ] Auto-tagging ON in the Ads account
- [ ] Ad headline matches the H1 promise on the page it lands on
- [ ] Page renders styled on the live URL, not just locally
