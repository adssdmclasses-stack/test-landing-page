#!/usr/bin/env python3
"""
Lakshyha Academy — landing page generator.

Builds one real static .html file per ad group URL from a single template,
so shared sections (fees, subjects, proof strip, FAQ, footer) are edited once.

    python3 build/generate.py

Output goes to the repo root. Commit the generated .html files — Vercel serves
them directly, no build step needed on their side.
"""

import os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =====================================================================
# SITE
# =====================================================================
SITE = {
    "domain": "https://vercel-test.sdmlabs.in",
    "gtm": "GTM-XXXXXXX",
    # Test domain: keep it out of the index so it never competes with the
    # client's real site. Google Ads serves noindex pages without any issue.
    # Flip to False the day you move to the client's own domain.
    "noindex": True,
}

# =====================================================================
# SHARED BLOCKS
# =====================================================================

PROOF_STRIP = """
<section class="strip">
  <div class="wrap">
    <div class="stat"><b>__ yrs</b><span>Teaching Class 10 in Bhopal</span></div>
    <div class="stat"><b>__%</b><span>Students scoring above 75% last board exam</span></div>
    <div class="stat"><b>20</b><span>Students maximum per batch</span></div>
    <div class="stat"><b>__+</b><span>Practice papers written before the board</span></div>
  </div>
</section>
"""

HOW_WE_TEACH = """
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">How we teach</span>
      <h2>The problem is rarely the child. It's usually the plan.</h2>
      <p>Most Class 10 students in Bhopal are attending coaching. Very few are being tracked week by week. That's the gap we fill.</p>
    </div>
    <div class="grid-3">
      <div class="tile"><span class="tag">Batch size</span><h3>20 students, not 60</h3><p>The teacher can name every student's weak chapter. In a hall of sixty, nobody can.</p></div>
      <div class="tile"><span class="tag">Testing</span><h3>A test every week</h3><p>Chapter test on Saturday, paper discussion on Monday. Marks go into a sheet you can see.</p></div>
      <div class="tile"><span class="tag">Doubts</span><h3>Daily doubt hour</h3><p>One fixed hour every day where students bring questions instead of carrying them home.</p></div>
      <div class="tile"><span class="tag">Parents</span><h3>Monthly parent meeting</h3><p>You see attendance, test scores and chapter progress on paper — not a vague "padh raha hai".</p></div>
      <div class="tile"><span class="tag">Revision</span><h3>Two full revisions</h3><p>Syllabus finishes early enough to revise everything twice before the board exam.</p></div>
      <div class="tile"><span class="tag">Papers</span><h3>Board pattern practice</h3><p>Previous years' papers and blueprint-based sets, written in exam conditions with timing.</p></div>
    </div>
  </div>
</section>
"""

SUBJECTS = """
<section class="sec sec-alt">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">Subjects covered</span>
      <h2>All five board subjects, one fee.</h2>
      <p>Numbered the way the board counts them, because that's the order the marksheet will.</p>
    </div>
    <div class="ledger">
      <div class="ledger-row"><span class="n">01</span><h3>Mathematics</h3><p>Concept building from Class 9 basics, then chapter-wise problem sets and full-length papers.</p></div>
      <div class="ledger-row"><span class="n">02</span><h3>Science</h3><p>Physics, Chemistry and Biology taught separately by subject, with diagram and numerical practice.</p></div>
      <div class="ledger-row"><span class="n">03</span><h3>Social Science</h3><p>Map work, dates and answer-writing structure — the marks most students leave on the table.</p></div>
      <div class="ledger-row"><span class="n">04</span><h3>English</h3><p>Grammar, unseen passages, letter and essay writing to a scoring format.</p></div>
      <div class="ledger-row"><span class="n">05</span><h3 class="hi">हिन्दी</h3><p>व्याकरण, अपठित गद्यांश और लेखन — बोर्ड पैटर्न के अनुसार अभ्यास।</p></div>
    </div>
  </div>
</section>
"""

FEES = """
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">Batches &amp; fees</span>
      <h2>Timings and fees, stated upfront.</h2>
      <p>Pick the slot that fits school hours. Seats per batch are capped, so the earlier batch usually fills first.</p>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Batch</th><th>Days</th><th>Timing</th><th>Seats left</th><th>Fee</th></tr></thead>
        <tbody>
          <tr><td>Morning</td><td>Mon–Sat</td><td>__:__ – __:__ AM</td><td>__</td><td><b>₹__,___</b> / year</td></tr>
          <tr><td>Evening</td><td>Mon–Sat</td><td>__:__ – __:__ PM</td><td>__</td><td><b>₹__,___</b> / year</td></tr>
          <tr><td>Weekend crash</td><td>Sat–Sun</td><td>__:__ – __:__</td><td>__</td><td><b>₹__,___</b></td></tr>
        </tbody>
      </table>
    </div>
    <p class="fee-note" data-fee-note>One-time registration ₹___ · Instalment option available</p>
  </div>
</section>
"""

QUOTES = """
<section class="sec sec-alt">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">What parents say</span>
      <h2>Ask the parents already sending their child here.</h2>
    </div>
    <div class="quotes">
      <div class="quote"><p>[Replace with a real parent quote — 2 to 3 lines, mention the subject that improved and the marks jump.]</p><footer><b>Parent name</b>Parent of Class 10 student · Area, Bhopal</footer></div>
      <div class="quote"><p>[Replace with a real parent quote — mention the weekly test reports or the doubt hour.]</p><footer><b>Parent name</b>Parent of Class 10 student · Area, Bhopal</footer></div>
      <div class="quote"><p>[Replace with a real student quote — what changed in their study routine.]</p><footer><b>Student name</b>Scored __% · MP Board 20__</footer></div>
    </div>
  </div>
</section>
"""

FAQ_BASE = """
    <details>
      <summary>Is the demo class really free?</summary>
      <p>Yes. Your child sits in a live class with the regular batch, and you meet the subject teacher afterwards. No fee, and no obligation to join.</p>
    </details>
    <details>
      <summary>My child has joined mid-session. Can they catch up?</summary>
      <p>Yes. We run a short diagnostic test first, then a catch-up plan for the chapters already covered, alongside the running batch.</p>
    </details>
    <details>
      <summary>How will I know if my child is actually improving?</summary>
      <p>Every weekly test is scored and recorded. You get the report at the monthly parent meeting, and on WhatsApp if you prefer.</p>
    </details>
    <details>
      <summary>Where exactly is the centre?</summary>
      <p><span data-address-inline>Address will appear here</span> — <a href="#" data-maps>open in Google Maps</a>.</p>
    </details>
    <details>
      <summary>Can the fee be paid in instalments?</summary>
      <p>Yes. Talk to us on the call and we'll set up a schedule that works around your other school payments.</p>
    </details>
"""

# =====================================================================
# PAGES — one per ad group. Add or delete freely.
# =====================================================================
PAGES = [
    {
        "slug": "index",
        "path": "/",
        "variant": "home",
        "title": "Class 10 Coaching in Bhopal | Lakshyha Academy — Free Demo Class",
        "desc": "Class 10 coaching in Bhopal for MP Board and CBSE. Small batches, weekly tests, daily doubt hour and monthly parent meetings. Book a free demo class.",
        "eyebrow": "Class 10 · MP Board &amp; CBSE · Bhopal",
        "h1": 'Board exams don\'t reward last-minute revision. They reward <em>a finished syllabus</em>.',
        "sub": "Lakshyha Academy runs small Class 10 batches in Bhopal with a chapter-wise plan, a test every week, and a teacher who knows exactly where your child is losing marks.",
        "pills": ["Max 20 students per batch", "Weekly chapter tests", "Daily doubt hour", "Monthly parent meeting"],
        "form_h": "Book a free demo class",
        "form_sub": "No fee, no commitment. Sit through one live class, meet the teacher, then decide.",
        "focus": """
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">Start here</span>
      <h2>Pick the batch that matches your child.</h2>
      <p>Boards are taught in separate batches because the paper pattern and marking differ. Open the one that applies to you.</p>
    </div>
    <div class="grid-3">
      <a class="tile tile-link" href="/mp-board-10th-coaching-bhopal"><span class="tag">MP Board</span><h3>MP Board Class 10 batch</h3><p>Blueprint weightage, MPBSE paper pattern, Hindi and English medium.</p></a>
      <a class="tile tile-link" href="/cbse-class-10-coaching-bhopal"><span class="tag">CBSE</span><h3>CBSE Class 10 batch</h3><p>NCERT plus exemplar, competency-based questions, internal assessment support.</p></a>
      <a class="tile tile-link" href="/class-10-maths-science-coaching-bhopal"><span class="tag">Two subjects</span><h3>Maths &amp; Science only</h3><p>Separate teachers for Physics, Chemistry and Biology. The percentage-deciding subjects.</p></a>
      <a class="tile tile-link" href="/class-10-crash-course-bhopal"><span class="tag">Short course</span><h3>Crash course</h3><p>Full revision and paper practice for the last few weeks before the board.</p></a>
      <a class="tile tile-link" href="/10th-class-coaching-bhopal"><span class="tag">Full year</span><h3>Regular 10th class coaching</h3><p>Mon to Sat, all five subjects, a test every week from day one.</p></a>
      <a class="tile tile-link" href="/class-10-tuition-near-me-bhopal"><span class="tag">Location</span><h3>Timings &amp; directions</h3><p>Morning and evening slots, with the centre location on the map.</p></a>
    </div>
  </div>
</section>
""",
        "faq_extra": """
    <details open>
      <summary>Do you teach MP Board and CBSE together?</summary>
      <p>No. Batches are separate because the syllabus, paper pattern and marking differ. Tell us the board when you book and we'll put you in the right demo.</p>
    </details>
""",
    },
    {
        "slug": "10th-class-coaching-bhopal",
        "path": "/10th-class-coaching-bhopal",
        "variant": "10th-core",
        "title": "10th Class Coaching in Bhopal | Small Batches, Weekly Tests — Lakshyha Academy",
        "desc": "10th class coaching in Bhopal with a maximum of 20 students per batch, a chapter test every week and a daily doubt hour. Book a free demo class today.",
        "eyebrow": "10th class coaching · Bhopal",
        "h1": '10th class coaching in Bhopal where the teacher <em>knows your child\'s weak chapter</em>.',
        "sub": "Twenty students a batch. A test every Saturday. A doubt hour every day. Sit through one free class before you decide anything.",
        "pills": ["Max 20 students", "Test every Saturday", "Daily doubt hour", "Mon–Sat batches"],
        "form_h": "Book a free demo class",
        "form_sub": "One live class with the regular batch, then a sit-down with the teacher. No fee.",
        "focus": """
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">A week at the centre</span>
      <h2>What actually happens, Monday to Saturday.</h2>
      <p>The order matters — the test comes before the discussion, and the discussion before the next chapter.</p>
    </div>
    <div class="ledger">
      <div class="ledger-row"><span class="n">MON</span><h3>New chapter starts</h3><p>Concept teaching, then board-pattern questions from the same chapter the same day.</p></div>
      <div class="ledger-row"><span class="n">TUE</span><h3>Practice + doubt hour</h3><p>Problem sets in class. Anything unfinished goes to the fixed doubt hour, not home.</p></div>
      <div class="ledger-row"><span class="n">WED</span><h3>Second subject block</h3><p>Rotating schedule so no subject goes more than two days without a class.</p></div>
      <div class="ledger-row"><span class="n">THU</span><h3>Previous year questions</h3><p>Whatever the board has actually asked from this chapter in the last ten years.</p></div>
      <div class="ledger-row"><span class="n">FRI</span><h3>Revision + test prep</h3><p>Quick recap and the exact syllabus for tomorrow's test, written on the board.</p></div>
      <div class="ledger-row"><span class="n">SAT</span><h3>Chapter test</h3><p>Written under exam conditions. Marks recorded, paper returned with corrections on Monday.</p></div>
    </div>
  </div>
</section>
""",
        "faq_extra": """
    <details open>
      <summary>How is this different from a big coaching hall?</summary>
      <p>Batch size. In a hall of sixty, a student who stays quiet stays invisible for months. At twenty, the teacher notices in the first week and tells you at the parent meeting.</p>
    </details>
""",
    },
    {
        "slug": "mp-board-10th-coaching-bhopal",
        "path": "/mp-board-10th-coaching-bhopal",
        "variant": "mp-board",
        "title": "MP Board Class 10 Coaching in Bhopal | Blueprint-Based Preparation",
        "desc": "MP Board Class 10 coaching in Bhopal. Separate MPBSE batch, blueprint-based papers, previous years' question practice, Hindi and English medium. Free demo class.",
        "eyebrow": "MP Board · Class 10 · Bhopal",
        "h1": 'MP Board Class 10 coaching, taught to <em>the MPBSE blueprint</em>.',
        "sub": "A separate MP Board batch — chapter weightage from the official blueprint, previous years' papers, and answer writing in the medium your child studies in.",
        "pills": ["MP Board batch only", "Blueprint weightage", "Hindi &amp; English medium", "Previous 10 years' papers"],
        "form_h": "Book a free MP Board demo class",
        "form_sub": "Tell us the medium and we'll put your child in the right batch for the demo.",
        "focus": """
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">MP Board specifics</span>
      <h2>Taught for the paper your child will actually write.</h2>
      <p>MPBSE marks differently from CBSE. Preparing for the wrong pattern costs marks even when the concepts are clear.</p>
    </div>
    <div class="grid-3">
      <div class="tile"><span class="tag">Weightage</span><h3>Blueprint-led chapter time</h3><p>Chapters get classroom time in proportion to the marks MPBSE gives them, not equal time each.</p></div>
      <div class="tile"><span class="tag">Medium</span><h3>Hindi and English medium</h3><p>Terminology and answer writing practised in the medium your child will write the paper in.</p></div>
      <div class="tile"><span class="tag">Papers</span><h3>Ten years of question papers</h3><p>Repeated questions get flagged so students recognise them in the exam hall.</p></div>
      <div class="tile"><span class="tag">Answer writing</span><h3>Marks-per-point discipline</h3><p>How long a 3-mark answer should be, and where examiners stop reading.</p></div>
      <div class="tile"><span class="tag">Practicals</span><h3>Practical and project marks</h3><p>The internal marks most students treat casually and then miss the distinction by.</p></div>
      <div class="tile"><span class="tag">Timing</span><h3>Full paper in three hours</h3><p>Timed full-length papers so nobody discovers the timing problem on exam day.</p></div>
    </div>
  </div>
</section>
""",
        "faq_extra": """
    <details open>
      <summary>Do you teach in Hindi medium?</summary>
      <p>Yes. MP Board batches run in both Hindi and English medium. Mention the medium when you book so the demo class matches.</p>
    </details>
""",
    },
    {
        "slug": "cbse-class-10-coaching-bhopal",
        "path": "/cbse-class-10-coaching-bhopal",
        "variant": "cbse",
        "title": "CBSE Class 10 Coaching in Bhopal | NCERT + Exemplar Practice",
        "desc": "CBSE Class 10 coaching in Bhopal. Separate CBSE batch covering NCERT and exemplar problems, competency-based questions and internal assessment support. Free demo class.",
        "eyebrow": "CBSE · Class 10 · Bhopal",
        "h1": 'CBSE Class 10 coaching aligned to <em>the NCERT chapter plan</em>.',
        "sub": "A separate CBSE batch — NCERT worked line by line, exemplar problems for the hard questions, and practice on the case-based questions students lose most marks on.",
        "pills": ["CBSE batch only", "NCERT + exemplar", "Case-based questions", "Internal assessment support"],
        "form_h": "Book a free CBSE demo class",
        "form_sub": "One live class with the CBSE batch, then a conversation with the subject teacher.",
        "focus": """
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">CBSE specifics</span>
      <h2>The 20 internal marks matter as much as the 80.</h2>
      <p>CBSE splits every subject between the board paper and school assessment. We prepare for both.</p>
    </div>
    <div class="grid-3">
      <div class="tile"><span class="tag">Internal 20</span><h3>Periodic tests and portfolio</h3><p>Support for the school's periodic tests, notebook submission and subject enrichment marks.</p></div>
      <div class="tile"><span class="tag">Board 80</span><h3>NCERT first, then exemplar</h3><p>Every NCERT question solved, then exemplar problems for the difficulty CBSE now sets.</p></div>
      <div class="tile"><span class="tag">Competency</span><h3>Case-based and assertion-reason</h3><p>The newer question types that catch out students trained only on direct questions.</p></div>
      <div class="tile"><span class="tag">Papers</span><h3>CBSE sample papers</h3><p>Official sample papers and marking schemes, written to time and marked to the scheme.</p></div>
      <div class="tile"><span class="tag">Standard</span><h3>Basic vs standard Maths</h3><p>An honest recommendation on which paper your child should opt for, based on test data.</p></div>
      <div class="tile"><span class="tag">School fit</span><h3>Works alongside school</h3><p>Timings that leave room for school homework instead of competing with it.</p></div>
    </div>
  </div>
</section>
""",
        "faq_extra": """
    <details open>
      <summary>Do you cover school internal assessments too?</summary>
      <p>Yes. Periodic tests, notebook work and subject enrichment carry 20 marks per subject. We prepare for those alongside the board paper.</p>
    </details>
""",
    },
    {
        "slug": "class-10-maths-science-coaching-bhopal",
        "path": "/class-10-maths-science-coaching-bhopal",
        "variant": "maths-science",
        "title": "Class 10 Maths &amp; Science Coaching in Bhopal | Separate Subject Teachers",
        "desc": "Class 10 Maths and Science coaching in Bhopal. Physics, Chemistry and Biology taught by separate subject teachers, with numerical and diagram practice. Free demo class.",
        "eyebrow": "Maths &amp; Science · Class 10 · Bhopal",
        "h1": 'Maths and Science, taught by <em>separate subject teachers</em>.',
        "sub": "These two subjects decide the percentage. Physics, Chemistry and Biology each get their own teacher here — not one generalist covering all three.",
        "pills": ["Separate P/C/B teachers", "Numerical practice", "Diagram marks", "NCERT + previous years"],
        "form_h": "Book a free Maths or Science demo",
        "form_sub": "Pick the subject you're worried about. Your child sits in that class free.",
        "focus": """
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">Where the marks go</span>
      <h2>Most students don't lose marks on the hard chapters.</h2>
      <p>They lose them on units they were taught quickly, by a teacher covering three subjects at once.</p>
    </div>
    <div class="grid-3">
      <div class="tile"><span class="tag">Maths</span><h3>Concepts from Class 9 up</h3><p>Algebra and geometry gaps from last year get fixed before this year's chapters are built on them.</p></div>
      <div class="tile"><span class="tag">Physics</span><h3>Numericals, not just formulae</h3><p>Light, electricity and magnetism drilled with numerical sets until the method is automatic.</p></div>
      <div class="tile"><span class="tag">Chemistry</span><h3>Equations and reactions</h3><p>Balancing, reaction types and the carbon chapter, with equation-writing practice every class.</p></div>
      <div class="tile"><span class="tag">Biology</span><h3>Diagrams score</h3><p>Labelled diagram practice — the fastest marks in the paper and the ones most often lost.</p></div>
      <div class="tile"><span class="tag">Tests</span><h3>Unit-wise testing</h3><p>A test per unit, so a weak unit is caught in a week instead of at the pre-board.</p></div>
      <div class="tile"><span class="tag">Papers</span><h3>Full-length practice</h3><p>Board-pattern papers under timing, with the answer sheet returned and corrected.</p></div>
    </div>
  </div>
</section>
""",
        "faq_extra": """
    <details open>
      <summary>Can we join for Maths and Science only?</summary>
      <p>Yes. There's a two-subject option if your child is comfortable in the languages and Social Science. Ask about the fee for it on the call.</p>
    </details>
""",
    },
    {
        "slug": "class-10-tuition-near-me-bhopal",
        "path": "/class-10-tuition-near-me-bhopal",
        "variant": "near-me",
        "title": "Class 10 Tuition Near You in Bhopal | Morning &amp; Evening Batches",
        "desc": "Class 10 tuition in Bhopal with morning and evening batches, six days a week. Small batches, weekly tests, and a free demo class. Check timings and directions.",
        "eyebrow": "Class 10 tuition · Bhopal",
        "h1": 'Class 10 tuition in Bhopal, at a time that <em>fits around school</em>.',
        "sub": "Morning and evening batches, Monday to Saturday. Small groups, a test every week, and a centre you can actually get to without a long commute.",
        "pills": ["Morning &amp; evening slots", "Monday to Saturday", "Max 20 per batch", "Free demo class"],
        "form_h": "Check timings for your area",
        "form_sub": "Tell us your area in Bhopal and we'll suggest the batch with the easiest commute.",
        "focus": """
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">Getting here</span>
      <h2>One centre, two slots, six days a week.</h2>
      <p>Students currently travel in from across Bhopal. Pick the slot that leaves the commute outside peak school traffic.</p>
    </div>
    <div class="grid-3">
      <div class="tile"><span class="tag">Location</span><h3>Where we are</h3><p><span data-address-inline>Address appears here</span>. <a href="#" data-maps>Open in Google Maps →</a></p></div>
      <div class="tile"><span class="tag">Morning batch</span><h3>Before school hours</h3><p>__:__ to __:__ AM, Monday to Saturday. Suits students with afternoon school shifts.</p></div>
      <div class="tile"><span class="tag">Evening batch</span><h3>After school hours</h3><p>__:__ to __:__ PM, Monday to Saturday. The batch that fills first every session.</p></div>
      <div class="tile"><span class="tag">Areas</span><h3>Students come from</h3><p>__________, __________, __________ and nearby areas. [List 4–6 real areas.]</p></div>
      <div class="tile"><span class="tag">Parking</span><h3>Drop-off and pickup</h3><p>[Describe parking or the safe drop-off point — parents ask this on every call.]</p></div>
      <div class="tile"><span class="tag">Safety</span><h3>Attendance messaged</h3><p>You get told the same day if your child doesn't reach class.</p></div>
    </div>
  </div>
</section>
""",
        "faq_extra": """
    <details open>
      <summary>Which areas of Bhopal do your students come from?</summary>
      <p>Mostly __________, __________ and __________. If you're further out, ask about the weekend batch — fewer trips, same syllabus coverage.</p>
    </details>
""",
    },
    {
        "slug": "class-10-crash-course-bhopal",
        "path": "/class-10-crash-course-bhopal",
        "variant": "crash-course",
        "title": "Class 10 Crash Course in Bhopal | Full Revision Before the Board Exam",
        "desc": "Class 10 crash course in Bhopal: full syllabus revision, chapter weightage, and timed board-pattern papers before the exam. Limited seats. Book a free demo class.",
        "eyebrow": "Crash course · Class 10 · Bhopal",
        "h1": 'A crash course that spends the last weeks on <em>what the paper actually asks</em>.',
        "sub": "Full revision in weightage order, previous years' questions, and enough timed papers that your child stops losing marks to the clock.",
        "pills": ["Full syllabus revision", "Timed board-pattern papers", "Weightage-first order", "Limited seats"],
        "form_h": "Book a crash course seat",
        "form_sub": "Seats are capped at 20. Book the free demo and we'll tell you honestly whether the crash course is the right fit.",
        "focus": """
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">The plan</span>
      <h2>Four phases, in this order.</h2>
      <p>Sequence is the whole point of a crash course. Revising alphabetically instead of by weightage wastes the weeks that are left.</p>
    </div>
    <div class="ledger">
      <div class="ledger-row"><span class="n">01</span><h3>Diagnostic test</h3><p>One paper per subject to find out what's actually missing. Nothing gets revised blind.</p></div>
      <div class="ledger-row"><span class="n">02</span><h3>High-weightage chapters first</h3><p>The chapters carrying the most marks get taught and tested before anything else.</p></div>
      <div class="ledger-row"><span class="n">03</span><h3>Previous years' questions</h3><p>Ten years of papers, sorted by chapter, with the repeated questions marked.</p></div>
      <div class="ledger-row"><span class="n">04</span><h3>Timed full-length papers</h3><p>Full papers in three hours, corrected and returned, until the timing stops being a problem.</p></div>
    </div>
  </div>
</section>
""",
        "faq_extra": """
    <details open>
      <summary>Is a crash course enough if my child hasn't studied all year?</summary>
      <p>Honestly, it depends how much is missing — the diagnostic test tells us in one sitting. If a crash course won't be enough, we'll say so instead of taking the fee.</p>
    </details>
""",
    },
]

# =====================================================================
# TEMPLATE
# =====================================================================
TEMPLATE = """<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{domain}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{domain}{path}">
<meta property="og:type" content="website">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+Devanagari:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css">

<!-- GOOGLE TAG MANAGER -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});
var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;
j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{gtm}');</script>

<!-- page variant, available to GTM before anything else fires -->
<script>window.dataLayer=window.dataLayer||[];window.dataLayer.push({{page_variant:'{variant}'}});</script>

<!-- GTB CLICK CAPTURE JS v1.2.1 (Techysoar) — drop the file in and uncomment -->
<!-- <script src="/assets/gtb-click-capture.js"></script> -->
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

<header class="topbar">
  <div class="wrap">
    <a class="brand" href="/"><b>Lakshyha Academy</b><span>Bhopal</span></a>
    <a class="topbar-call" href="#" data-call>
      <span aria-hidden="true">&#128222;</span>
      <span class="lbl" data-phone-text></span>
      <span class="sr">Call Lakshyha Academy</span>
    </a>
  </div>
</header>

<section class="hero on-board">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">{eyebrow}</span>
      <h1>{h1}</h1>
      <p class="hero-sub">{sub}</p>
      <ul class="pills">{pills}</ul>
      <div class="hero-actions">
        <a class="btn btn-call" href="#" data-call>Call now — talk to a teacher</a>
        <a class="btn btn-ghost" href="#demo">Book a free demo class</a>
      </div>

      <div class="countdown">
        <div class="countdown-label" data-cd-label>Time left until the Class 10 board exam</div>
        <div class="cd-row">
          <div class="cd-big" data-cd-days>&mdash;</div>
          <div class="cd-unit">days</div>
          <p class="cd-note">That's roughly <b data-cd-weeks>&mdash;</b> weeks to cover the full syllabus, revise it twice, and write enough practice papers to stop making silly mistakes.</p>
        </div>
        <div class="cd-track" data-cd-track aria-hidden="true"></div>
      </div>
    </div>

    <div class="card" id="demo">
      <h2>{form_h}</h2>
      <p class="card-sub">{form_sub}</p>
      <div class="form-msg" data-form-msg role="alert"></div>

      <form id="lead-form" novalidate>
        <div class="field">
          <label for="name">Student or parent name</label>
          <input type="text" id="name" name="name" autocomplete="name" placeholder="Full name" required>
          <span class="err">Please enter a name.</span>
        </div>
        <div class="field">
          <label for="phone">Mobile number (WhatsApp)</label>
          <input type="tel" id="phone" name="phone" inputmode="numeric" autocomplete="tel" placeholder="10-digit mobile number" maxlength="10" required>
          <span class="err">Enter a valid 10-digit Indian mobile number.</span>
        </div>
        <div class="field">
          <label for="email">Email (optional &mdash; for the study plan PDF)</label>
          <input type="email" id="email" name="email" autocomplete="email" placeholder="you@example.com">
          <span class="err">Please check the email address.</span>
        </div>
        <div class="field">
          <label for="board">Which board?</label>
          <select id="board" name="board" required>
            <option value="">Select board</option>
            <option value="MP Board">MP Board</option>
            <option value="CBSE">CBSE</option>
            <option value="ICSE">ICSE</option>
            <option value="Not sure">Not sure yet</option>
          </select>
          <span class="err">Please select a board.</span>
        </div>
        <div class="field">
          <label for="area">Area in Bhopal</label>
          <input type="text" id="area" name="area" placeholder="e.g. Kolar, Ayodhya Bypass, MP Nagar">
        </div>

        <label class="consent">
          <input type="checkbox" id="consent" name="consent" required>
          <span>I agree to be contacted by Lakshyha Academy on call and WhatsApp about admissions. See our <a href="/privacy.html">privacy policy</a>.</span>
        </label>

        <!-- GTB Method A hidden fields — do not remove -->
        <input type="hidden" name="gclid" id="gclid">
        <input type="hidden" name="gbraid" id="gbraid">
        <input type="hidden" name="wbraid" id="wbraid">
        <input type="hidden" name="utm_source" id="utm_source">
        <input type="hidden" name="utm_medium" id="utm_medium">
        <input type="hidden" name="utm_campaign" id="utm_campaign">
        <input type="hidden" name="utm_term" id="utm_term">
        <input type="hidden" name="utm_content" id="utm_content">
        <input type="hidden" name="session_attributes" id="session_attributes">
        <input type="hidden" name="page_url" id="page_url">
        <input type="hidden" name="submitted_at" id="submitted_at">
        <input type="hidden" name="page_variant" id="page_variant" value="{variant}">

        <button type="submit" class="btn btn-primary" data-submit>Book my free demo class</button>
      </form>

      <div class="card-alt">Prefer to talk first? <a href="#" data-whatsapp>Message us on WhatsApp</a></div>
    </div>
  </div>
</section>
{proof}
{focus}
{how}
{subjects}
{fees}
{quotes}
<section class="sec">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow">Questions parents ask</span>
      <h2>Before you book the demo.</h2>
    </div>
{faq_extra}{faq_base}  </div>
</section>

<section class="close-cta">
  <div class="wrap close-grid">
    <div>
      <span class="eyebrow">Admissions open</span>
      <h2>One free class is enough to judge a coaching centre.</h2>
      <p>Book it for this week. Bring your child's last report card if you have it &mdash; the teacher will tell you exactly where the marks are leaking.</p>
      <div class="hero-actions" style="margin-top:22px">
        <a class="btn btn-call" href="#" data-call>Call now</a>
        <a class="btn btn-primary" href="#demo">Book free demo class</a>
      </div>
      <div class="addr">
        <span data-address1></span><br>
        <span data-address2></span><br>
        <a href="#" data-maps>Get directions &rarr;</a>
      </div>
    </div>
    <div>
      <div class="card" style="box-shadow:none">
        <h2 style="font-size:1.25rem">Prefer WhatsApp?</h2>
        <p class="card-sub">Send us your child's board and class, and we'll share batch timings and fees straight away.</p>
        <a class="btn btn-primary" href="#" data-whatsapp>Message on WhatsApp</a>
      </div>
    </div>
  </div>
</section>

<footer class="site">
  <div class="wrap">
    <span>&copy; <span data-year></span> Lakshyha Academy, Bhopal. All rights reserved.</span>
    <nav class="foot-nav">
      <a href="/10th-class-coaching-bhopal">10th class coaching</a>
      <a href="/mp-board-10th-coaching-bhopal">MP Board</a>
      <a href="/cbse-class-10-coaching-bhopal">CBSE</a>
      <a href="/class-10-maths-science-coaching-bhopal">Maths &amp; Science</a>
      <a href="/class-10-crash-course-bhopal">Crash course</a>
      <a href="/class-10-tuition-near-me-bhopal">Timings</a>
    </nav>
    <span><a href="/privacy.html">Privacy policy</a> &middot; <a href="/terms.html">Terms</a></span>
  </div>
</footer>

<nav class="mobile-bar" aria-label="Quick actions">
  <a class="m-call" href="#" data-call>Call now</a>
  <a class="m-form" href="#demo">Free demo</a>
</nav>

<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"EducationalOrganization","name":"Lakshyha Academy","description":"{desc}","url":"{domain}{path}","areaServed":"Bhopal, Madhya Pradesh","address":{{"@type":"PostalAddress","addressLocality":"Bhopal","addressRegion":"MP","addressCountry":"IN"}}}}
</script>

<script src="/assets/config.js"></script>
<script src="/assets/app.js"></script>
</body>
</html>
"""


def build():
    robots = "noindex,nofollow" if SITE["noindex"] else "index,follow"
    written = []
    for p in PAGES:
        html = TEMPLATE.format(
            title=p["title"], desc=p["desc"], robots=robots,
            domain=SITE["domain"], path=p["path"], gtm=SITE["gtm"],
            variant=p["variant"], eyebrow=p["eyebrow"], h1=p["h1"], sub=p["sub"],
            pills="".join("<li>%s</li>" % x for x in p["pills"]),
            form_h=p["form_h"], form_sub=p["form_sub"],
            proof=PROOF_STRIP, focus=p["focus"], how=HOW_WE_TEACH,
            subjects=SUBJECTS, fees=FEES, quotes=QUOTES,
            faq_extra=p["faq_extra"], faq_base=FAQ_BASE,
        )
        out = os.path.join(ROOT, p["slug"] + ".html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        written.append(p)
        print("  wrote", p["slug"] + ".html", "->", p["path"])

    # sitemap
    today = datetime.date.today().isoformat()
    urls = "".join(
        '  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n'
        % (SITE["domain"], p["path"], today, "1.0" if p["path"] == "/" else "0.8")
        for p in written
    )
    urls += '  <url><loc>%s/privacy.html</loc><priority>0.1</priority></url>\n' % SITE["domain"]
    urls += '  <url><loc>%s/terms.html</loc><priority>0.1</priority></url>\n' % SITE["domain"]
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
    print("  wrote sitemap.xml")

    # robots.txt — block organic crawlers on the test domain, always allow AdsBot
    if SITE["noindex"]:
        body = ("# Test domain — kept out of organic search.\n"
                "# AdsBot must stay allowed or Google Ads cannot check the landing page.\n"
                "User-agent: AdsBot-Google\nAllow: /\n\n"
                "User-agent: AdsBot-Google-Mobile\nAllow: /\n\n"
                "User-agent: *\nDisallow: /\n")
    else:
        body = ("User-agent: *\nAllow: /\nDisallow: /thank-you.html\n\n"
                "Sitemap: %s/sitemap.xml\n" % SITE["domain"])
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(body)
    print("  wrote robots.txt (noindex=%s)" % SITE["noindex"])

    print("\nDone. %d landing pages built for %s" % (len(written), SITE["domain"]))


if __name__ == "__main__":
    build()
