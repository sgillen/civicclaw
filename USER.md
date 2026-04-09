# USER.md — Your Civic Digest Profile

This file tells the agent who it's writing for. It shapes editorial tone, what gets highlighted vs. condensed, and how actionable the output is. Every report should feel like it was written *for this person*, not for a generic civic-minded audience.

**If this file is missing or left empty, reports default to neutral tone with no filtering preferences.**

---

## My Neighborhood

**District:** 5
**Supervisor:** Bilal Mahmood
**Neighborhoods:** NOPA, Western Addition, Hayes Valley, Lower Haight
**Streets I care about:** Divisadero St, Fillmore St, Golden Gate Ave, Oak St, Fell St
**Addresses to watch:** 400 Divisadero St (203-unit AB 2011 project, approved Dec 2024, no permits yet)
**People to flag:** Mahmood, 4Terra Investments, Dean Preston

---

## Me

- **Neighborhood:** NOPA (District 5)
- **How I get around:** Walk, bike, Muni — no car. Transit and bike infrastructure matter directly.
- **Background:** Software engineer / ML researcher (NVIDIA robotics). Technical — don't simplify.

---

## What I Care About

**Housing:** Pro-building. The question is always "why isn't this getting built faster." 400 Divisadero is on the watchlist but only mention it when there's actual new activity (permit filed, construction started, status change) — not every week as a "still nothing" item. Flag stalled projects, cancellations, and anything that constrains the pipeline (landmark designations, discretionary review, permit delays).

**Transit & streets:** Pedestrian and cyclist lens. Parking policy matters when it affects how streets work for people not in cars. Muni reliability, bike lanes, Vision Zero.

**Civic engagement:** I want to show up to hearings. Tell me what's happening, why I'd care, and what I'd say. Include specific dates, email addresses, item numbers.


---

## What I Don't Care About

- Minor residential permits (reroofing, windows, decks) — skip entirely
- Meetings with no agenda and nothing to say about them — omit, don't mention
- Out-of-district items unless they set a precedent that directly affects D5
- "Nothing to report" placeholders — if a section is empty, cut it

---

## How I Want Reports Written

**Depth:** Technical background. Editorialize. Give me your read on what's actually going on, not just what happened.

**Format:** Narrative with through-lines, not section-by-section data dumps. Connect the dots across sources.

**Actions:** Every time-sensitive item (hearing, town hall, cleanup, comment deadline) goes in Potential Actions with: what it is, why I'd care, what to do. Don't bury actions in body sections.

**Tone:** Neutral language, editorial judgment. Curate what matters, explain why I should care, connect dots across sources — but let me form my own conclusions. Don't be punchy or write headlines that have already decided the answer. Pro-tech, pro-building, pro-transit as a lens for what's worth flagging, not as a rhetorical stance.

---

## Framing Preferences

These override the default STYLE.md framing. They tell the agent *how I think about* these topics.

**Housing: "why isn't this built yet."** Not "should this be built" or "developers seek approvals." I'm pro-building. The question is always what's constraining the pipeline. Flag cancellations, stalled projects, landmark designations that block density.

**Transit: pedestrian/cyclist lens.** I'm car-free. Parking policy matters when it changes how streets work for people walking and biking, not for drivers' convenience.

**Lobbying: don't frame it as adversarial.** I work in tech. Lobbying is how industries engage with government — it's notable when the volume is unusual, not inherently sinister. Note the volume, explain the business logic, ask whether the policy makes sense. Don't default to "corporations buying influence."

**Out-of-district items:** I also follow Castro, Mission, Duboce Triangle, Haight Ashbury, Lower Haight, and Golden Gate Park. Surface notable items from these neighborhoods (landmark blitzes, major housing projects, precedent-setting votes) but give them less weight than D5 items. Think "FYI" not "action item." Everything else: skip unless it sets a citywide precedent.

**Board of Supervisors:** Don't just list what passed. Look for patterns, contradictions, and dollar amounts buried in routine items.

---

## Developer Mode

**I'm the developer of this skill.** Include a `🔧 Dev Notes` section at the end of every report with:
- Meetings that appeared in the data but had no agenda or nothing actionable (so I know the scraper found them)
- Items that hit a relevance filter but weren't clear enough to include in the main report
- Any data sources that returned empty or errored

This section is for me only. Users like Tom or Fraser should have a USER.md without this section — they get the clean report.
