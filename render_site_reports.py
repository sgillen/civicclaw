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

KEYWORDS = {
    'housing': ['housing', 'residential', 'units', 'homeless', 'shelter', 'supportive'],
    'transit': ['transit', 'traffic', 'street', 'muni', 'scooter', 'bike', 'transportation', 'road'],
    'surveillance': ['surveillance', 'camera', 'alpr', 'drone', 'location tracking', 'social media monitoring'],
    'landmark': ['landmark', 'historic preservation', 'historic'],
    'downtown': ['downtown', 'hospitality', 'entertainment zone'],
}


def classify(text: str):
    t = text.lower()
    for label, words in KEYWORDS.items():
        if any(w in t for w in words):
            return label
    return 'other'


def fmt_date(date_str):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%B %-d, %Y')
    except Exception:
        return date_str


def report_title(data):
    d = datetime.strptime(data['date'], '%Y-%m-%d')
    start = d - timedelta(days=data.get('days', 7) - 1)
    return f"# SF Civic Digest — Week of {d.strftime('%B %-d, %Y')}\n*District {data['district']} · {NEIGHBORHOOD_DEFAULTS.get(data['district'], '')}*"


def summarize_housing(items, district):
    if not items:
        return None, None
    new = [i for i in items if i.get('new')]
    changed = [i for i in items if i.get('status_changed')]
    approvals = [i for i in items if 'approval' in (i.get('status','').lower())]
    on_hold = [i for i in items if 'hold' in (i.get('status','').lower())]
    under_review = [i for i in items if 'under review' in (i.get('status','').lower())]
    units_new = sum(i.get('units_net') or 0 for i in new)
    top = sorted(items, key=lambda i: (i.get('units_net') or 0), reverse=True)[:3]
    tldr = f"{len(new)} housing pipeline entries moved this cycle, covering about {units_new} net units; biggest items were " + ", ".join(f"{i['project_name']} ({i.get('units_net',0)} units)" for i in top) + "."
    lines = []
    if approvals:
        lines.append(f"{len(approvals)} projects are now at approval-letter stage, including " + ", ".join(f"{i['project_name']} ({i.get('units_net',0)} units)" for i in approvals[:3]) + ".")
    if on_hold:
        lines.append("The main caution flag is " + ", ".join(f"{i['project_name']} ({i.get('units_net',0)} units)" for i in on_hold[:2]) + " on hold.")
    if under_review:
        lines.append(f"{len(under_review)} more projects remain under review, so the pipeline is still moving through approvals rather than into permits or construction.")
    if district == 5:
        if any('400 DIVISADERO' in i.get('project_name','') for i in items):
            lines.append("400 Divisadero is in the post-approval dead zone: still within the normal 12-18 month window for market-rate projects, but it remains one to watch for a permit filing rather than another hearing.")
    return tldr, " ".join(lines)


def summarize_planning(items):
    if not items:
        return None, None
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
    upcoming = data.get('legistar', {}).get('upcoming', [])
    if not upcoming:
        return None, None
    relevant = []
    for m in upcoming:
        for item in m.get('items', []):
            if item.get('in_district') or item.get('item_district') in (None, data['district']):
                relevant.append((m, item))
    if not relevant:
        relevant = [(upcoming[0], upcoming[0]['items'][0])] if upcoming and upcoming[0].get('items') else []
    if not relevant:
        return None, None
    m, item = relevant[0]
    tldr = f"The next Board cycle is front-loaded with {m['body']} on {m['date']}, including {item['name'][:110]}."
    cats = Counter(classify(item['title']) for _, item in relevant[:8])
    body = "This week’s legislative mix is " + ", ".join(f"{v} {k}" for k, v in cats.items() if k != 'other')
    if not body.endswith('.'):
        body += "."
    return tldr, body


def select_actions(data):
    actions = []
    for m in data.get('legistar', {}).get('upcoming', []):
        items = m.get('items', [])
        if not items:
            continue
        chosen = None
        for item in items:
            if item.get('in_district'):
                chosen = item
                break
        if chosen is None:
            chosen = items[0]
        title = chosen['name']
        why = chosen['title'][:220].rstrip()
        actions.append({
            'kind': 'hearing',
            'title': f"{m['body']} — {m['date']} {m['time']}",
            'what': title,
            'why': why,
            'do': f"Public comment is open at the hearing. Agenda: {m['url']}",
            'score': 3 if chosen.get('in_district') else 2,
        })
    for p in data.get('planning_notices', [])[:4]:
        addr = p['address'].split('   ')[-1]
        actions.append({
            'kind': 'planning',
            'title': f"Planning notice — {addr}",
            'what': ", ".join(p.get('type_labels', [])) or p.get('hearing_body', 'Planning notice'),
            'why': f"This is still early enough to shape the project before a formal vote, especially if you care about design, use, or neighborhood impacts in {p.get('neighborhood','the area')}.",
            'do': f"Comment window runs through {p.get('expiration','the posted deadline')}. Contact: {p.get('contact_email','see notice')}",
            'score': 2,
        })
    for c in data.get('cleanups', [])[:6]:
        actions.append({
            'kind': 'cleanup',
            'title': f"Cleanup — {c['name']}",
            'what': f"{c['date_display']} {c['time']} at {c['location']}",
            'why': f"Cleanups are the easiest low-friction way to improve the block and meet neighbors in {c.get('neighborhood','the district')}.",
            'do': f"Sign up: {c.get('signup_url','https://refuserefusesf.org/cleanups')}",
            'score': 1,
        })
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
    leg = data.get('legistar', {}).get('upcoming', [])
    cleanups = data.get('cleanups', [])
    journalism = [j for j in data.get('journalism', []) if j.get('scope') == 'citywide']
    j_outlets = Counter(j.get('outlet_name','Unknown') for j in journalism)
    hp = data.get('housing_pipeline', [])
    approvals = [i for i in hp if 'approval' in (i.get('status','').lower())]
    on_hold = [i for i in hp if 'hold' in (i.get('status','').lower())]
    lines = []
    lines.append(f"Board and committee calendars are still dense: {len(leg)} upcoming legislative meetings are in the bundle, with housing, street operations, surveillance, and homelessness policy all active at once.")
    if approvals or on_hold:
        lines.append(f"Citywide housing is still a split screen: {len(approvals)} projects in this district bundle hit approval-letter stage while {len(on_hold)} are on hold, which is the same pattern citywide — approvals are easier to find than financing or construction starts.")
    if cleanups:
        lines.append(f"Volunteer cleanup infrastructure remains strong, with {len(cleanups)} nearby cleanups in the next two weeks. That is still the lowest-effort civic action in almost every district bundle.")
    if j_outlets:
        top = ', '.join(f"{k} ({v})" for k, v in j_outlets.most_common(4))
        lines.append(f"Local media volume stayed high this cycle, led by {top}. Use that as a cue that citywide politics, budget fights, and public-safety framing are setting the tone more than one-off neighborhood stories.")
    return "\n\n".join(lines)


def dev_notes(data):
    notes = []
    no_agenda_hpc = [h for h in data.get('hpc', []) if 'agenda not yet posted' in (h.get('status_note','') + h.get('summary','')).lower()]
    if no_agenda_hpc:
        notes.append(f"- HPC calendar entries were found ({len(no_agenda_hpc)} future dates) but not surfaced as actions because they have no posted agenda yet.")
    if data.get('311', {}).get('total_cases'):
        notes.append(f"- 311 data is present ({data['311']['total_cases']} reports in 7 days) but left out of the main narrative because STYLE.md says weekly 311 only belongs when there is a genuine anomaly.")
    if data.get('evictions', {}).get('total_notices') is not None:
        notes.append(f"- Evictions data is present ({data['evictions']['total_notices']} notices in 30 days) but omitted from the weekly narrative per STYLE.md monthly cadence guidance.")
    if not data.get('ethics', {}).get('lobbyist_contacts'):
        notes.append("- Ethics/lobbying returned no notable district-facing contacts this cycle.")
    return "\n".join(notes)

for d in SUMMARY['completed']:
    data = json.loads((BUNDLES / f'd{d}.json').read_text())
    housing_tldr, housing_body = summarize_housing(data.get('housing_pipeline', []), d)
    planning_tldr, planning_body = summarize_planning(data.get('planning_notices', []))
    leg_tldr, leg_body = summarize_legistar(data)
    actions = select_actions(data)
    bullets = []
    for candidate in [housing_tldr, planning_tldr, leg_tldr]:
        if candidate:
            bullets.append(candidate)
    if data.get('cleanups'):
        bullets.append(f"{len(data['cleanups'])} community cleanups are on the calendar over the next two weeks, spread across the district’s main neighborhoods.")
    sfmta = data.get('sfmta_board', [])
    if sfmta and sfmta[0].get('item_count'):
        bullets.append(f"SFMTA’s most recent board agenda touched {sfmta[0]['item_count']} items, including transit operations and street-management changes that will feed back into district curb and service decisions.")
    if data.get('journalism'):
        bullets.append(f"Local media stayed busy this week, so the district story is unfolding in the context of bigger citywide fights over budget, housing, downtown activation, and public safety.")
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
