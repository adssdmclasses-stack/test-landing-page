/* Lakshyha Academy — landing page logic
   Injects config, runs the exam countdown, validates + submits the lead,
   and pushes dataLayer events for GTM / Google Ads conversions. */

(function () {
  "use strict";
  var C = window.LA_CONFIG || {};
  var dl = (window.dataLayer = window.dataLayer || []);

  /* ---------- helpers ---------- */
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function push(name, extra) { dl.push(Object.assign({ event: name }, extra || {})); }
  function variant() { var el = document.getElementById("page_variant"); return el ? el.value : "unknown"; }

  /* Optional direct gtag fallback if you are not using GTM for conversions. */
  function adsConversion(labelKey) {
    var id = C.adsConversionId, lab = (C.conversionLabels || {})[labelKey];
    if (typeof gtag === "function" && id && lab && id.indexOf("X") === -1) {
      gtag("event", "conversion", { send_to: id + "/" + lab });
    }
  }

  /* ---------- 1. inject contact details everywhere ---------- */
  var tel = "tel:" + (C.phoneDial || "");
  var wa = "https://wa.me/" + (C.whatsapp || "") +
    "?text=" + encodeURIComponent("Hi, I want details about Class 10 coaching at Lakshyha Academy, Bhopal.");

  $$("[data-call]").forEach(function (a) {
    a.setAttribute("href", tel);
    a.addEventListener("click", function () {
      push("gtb_call_click", { link_url: tel, page_variant: variant() });
      adsConversion("callClick");
    });
  });
  $$("[data-phone-text]").forEach(function (n) { n.textContent = C.phoneDisplay || ""; });

  $$("[data-whatsapp]").forEach(function (a) {
    a.setAttribute("href", wa);
    a.setAttribute("target", "_blank");
    a.setAttribute("rel", "noopener");
    a.addEventListener("click", function () {
      push("gtb_whatsapp_click", { page_variant: variant() });
      adsConversion("whatsapp");
    });
  });

  $$("[data-maps]").forEach(function (a) {
    a.setAttribute("href", C.mapsUrl || "#");
    a.setAttribute("target", "_blank");
    a.setAttribute("rel", "noopener");
  });

  var addr = (C.addressLine1 || "") + ", " + (C.addressLine2 || "");
  $$("[data-address1]").forEach(function (n) { n.textContent = C.addressLine1 || ""; });
  $$("[data-address2]").forEach(function (n) { n.textContent = C.addressLine2 || ""; });
  $$("[data-address-inline]").forEach(function (n) { n.textContent = addr; });
  $$("[data-fee-note]").forEach(function (n) { if (C.feeNote) n.textContent = C.feeNote; });
  $$("[data-year]").forEach(function (n) { n.textContent = new Date().getFullYear(); });

  /* ---------- 2. exam countdown (hero signature) ---------- */
  (function countdown() {
    var big = $("[data-cd-days]"); if (!big) return;
    var exam = new Date(C.examDate || "");
    if (isNaN(exam.getTime())) { big.textContent = "—"; return; }

    var ms = exam - new Date();
    var days = Math.max(0, Math.ceil(ms / 86400000));
    var weeks = Math.max(0, Math.floor(days / 7));

    big.textContent = days;
    var w = $("[data-cd-weeks]"); if (w) w.textContent = weeks;
    var lbl = $("[data-cd-label]");
    if (lbl && C.examLabel) lbl.textContent = "Time left until " + C.examLabel;

    /* track: 40 segments across a 12-month prep year, filled = time already gone */
    var track = $("[data-cd-track]"); if (!track) return;
    var total = 365, gone = Math.min(40, Math.round(((total - days) / total) * 40));
    for (var i = 0; i < 40; i++) {
      var seg = document.createElement("i");
      if (i < gone) seg.className = "done";
      track.appendChild(seg);
    }
  })();

  /* ---------- 3. lead form ---------- */
  var form = $("#lead-form");
  if (!form) return;

  var msg = $("[data-form-msg]");
  var btn = $("[data-submit]");
  var startedTracked = false;

  form.addEventListener("input", function () {
    if (!startedTracked) { push("gtb_form_start"); startedTracked = true; }
  }, { once: false });

  /* keep the phone field numeric, 10 digits */
  var phoneEl = $("#phone");
  phoneEl.addEventListener("input", function () {
    this.value = this.value.replace(/\D/g, "").slice(0, 10);
  });

  function setErr(el, bad, text) {
    var f = el.closest(".field");
    if (!f) return;
    f.classList.toggle("invalid", bad);
    if (text) { var e = $(".err", f); if (e) e.textContent = text; }
  }

  function validate() {
    var ok = true;

    var name = $("#name");
    var nameBad = name.value.trim().length < 2;
    setErr(name, nameBad); if (nameBad) ok = false;

    var phoneBad = !/^[6-9]\d{9}$/.test(phoneEl.value);
    setErr(phoneEl, phoneBad, "Enter a valid 10-digit Indian mobile number.");
    if (phoneBad) ok = false;

    var email = $("#email");
    var emailBad = email.value.trim() !== "" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.value.trim());
    setErr(email, emailBad); if (emailBad) ok = false;

    var board = $("#board");
    var boardBad = !board.value;
    setErr(board, boardBad); if (boardBad) ok = false;

    var consent = $("#consent");
    if (!consent.checked) {
      ok = false;
      show("Please tick the consent box so we can call you back.", "bad");
    }
    return ok;
  }

  function show(text, kind) {
    if (!msg) return;
    msg.textContent = text;
    msg.className = "form-msg show " + (kind || "");
  }
  function hide() { if (msg) msg.className = "form-msg"; }

  /* fill the GTB hidden fields.
     If the blueprint's click-capture script is loaded it owns these
     (window.GTB auto-populates). This is only a fallback so the fields
     are never empty in the sheet. */
  function fillHidden() {
    var p = new URLSearchParams(location.search);
    function set(id, val) { var el = document.getElementById(id); if (el && !el.value && val) el.value = val; }
    ["gclid", "gbraid", "wbraid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]
      .forEach(function (k) { set(k, p.get(k) || ""); });
    set("page_url", location.href);
    set("submitted_at", new Date().toISOString());
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    hide();
    if (!validate()) return;
    fillHidden();

    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    data.consent = $("#consent").checked ? "yes" : "no";

    push("gtb_form_submit", {
      form_name: "class10_demo_booking",
      page_variant: data.page_variant || "",
      board: data.board || "",
      area: data.area || ""
    });
    adsConversion("formSubmit");

    var done = function () { location.href = C.thankYouUrl || "/thank-you.html"; };

    /* No endpoint configured yet → hand off to WhatsApp so leads are never lost. */
    if (!C.formEndpoint) {
      var text = "New demo booking request\n" +
        "Name: " + (data.name || "") + "\n" +
        "Phone: " + (data.phone || "") + "\n" +
        "Board: " + (data.board || "") + "\n" +
        "Area: " + (data.area || "");
      window.open("https://wa.me/" + (C.whatsapp || "") + "?text=" + encodeURIComponent(text), "_blank", "noopener");
      done();
      return;
    }

    btn.disabled = true;
    btn.textContent = "Booking…";

    fetch(C.formEndpoint, {
      method: "POST",
      mode: "no-cors",                       // Apps Script web app
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify(data)
    }).then(done).catch(function () {
      btn.disabled = false;
      btn.textContent = "Book my free demo class";
      show("Could not submit just now. Please call us instead — we'll book the slot on the phone.", "bad");
    });
  });
})();
