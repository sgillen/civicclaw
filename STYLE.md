# CivicClaw Report Style Guide

Rules first, then examples. Rules are things we're sure about. Examples show what the rules look like in practice. Both evolve — if a rule doesn't hold, update it.

Reference: generate a sample digest to see these rules in practice.

---

## Rules

1. **TLDR first. Assume most people stop here.** 5-7 bullets, one sentence each. This IS the report for most readers. Make every bullet count. **The TLDR is summary only — no action items here.** Citywide news (budget, major policy, elections) belongs in the TLDR when it's genuinely big — but district-specific items take priority. Don't let citywide headlines crowd out what's happening on the reader's block.
2. **Potential actions section immediately after TLDR.** This is the second thing people read, and for many the most useful. Header: `## Potential Actions`. Structure:

   **Every digest must have a featured action.** If there's a hearing, a comment deadline, a cleanup, or anything else actionable this week — pick the best one and feature it. If nothing is time-sensitive this week, feature the best standing action (constituent meeting, petition, upcoming deadline). If there is genuinely nothing — no hearings, no cleanups, no open comment periods — say so explicitly: "No meetings or actions this week." Don't omit the section; state the absence. No digest ships without addressing this.

   **Lead with one featured action** — the single highest-impact or lowest-effort thing the reader can do. Give it a bold header and the full three-part treatment: (1) **What's happening** — the specific policy change or event in plain language, (2) **Why you'd care** — connect it to the reader's life, explain trade-offs, enough context to form an opinion, (3) **What you can do** — email address, deadline, item numbers, how to comment. This is the one you'd text a friend about.

   **Always show every action.** Every hearing, every comment period, every cleanup, every petition — list them all below the featured one. Nothing gets cut for space. The reader decides what's worth their time; the digest's job is to make sure they've seen everything. A short week with one cleanup is still a full list.
   - **Hearings & comment periods** — planning, SFMTA, Board of Appeals, HPC, Rent Board. Say what's actually changing, not just "a hearing is happening."
   - **Community cleanups** — from `sf_volunteer_cleanups.py`. Date, time, location. These are the easiest, lowest-barrier actions — always include them.
   - **Constituent meetings** — if there's an open window to meet your supervisor
   - **Ballot/petition drives** — if active

   This section replaces the old action calendar at the bottom — bring actions to the top where people see them.

   **Run all sources before writing.** The Potential Actions section must be assembled after running every script, not drafted from partial data. SFMTA hearings (`sfmta_hearings.py`), planning commission (`sf_planning_commission.py`), board of appeals (`sf_board_of_appeals.py`), and volunteer cleanups (`sf_volunteer_cleanups.py`) are all action sources — run them first, then write the section. A hearing found in a follow-up question is a failure mode, not a normal Q&A flow.
3. **Two things must stand out above all else:** What did my elected officials actually do? And what can I do about it? Everything else is context for those two questions.
4. **Officials box right after the potential actions — YOUR officials only.** These are the people the reader directly votes for: district supervisor, mayor, DA, City Attorney, state Assembly/Senate, US House/Senate. One-line summary of what each did this period. If they did nothing notable, leave them out. **Political actors** the reader doesn't elect (Board President, other supervisors, agency heads, commission members) appear in the narrative when they do something relevant — not in the officials box. Mandelman scheduling a landmark blitz is a story, not an accountability line item.
5. **Don't repeat the TLDR in sections.** If the TLDR already covers it, the section should add NEW detail or skip entirely. The reader already read the bullet — don't make them read it again in paragraph form. Sections exist for people who want to zoom in, not for restating what's above.
6. **Short reports.** The whole report should be scannable in 2 minutes. 3-5 sentences per section max. Housing pipeline gets a 1-2 sentence summary unless something unusual happened (major cancellation cluster, stalled project with new activity, policy change). Don't list every project and its status — that's data, not narrative. Clear headers. Scan-and-skip.
7. **Every action item needs an actual action.** Don't just list what's happening — say what the reader can do. Usually that's "public comment open at the hearing" or an email address. A 2-minute email beats attending a 3-hour hearing — say so. Be specific (date, email address, item number). Frame as nudges, not demands: "if you want to weigh in" not "you should show up." **For ambiguous items, explain the trade-off and let the reader decide.**
8. **Rates over counts.** "41/day" or "up 15%" beats "2,843 total."
9. **311 and eviction data are monthly, not weekly.** Weekly 311 counts and eviction filings are noisy — small numbers swing wildly and "up 33%" from 6 to 8 isn't a story. Include 311 pulse and eviction sections in monthly/quarterly reports only. In weekly reports, only mention 311 or evictions if there's a genuine anomaly (e.g., sewer reports up 10x in one corridor, Ellis Act cluster in a single block). When included, use this format:
   > 📞 311 — N reports across X spiking categories (30 days)
   > • Category: count (+Y% vs prior month)
   > • Category: count (flat)
   > • X more categories spiking
   Always show top 4 by count with trend. Summarize the rest with a count.
10. **Locate geographically.** "Jones Street corridor" not "District 5."
11. **Connect threads across sources.** Lobbying + permits + 311 + journalism = one story, not four sections.
12. **Neutral language, editorial judgment.** Curate aggressively — decide what matters, connect the dots, explain why the reader should care. But write in neutral language, and stop when you've stated the fact and its consequence. Don't editorialize beyond that. "40+ landmark designations this quarter — each one adds preservation constraints that make demolition or major alteration harder" is the right stopping point. Don't add "whether that's clearing a backlog or systematically constraining the corridor..." — the reader can see the implication. And don't write punchy headlines that have already decided the answer: "the corridor keeps getting harder to build one vote at a time" has already picked a villain. State the fact, state the consequence, stop.
13. **Framing comes from USER.md.** Housing lens, transit lens, lobbying stance, out-of-district filtering — all defined per-user in their profile. If USER.md has framing preferences, follow them. If not, default to neutral.
14. **Cut empty sections.** If there's no signal, don't include a "nothing to report" placeholder.
15. **Cut minor permits.** Reroofing, windows, decks → one summary line at most. If nothing notable was filed, don't write a "Nothing Happening" section — the TLDR already said it.
16. **No infrastructure excuses in the narrative.** "RSS only covers 5 days" goes in a footnote or nowhere.
17. **The user can ask for details.** The report doesn't need to be exhaustive. It needs to be interesting. If someone wants the full permit list or 311 breakdown, they'll ask. Don't preemptively dump it.
18. **The test:** Would this person text a friend about this? If not, cut it or rewrite it.
19. **No upcoming meetings section.** If a meeting isn't actionable enough to be in Potential Actions, it doesn't belong in the report at all. Don't write a calendar of meetings with no agenda — that's noise. Every meeting that appears in the report should be in the Actions section with a concrete action (usually: "public comment open at the hearing").
20. **Every time-sensitive item belongs in Potential Actions.** Town halls, hearings, comment periods, cleanups — all of it. Don't bury actionable items in body sections. If there's a date and a place, it's an action. Give it the full treatment: what it is, why you'd care, what to do.
21. **Out-of-district items: check USER.md first.** If the user lists watched neighborhoods or districts outside their own, surface notable items from those areas — but at lower weight than in-district items. Think "FYI" not "action item." Items from unwatched districts only appear if they set citywide precedent. When in doubt, cut it.
22. **Every district report is self-contained.** A reader should never need to also read the citywide report. After district-specific sections (311 pulse, evictions, permits, supervisor activity, local actions), include a `## Citywide` section covering: budget/policy headlines, housing pipeline highlights, ethics & money, journalism roundup, and upcoming meetings. Write this section district-neutral — no "your supervisor," no district-specific 311 data. A D5 report and a D9 report should have identical citywide sections. The citywide-only report still exists for readers who don't pick a district.
23. **Developer mode (USER.md flag).** If the reader's USER.md includes a developer mode section, append a `🔧 Dev Notes` section at the end with: meetings found but not actionable, items that hit a filter but were too thin to include, and any sources that errored or returned empty. Default users (no developer flag) never see this section.

---

## Examples

### Voice

**Good:** "400 Divisadero got its approval letter 15 months ago. No building permits filed since."

**Bad:** "One must wonder whether the approval process is truly functioning as intended when projects languish in bureaucratic limbo."

---

### Voice — More Examples

**Lobbying — be specific, not suspicious:**
> Company X is the supervisor's most active lobbyist — 8 contacts in 2 months, all on the same topic. The volume is notable, and the coordination suggests a strategy.

Not: "Classic lobbying: work the target from both sides." Don't assume adversarial intent — note the pattern, explain the business logic, let the reader judge.

---

**Housing — tell a story, not a zoning report:**
> Three cancellations: 39 Taylor (112 units), 819 Ellis (120), 841 Polk (22). The pipeline is losing more units to cancellation than it's adding through new filings.

Not: "Developers continue to seek approvals for large residential projects in the district."

---

**Board of Supervisors — patterns, not minutes:**
> 33 landmark designations in one Board meeting. At this pace, preservation is outpacing new construction.

Not: "The Board of Supervisors passed several landmark designation resolutions at its March 24 meeting, including properties in multiple districts."

The first one has a point of view. The second one is a press release.

---

## 311 & Neighborhood Data

Rates of change over raw counts. "41 graffiti reports per day" is more useful than "2,843 reports." Even better: "graffiti up 15% from last quarter." Raw counts need context — is this normal? Getting worse? Concentrated where?

Always locate the data geographically. "Jones Street corridor" means something. "District 5" doesn't.

---

## What to Cut

- Infrastructure excuses ("the RSS feed only covers 5 days") — put in a footnote or skip it
- Sections with no signal ("Ethics: no lobbying activity flagged this period") — just don't include them
- Minor permits (reroofing, windows, decks) — one line summary at most
- Planning Commission items outside the district unless they set citywide precedent
- Anything that reads like a government report

---

## The Test

Read each section and ask: would this person text a friend about this? If not, it's either not important enough to include or not written sharply enough to be interesting. Cut it or rewrite it.
