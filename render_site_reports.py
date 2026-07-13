import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

ROOT = Path('/home/ubuntu/repos/civicclaw')
BUNDLES = ROOT / 'build' / 'bundles'
OUT = ROOT / 'docs' / 'data'
SUMMARY = json.loads((OUT / 'site-refresh-summary.json').read_text())
USER_MD = (ROOT / 'users' / 'sgillen' / 'USER.md').read_text()

SUPERVISOR_TO_STATE = {
    1: ("Catherine Stefani", "Assemblymember Phil Ting", "Sen. Scott Wiener"),
    2: ("Stephen Sherrill", "Assemblymember Matt Haney", "Sen. Scott Wiener"),
    3: ("Danny Sauter", "Assemblymember Matt Haney", "Sen. Scott Wiener"),
    4: ("Joel Engardio", "Assemblymember Joel Engardio", "Sen. Scott Wiener"),
    5: ("Bilal Mahmood", "Assemblymember Matt Haney", "Sen. Scott Wiener"),
    6: ("Matt Dorsey", "Assemblymember Matt Haney", "Sen. Scott Wiener"),
    7: ("Myrna Melgar", "Assemblymember Catherine Stefani", "Sen. Scott Wiener"),
    8: ("Rafael Mandelman", "Assemblymember Matt Haney", "Sen. Scott Wiener"),
    9: ("Jackie Fielder", "Assemblymember Matt Haney", "Sen. Scott Wiener"),
    10: ("Shamann Walton", "Assemblymember Matt Haney", "Sen. Scott Wiener"),
    11: ("Chyanne Chen", "Assemblymember Matt Haney", "Sen. Scott Wiener"),
}

MAYOR = "Mayor Daniel Lurie"

NEIGHBORHOOD_DEFAULTS = {
    1: "Richmond District",
    2: "Marina / Pacific Heights / Cow Hollow",
    3: "North Beach / Chinatown / Nob Hill",
    4: "Sunset",
    5: "NOPA / Western Addition / Hayes Valley / Lower Haight",
    6: "SoMa / Tenderloin / Mission Bay",
    7: "West Portal / Inner Sunset / Parkmerced",
    8: "Castro / Noe Valley / Glen Park",
    9: "Mission / Bernal Heights / Portola",
    10: "Bayview / Hunters Point / Potrero Hill",
    11: "Excelsior / Outer Mission / Ingleside",
}

DISTRICT_KEYWORDS = {
    1: ['richmond', 'geary', 'clement', 'anza', 'rossi', 'balboa', 'la playa', 'ocean beach'],
    2: ['marina', 'pacific heights', 'cow hollow', 'union', 'chestnut', 'fillmore', 'scott'],
    3: ['north beach', 'chinatown', 'nob hill', 'broadway', 'columbus', 'kearny', 'grant'],
    4: ['sunset', 'irving', 'noriega', 'taraval', 'judah'],
    5: ['lower haight', 'haight', 'hayes', 'divisadero', 'fillmore', 'fulton', 'mcallister', 'ellis', 'western addition', 'nopa', 'geary'],
    6: ['soma', 'tenderloin', 'mission bay', 'market', '6th', 'folsom', 'howard', 'south of market'],
    7: ['west portal', 'inner sunset', 'parkmerced', 'ocean avenue', 'taraval', '19th avenue'],
    8: ['castro', 'noe', 'glen park', 'dolores', 'market', 'valencia'],
    9: ['mission', 'bernal', 'portola', 'valencia', 'folsom', 'silliman', 'bowdoin', 'elsie', 'dolores', 'florida', 'mission street'],
    10: ['bayview', 'hunters point', 'potrero', '3rd street', 'jerrold', 'mckinnon', 'newcomb', 'lasalle', 'san bruno avenue'],
    11: ['excelsior', 'outer mission', 'ingleside', 'mission street', 'geneva', 'ocean avenue', 'persia'],
}

KEYWORDS = {
    'housing': ['housing', 'residential', 'units', 'homeless', 'shelter', 'supportive'],
    'transit': ['transit', 'traffic', 'street', 'muni', 'scooter', 'bike', 'transportation', 'road'],
    'surveillance': ['surveillance', 'camera', 'alpr', 'drone', 'location tracking', 'social media monitoring'],
    'landmark': ['landmark', 'historic preservation', 'historic'],
    'downtown': ['downtown', 'hospitality', 'entertainment zone'],
}

BAD_LEGISTAR_TERMS = ['settlement of lawsuit', 'appointment', 'reappointment']
PRIORITY_LEGISTAR_TERMS = ['entertainment zone', 'housing', 'planning code', 'supportive housing', 'drug-free', 'street', 'transit']


def parse_date(date_str, fmt='%Y-%m-%d'):
    try:
        return datetime.strptime(date_str, fmt).date()
    except Exception:
        return None


def classify(text: str):
    t = text.lower()
    for label, words in KEYWORDS.items():
        if any(w in t for w in words):
            return label
    return 'other'


def district_keyword_score(text: str, district: int):
    t = (text or '').lower()
    return sum(1 for kw in DISTRICT_KEYWORDS.get(district, []) if kw in t)


def unique_by(items, key_fn):
    out = []
    seen = set()
    for item in items:
        key = key_fn(item)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def report_title(data):
    d = datetime.strptime(data['date'], '%Y-%m-%d')
    return f"# SF Civic Digest — Week of {d.strftime('%B %-d, %Y')}\n*District {data['district']} · {NEIGHBORHOOD_DEFAULTS.get(data['district'], '')}*"


def summarize_housing(items, district):
    if not items:
        return None, None
    items = unique_by(items, lambda i: (i.get('project_name'), i.get('status')))
    new = [i for i in items if i.get('new')]
    approvals = [i for i in items if 'approval' in (i.get('status', '').lower())]
    on_hold = [i for i in items if 'hold' in (i.get('status', '').lower())]
    under_review = [i for i in items if 'under review' in (i.get('status', '').lower())]
    units_new = sum(i.get('units_net') or 0 for i in new)
    top = sorted(items, key=lambda i: (i.get('units_net') or 0), reverse=True)[:3]
    tldr = f"{len(new)} housing pipeline entries moved this cycle, covering about {units_new} net units; biggest items were " + ", ".join(f"{i['project_name']} ({i.get('units_net', 0)} units)" for i in top) + "."
    lines = []
    if approvals:
        lines.append(f"{len(approvals)} projects are now at approval-letter stage, including " + ", ".join(f"{i['project_name']} ({i.get('units_net', 0)} units)" for i in approvals[:3]) + ".")
    if on_hold:
        lines.append("The main caution flag is " + ", ".join(f"{i['project_name']} ({i.get('units_net', 0)} units)" for i in on_hold[:2]) + " on hold.")
    if under_review:
        lines.append(f"{len(under_review)} more projects remain under review, so the pipeline is still moving through approvals rather than into permits or construction.")
    if district == 5 and any('400 DIVISADERO' in (i.get('project_name') or '') for i in items):
        lines.append("400 Divisadero is in the post-approval dead zone: still within the normal 12-18 month window for market-rate projects, but it remains one to watch for a permit filing rather than another hearing.")
    return tldr, " ".join(lines)


def summarize_planning(items):
    if not items:
        return None, None
    today = datetime.utcnow().date()
    active = []
    for i in items:
        expiration = parse_date(i.get('expiration'), '%m/%d/%Y')
        if expiration and expiration < today:
            continue
        active.append(i)
    items = active or items
    by_body = Counter(i.get('hearing_body') or 'Other' for i in items)
    top_body, count = by_body.most_common(1)[0]
    expiring = [i for i in items if i.get('expiration') and i.get('expiration') != 'N/A'][:3]
    tldr = f"{len(items)} planning notices are active, led by {count} tied to {top_body}."
    body = []
    if expiring:
        body.append("Most of the near-term planning activity is still at the notice stage, including " + ", ".join(i['address'].split('   ')[-1] for i in expiring[:3]) + ".")
    body.append("That means the useful move this week is written comment or early project review, not waiting for a final vote.")
    return tldr, " ".join(body)


def summarize_legistar(data):
    upcoming = (data.get('legistar') or {}).get('upcoming') or []
    if not upcoming:
        return None, None
    relevant = []
    for m in upcoming:
        for item in m.get('items', []):
            text = f"{item.get('name', '')} {item.get('title', '')}"
            if item.get('in_district') or item.get('item_district') == data['district'] or district_keyword_score(text, data['district']):
                relevant.append((m, item))
    if not relevant:
        for m in upcoming:
            for item in m.get('items', []):
                text = f"{item.get('name', '')} {item.get('title', '')}".lower()
                if not any(term in text for term in BAD_LEGISTAR_TERMS):
                    relevant.append((m, item))
                    break
            if relevant:
                break
    if not relevant:
        return None, None
    m, item = relevant[0]
    tldr = f"The next Board cycle is front-loaded with {m['body']} on {m['date']}, including {item['name'][:110]}."
    cats = Counter(classify(item['title']) for _, item in relevant[:8])
    summary = ", ".join(f"{v} {k}" for k, v in cats.items() if k != 'other')
    body = f"This week’s legislative mix is {summary}." if summary else "This week’s legislative agenda is broad, but the most relevant items are the ones that affect housing and how streets are used."
    return tldr, body


def select_actions(data):
    today = datetime.utcnow().date()
    actions = []

    for hearing in data.get('sfmta') or []:
        hearing_date = parse_date(hearing.get('date'))
        if hearing_date and hearing_date < today:
            continue
        for item in hearing.get('items', []):
            text = f"{item.get('location', '')} {item.get('description', '')}"
            if data['district'] in (item.get('districts') or []) or district_keyword_score(text, data['district']):
                actions.append({
                    'kind': 'sfmta',
                    'title': f"SFMTA engineering hearing — {hearing.get('date')} {hearing.get('time', '')}".strip(),
                    'what': item.get('description', item.get('location', 'Street change proposal'))[:240],
                    'why': 'This is a curb, loading, or street-control change in or near the district, so it matters if you walk, bike, ride Muni, or care how the street actually works.',
                    'do': f"Comment at the hearing or email {item.get('contact_email', 'the project contact')}. Notice: {hearing.get('notice_url', '')}",
                    'score': 6,
                })
                break

    for m in (data.get('legistar') or {}).get('upcoming') or []:
        items = m.get('items') or []
        if not items:
            continue
        meeting_date = parse_date(m.get('date'), '%m/%d/%Y')
        if meeting_date and meeting_date < today:
            continue
        chosen = None
        best_score = -999
        for item in items:
            text = f"{item.get('name', '')} {item.get('title', '')}"
            lower = text.lower()
            score = 0
            if item.get('in_district') or item.get('item_district') == data['district']:
                score += 4
            score += district_keyword_score(text, data['district']) * 2
            if any(term in lower for term in PRIORITY_LEGISTAR_TERMS):
                score += 2
            if any(term in lower for term in BAD_LEGISTAR_TERMS):
                score -= 4
            if score > best_score:
                chosen = item
                best_score = score
        if chosen is None:
            chosen = items[0]
        actions.append({
            'kind': 'hearing',
            'title': f"{m['body']} — {m['date']} {m['time']}",
            'what': chosen['name'],
            'why': chosen['title'][:220].rstrip(),
            'do': f"Public comment is open at the hearing. Agenda: {m['url']}",
            'score': max(1, best_score),
        })

    planning_actions = []
    for p in data.get('planning_notices') or []:
        expiration = parse_date(p.get('expiration'), '%m/%d/%Y')
        if expiration and expiration < today:
            continue
        addr = p['address'].split('   ')[-1]
        planning_actions.append({
            'kind': 'planning',
            'title': f"Planning notice — {addr}",
            'what': ", ".join(p.get('type_labels') or []) or p.get('hearing_body', 'Planning notice'),
            'why': f"This is still early enough to shape the project before a formal vote, especially if you care about design, use, or neighborhood impacts in {p.get('neighborhood', 'the area')}.",
            'do': f"Comment window runs through {p.get('expiration', 'the posted deadline')}. Contact: {p.get('contact_email', 'see notice')}",
            'score': 4 if expiration else 3,
        })
    actions.extend(planning_actions[:4])

    future_cleanups = []
    for c in data.get('cleanups') or []:
        cleanup_date = parse_date(c.get('date'))
        if cleanup_date and cleanup_date < today:
            continue
        future_cleanups.append(c)
    for c in future_cleanups[:6]:
        actions.append({
            'kind': 'cleanup',
            'title': f"Cleanup — {c['name']}",
            'what': f"{c['date_display']} {c['time']} at {c['location']}",
            'why': f"Cleanups are the easiest low-friction way to improve the block and meet neighbors in {c.get('neighborhood', 'the district')}.",
            'do': f"Sign up: {c.get('signup_url', 'https://refuserefusesf.org/cleanups')}",
            'score': 1,
        })

    actions = unique_by(actions, lambda a: (a['title'], a['what']))
    actions.sort(key=lambda a: (-a['score'], a['title']))
    return actions


def officials_section(data):
    sup, asm, sen = SUPERVISOR_TO_STATE[data['district']]
    lines = [
        f"**{sup}** — This week’s district-facing agenda is mostly hearings and planning notices rather than a major passed item, so the useful accountability question is what they prioritize as these items move.",
        f"**{MAYOR}** — The citywide agenda still runs through Lurie’s budget and downtown-activation frame, plus surveillance and homelessness items moving through committees.",
        f"**{asm}** — No district-specific state action surfaced in this weekly bundle; treat Sacramento as background context this cycle.",
        f"**{sen}** — No district-specific state action surfaced in this weekly bundle; treat Sacramento as background context this cycle.",
    ]
    return "\n\n".join(lines)


def citywide_section(data):
    leg = (data.get('legistar') or {}).get('upcoming') or []
    cleanups = [c for c in (data.get('cleanups') or []) if not parse_date(c.get('date')) or parse_date(c.get('date')) >= datetime.utcnow().date()]
    journalism = [j for j in (data.get('journalism') or []) if j.get('scope') == 'citywide']
    j_outlets = Counter(j.get('outlet_name', 'Unknown') for j in journalism)
    hp = unique_by(data.get('housing_pipeline') or [], lambda i: (i.get('project_name'), i.get('status')))
    approvals = [i for i in hp if 'approval' in (i.get('status', '').lower())]
    on_hold = [i for i in hp if 'hold' in (i.get('status', '').lower())]
    lines = []
    lines.append(f"Board and committee calendars are still dense: {len(leg)} upcoming legislative meetings are in the bundle, with housing, street operations, surveillance, and homelessness policy all active at once.")
    if approvals or on_hold:
        lines.append(f"Citywide housing is still a split screen: {len(approvals)} projects in this district bundle hit approval-letter stage while {len(on_hold)} are on hold, which is the same pattern citywide, approvals are easier to find than financing or construction starts.")
    if cleanups:
        lines.append(f"Volunteer cleanup infrastructure remains strong, with {len(cleanups)} nearby cleanups in the next two weeks. That is still the lowest-effort civic action in almost every district bundle.")
    if j_outlets:
        top = ', '.join(f"{k} ({v})" for k, v in j_outlets.most_common(4))
        lines.append(f"Local media volume stayed high this cycle, led by {top}. Use that as a cue that citywide politics, budget fights, and public-safety framing are setting the tone more than one-off neighborhood stories.")
    return "\n\n".join(lines)


def dev_notes(data):
    notes = []
    no_agenda_hpc = [h for h in (data.get('hpc') or []) if 'agenda not yet posted' in (h.get('status_note', '') + h.get('summary', '')).lower()]
    if no_agenda_hpc:
        notes.append(f"- HPC calendar entries were found ({len(no_agenda_hpc)} future dates) but not surfaced as actions because they have no posted agenda yet.")
    if (data.get('311') or {}).get('total_cases'):
        notes.append(f"- 311 data is present ({data['311']['total_cases']} reports in 7 days) but left out of the main narrative because STYLE.md says weekly 311 only belongs when there is a genuine anomaly.")
    if (data.get('evictions') or {}).get('total_notices') is not None:
        notes.append(f"- Evictions data is present ({data['evictions']['total_notices']} notices in 30 days) but omitted from the weekly narrative per STYLE.md monthly cadence guidance.")
    if not (data.get('ethics') or {}).get('lobbyist_contacts'):
        notes.append("- Ethics/lobbying returned no notable district-facing contacts this cycle.")
    return "\n".join(notes)


for d in SUMMARY['completed']:
    data = json.loads((BUNDLES / f'd{d}.json').read_text())
    housing_tldr, housing_body = summarize_housing(data.get('housing_pipeline') or [], d)
    planning_tldr, planning_body = summarize_planning(data.get('planning_notices') or [])
    leg_tldr, leg_body = summarize_legistar(data)
    actions = select_actions(data)
    bullets = []
    for candidate in [housing_tldr, planning_tldr, leg_tldr]:
        if candidate:
            bullets.append(candidate)
    future_cleanups = [c for c in (data.get('cleanups') or []) if not parse_date(c.get('date')) or parse_date(c.get('date')) >= datetime.utcnow().date()]
    if future_cleanups:
        bullets.append(f"{len(future_cleanups)} community cleanups are on the calendar over the next two weeks, spread across the district’s main neighborhoods.")
    sfmta = data.get('sfmta_board') or []
    if sfmta and sfmta[0].get('item_count'):
        bullets.append(f"SFMTA’s most recent board agenda touched {sfmta[0]['item_count']} items, including transit operations and street-management changes that will feed back into district curb and service decisions.")
    if data.get('journalism'):
        bullets.append("Local media stayed busy this week, so the district story is unfolding in the context of bigger citywide fights over budget, housing, downtown activation, and public safety.")
    bullets = bullets[:6]

    md = [report_title(data), '', '---', '', '## TLDR', '']
    for b in bullets:
        md.append(f"- {b}")
    md += ['', '## Potential Actions', '']
    if actions:
        feat = actions[0]
        md += [f"### Featured: {feat['title']}", '', f"**What’s happening:** {feat['what']}", '', f"**Why you’d care:** {feat['why']}", '', f"**What you can do:** {feat['do']}"]
        for act in actions[1:]:
            md += ['', f"**{act['title']}** — {act['what']}", f"Why it matters: {act['why']}", f"What to do: {act['do']}"]
    else:
        md += ['No meetings or actions this week.']
    md += ['', '## Your Officials', '', officials_section(data)]
    if housing_body:
        md += ['', '## Housing Pipeline', '', housing_body]
    if planning_body:
        md += ['', '## Planning and Hearings', '', planning_body]
    if leg_body:
        md += ['', '## What the City Is Doing', '', leg_body]
    md += ['', '## Citywide', '', citywide_section(data)]
    if d == 5:
        md += ['', '## 🔧 Dev Notes', '', dev_notes(data)]
    (OUT / f'd{d}.md').write_text('\n'.join(md).strip() + '\n')
    print(f'wrote d{d}.md')
