/**
 * Lakshyha Academy — lead capture endpoint (Google Apps Script)
 *
 * SETUP
 * 1. Create a new Google Sheet. Rename tab 1 to: Leads
 * 2. Extensions > Apps Script. Paste this file. Save.
 * 3. Run setupHeaders() once (authorise when prompted).
 * 4. Deploy > New deployment > Web app
 *      Execute as:      Me
 *      Who has access:  Anyone
 * 5. Copy the /exec URL into assets/config.js  →  formEndpoint
 *
 * The 14-column layout matches the GTB Path B sheet spec closely enough to
 * feed Google Ads Data Manager. Confirm column names against the blueprint
 * before you connect Data Manager or Pabbly.
 */

var SHEET_NAME = 'Leads';
var NOTIFY_EMAIL = '';   // optional: put an email here for instant lead alerts

var HEADERS = [
  'submitted_at','name','phone','email','board','area','consent','page_variant',
  'gclid','gbraid','wbraid','utm_source','utm_medium','utm_campaign','page_url'
];

function setupHeaders() {
  var sh = _sheet();
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold').setBackground('#0E2A26').setFontColor('#F4F6F1');
    sh.setFrozenRows(1);
  }
}

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    var sh = _sheet();
    if (sh.getLastRow() === 0) setupHeaders();

    var row = HEADERS.map(function (h) {
      if (h === 'submitted_at') return d.submitted_at || new Date().toISOString();
      return d[h] || '';
    });
    sh.appendRow(row);

    if (NOTIFY_EMAIL) {
      MailApp.sendEmail({
        to: NOTIFY_EMAIL,
        subject: 'New Class 10 demo lead — ' + (d.name || 'no name'),
        body: 'Name: ' + (d.name || '') +
              '\nPhone: ' + (d.phone || '') +
              '\nBoard: ' + (d.board || '') +
              '\nArea: ' + (d.area || '') +
              '\nCampaign: ' + (d.utm_campaign || '(none)') +
              '\nLanding page: ' + (d.page_variant || '(none)') +
              '\ngclid: ' + (d.gclid || '(none)')
      });
    }
    return _json({ ok: true });
  } catch (err) {
    return _json({ ok: false, error: String(err) });
  }
}

function doGet() { return _json({ ok: true, msg: 'Lakshyha Academy lead endpoint is live.' }); }

function _sheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
}

function _json(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
