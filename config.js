/* =============================================================
   LAKSHYHA ACADEMY — LANDING PAGE CONFIG
   This is the ONLY file you need to edit for launch.
   Everything below is injected into the page at runtime.
   ============================================================= */

window.LA_CONFIG = {

  /* ---------- 1. CONTACT (required) ---------- */
  phoneDisplay: "+91 XXXXX XXXXX",        // shown on the page
  phoneDial:    "+91XXXXXXXXXX",          // tel: link, no spaces
  whatsapp:     "91XXXXXXXXXX",           // wa.me number, country code, no +
  email:        "admissions@lakshyhaacademy.com",

  /* ---------- 2. CENTRE ---------- */
  centreName:   "Lakshyha Academy",
  addressLine1: "Shop No. __, __________ Complex",
  addressLine2: "____________, Bhopal, Madhya Pradesh 462___",
  mapsUrl:      "https://maps.google.com/?q=Lakshyha+Academy+Bhopal",

  /* ---------- 3. BOARD EXAM COUNTDOWN (hero signature) ---------- */
  // Set to the first paper date of the coming Class 10 board exam.
  // MP Board 10th usually starts in the first week of February.
  examDate:  "2027-02-05T09:00:00+05:30",
  examLabel: "MP Board Class 10 — first paper",

  /* ---------- 4. LEAD DESTINATION ---------- */
  // Google Apps Script Web App URL (deploy as: Execute as ME, Access ANYONE).
  // Leave blank and the form falls back to WhatsApp handoff.
  formEndpoint: "",

  // Page the user lands on after a successful submit (conversion page).
  thankYouUrl: "/thank-you.html",

  /* ---------- 5. TRACKING ---------- */
  gtmId: "GTM-XXXXXXX",                   // also paste into index.html <head>

  // Google Ads conversion actions. Fill from Ads > Goals > Conversions.
  // These fire only if you are NOT routing everything through GTM.
  adsConversionId: "AW-XXXXXXXXXX",
  conversionLabels: {
    formSubmit: "XXXXXXXXXXXXXXXXXX",     // "Demo Booking" conversion label
    callClick:  "XXXXXXXXXXXXXXXXXX",     // "Phone Call Click" conversion label
    whatsapp:   "XXXXXXXXXXXXXXXXXX"      // "WhatsApp Click" conversion label
  },

  /* ---------- 6. FEES / BATCHES (edit the table in index.html too) ---------- */
  feeNote: "One-time registration ₹___ · Instalment option available"
};
