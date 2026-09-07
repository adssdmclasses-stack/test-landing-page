/**
 * SDM Real Estate — website enquiry handler
 * Google Apps Script backend for index.html and contact.html forms.
 *
 * What it does
 *   1. Receives a form POST from the website
 *   2. Appends the lead to a Google Sheet
 *   3. Emails you a notification with a click-to-call and WhatsApp link
 *
 * Works on GitHub Pages, Netlify, or any static host. No server needed.
 * Setup instructions are at the bottom of this file.
 */

/* ============================================================
   CONFIGURATION — edit these five values
   ============================================================ */

// Sheet tab name. Created automatically if missing.
const SHEET_NAME = 'Leads';

// Where lead notifications are sent. Comma-separate for multiple recipients.
const NOTIFY_EMAIL = 'sdmrealestate@gmail.com';

// Set to false to stop notification emails (leads still go to the sheet).
const SEND_EMAIL = true;

// Your business phone, digits only with country code. Used in the email links.
const BUSINESS_PHONE = '917483736358';

// Timezone for the timestamp column.
const TIMEZONE = 'Asia/Kolkata';

/* ============================================================
   Column order. Change here and the sheet header updates itself.
   ============================================================ */
const HEADERS = [
  'Timestamp',
  'Name',
  'Phone',
  'Message',
  'Source page',
  'Referrer',
  'Status',
  'Notes'
];

/* ============================================================
   MAIN HANDLER
   ============================================================ */

function doPost(e) {
  const lock = LockService.getScriptLock();

  try {
    // Prevents two simultaneous submissions writing to the same row.
    lock.waitLock(20000);

    const data = parseBody_(e);

    // Honeypot: bots fill hidden fields, humans never see them.
    // Return success so the bot does not retry, but write nothing.
    if (data.bot_field) {
      return jsonResponse_({ result: 'ok' });
    }

    const name = String(data.name || '').trim();
    const phone = String(data.phone || '').trim();
    const message = String(data.message || '').trim();
    const page = String(data.page || 'unknown').trim();
    const referrer = String(data.referrer || '').trim();

    if (!name || !phone) {
      return jsonResponse_({
        result: 'error',
        message: 'Name and phone number are required.'
      });
    }

    // Basic sanity check — 8 to 20 characters of digits and phone punctuation.
    if (!/^[0-9+()\-\s]{8,20}$/.test(phone)) {
      return jsonResponse_({
        result: 'error',
        message: 'That phone number does not look right. Please check it.'
      });
    }

    const timestamp = Utilities.formatDate(new Date(), TIMEZONE, 'dd MMM yyyy, HH:mm');

    const sheet = getSheet_();
    sheet.appendRow([
      timestamp,
      name,
      phone,
      message,
      page,
      referrer,
      'New',      // Status — change to Contacted / Qualified / Closed as you work the lead
      ''          // Notes — yours to fill in
    ]);

    if (SEND_EMAIL) {
      sendNotification_({
        timestamp: timestamp,
        name: name,
        phone: phone,
        message: message,
        page: page
      });
    }

    return jsonResponse_({ result: 'ok' });

  } catch (err) {
    // Log it so you can see failures under Executions in the Apps Script editor.
    console.error('doPost failed: ' + err);
    return jsonResponse_({
      result: 'error',
      message: 'Something went wrong on our side. Please call us instead.'
    });

  } finally {
    try { lock.releaseLock(); } catch (ignore) {}
  }
}

/**
 * Health check. Open the web app URL in a browser to confirm it is live.
 */
function doGet() {
  return jsonResponse_({
    result: 'ok',
    message: 'SDM Real Estate enquiry endpoint is running.'
  });
}

/* ============================================================
   HELPERS
   ============================================================ */

/**
 * Accepts both form-encoded posts (e.parameter) and raw JSON bodies.
 * Form-encoded is what the website sends, because it avoids a CORS preflight.
 */
function parseBody_(e) {
  if (e && e.parameter && Object.keys(e.parameter).length) {
    return e.parameter;
  }
  if (e && e.postData && e.postData.contents) {
    try {
      return JSON.parse(e.postData.contents);
    } catch (err) {
      return {};
    }
  }
  return {};
}

/**
 * Returns the leads sheet, creating it with headers if it does not exist.
 * Also repairs the header row if it is missing or out of date.
 */
function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }

  const firstCell = sheet.getRange(1, 1).getValue();
  if (firstCell !== HEADERS[0]) {
    sheet.insertRowBefore(1);
    const headerRange = sheet.getRange(1, 1, 1, HEADERS.length);
    headerRange.setValues([HEADERS]);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#0B5D3B');
    headerRange.setFontColor('#FFFFFF');
    sheet.setFrozenRows(1);
    sheet.setColumnWidth(1, 150); // Timestamp
    sheet.setColumnWidth(2, 160); // Name
    sheet.setColumnWidth(3, 140); // Phone
    sheet.setColumnWidth(4, 340); // Message
  }

  return sheet;
}

/**
 * Emails the lead with tap-to-call and WhatsApp links, so you can act
 * on it straight from your phone.
 */
function sendNotification_(lead) {
  const cleanPhone = lead.phone.replace(/[^0-9]/g, '');
  const waPhone = cleanPhone.length === 10 ? '91' + cleanPhone : cleanPhone;

  const subject = 'New website lead: ' + lead.name + ' — ' + lead.phone;

  const body =
    '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#101A15;line-height:1.6">' +
      '<p style="margin:0 0 18px;font-size:13px;color:#41504A">' +
        'New enquiry from the website, ' + lead.timestamp +
      '</p>' +

      '<table cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:22px">' +
        row_('Name', escapeHtml_(lead.name)) +
        row_('Phone', '<a href="tel:+' + waPhone + '" style="color:#0B5D3B;font-weight:bold">' + escapeHtml_(lead.phone) + '</a>') +
        row_('Looking for', lead.message ? escapeHtml_(lead.message) : '<em style="color:#8A968F">not specified</em>') +
        row_('Page', escapeHtml_(lead.page)) +
      '</table>' +

      '<p style="margin:0 0 8px">' +
        '<a href="tel:+' + waPhone + '" ' +
           'style="display:inline-block;background:#C9A227;color:#20180A;text-decoration:none;' +
           'font-weight:bold;padding:12px 22px;border-radius:999px;margin-right:8px">Call ' + escapeHtml_(lead.name) + '</a>' +
        '<a href="https://wa.me/' + waPhone + '" ' +
           'style="display:inline-block;background:#0B5D3B;color:#ffffff;text-decoration:none;' +
           'font-weight:bold;padding:12px 22px;border-radius:999px">WhatsApp them</a>' +
      '</p>' +

      '<p style="margin:24px 0 0;font-size:12px;color:#8A968F">' +
        'Sent automatically by the SDM Real Estate website. The full list is in your Google Sheet.' +
      '</p>' +
    '</div>';

  MailApp.sendEmail({
    to: NOTIFY_EMAIL,
    subject: subject,
    htmlBody: body,
    name: 'SDM Real Estate website',
    replyTo: NOTIFY_EMAIL
  });
}

function row_(label, value) {
  return '<tr>' +
    '<td style="padding:6px 18px 6px 0;color:#41504A;vertical-align:top;white-space:nowrap">' + label + '</td>' +
    '<td style="padding:6px 0;font-weight:bold;vertical-align:top">' + value + '</td>' +
  '</tr>';
}

function escapeHtml_(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function jsonResponse_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/* ============================================================
   RUN ONCE, MANUALLY, TO TEST
   Select testSubmission in the toolbar dropdown and press Run.
   It writes a fake lead and sends you the notification email,
   so you can confirm both work before going live.
   ============================================================ */
function testSubmission() {
  const fake = {
    parameter: {
      name: 'Test Lead',
      phone: '+91 90000 00000',
      message: '3BHK in Kondapur, budget around 1.2 Cr. This is a test row, delete it.',
      page: 'test',
      referrer: 'manual test'
    }
  };
  const res = doPost(fake);
  console.log(res.getContent());
}


/* ============================================================
   SETUP — do this once, takes about five minutes

   1.  Create a new Google Sheet. Name it something like
       "SDM Real Estate — Website Leads".

   2.  In that sheet: Extensions > Apps Script.

   3.  Delete whatever is in Code.gs and paste this entire file in.
       Press the save icon.

   4.  Edit the five values in the CONFIGURATION block at the top.

   5.  Press Run with "testSubmission" selected in the dropdown.
       Google will ask for permission the first time:
         - Review permissions > choose your account
         - "Google hasn't verified this app" > Advanced >
           "Go to <project name> (unsafe)" > Allow
       This warning is normal for your own scripts.
       Check that a test row appeared and the email arrived.

   6.  Deploy > New deployment
         - Type: Web app  (click the gear icon next to "Select type")
         - Description: anything, e.g. "v1"
         - Execute as: Me
         - Who has access: ANYONE          <-- important, not "Anyone with Google account"
       Press Deploy, then copy the Web app URL. It looks like:
         https://script.google.com/macros/s/AKfycb.../exec

   7.  Paste that URL into index.html and contact.html, replacing
       PASTE_YOUR_APPS_SCRIPT_URL_HERE in the SDM_FORM_ENDPOINT line
       near the bottom of each file.

   8.  Push to GitHub and test the live form.

   IF YOU EDIT THIS SCRIPT LATER
   Deploy > Manage deployments > pencil icon > Version: New version > Deploy.
   Editing without redeploying changes nothing on the live site.

   LIMITS
   Free Google accounts can send about 100 notification emails per day.
   Sheet writes are effectively unlimited for this use case.
   ============================================================ */
