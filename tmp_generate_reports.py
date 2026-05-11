import json
import subprocess
from pathlib import Path

root = Path('/home/ubuntu/repos/civicclaw')
style = (root / 'STYLE.md').read_text()
user = (root / 'users/sgillen/USER.md').read_text()
refs = (root / 'references/sf-build-timelines.md').read_text()
summary = json.loads((root / 'docs/data/site-refresh-summary.json').read_text())

for d in summary['completed']:
    bundle = root / f'build/bundles/d{d}.json'
    out = root / f'docs/data/d{d}.md'
    data = json.loads(bundle.read_text())
    parts = [
        f"Write a polished CivicClaw district report markdown for District {d}.",
        "You must output ONLY the final markdown report.",
        "",
        "Inputs:",
        "- STYLE.md rules:",
        style,
        "",
    ]
    if d == 5:
        parts += ["- USER.md for this reader:", user, ""]
    else:
        parts += ["- No district-specific USER.md is available. Use neutral defaults, but still follow STYLE.md exactly.", ""]
    parts += [
        "- Housing timeline reference:",
        refs,
        "",
        "- District bundle JSON:",
        json.dumps(data, ensure_ascii=False),
        "",
        "Requirements:",
        "- Follow STYLE.md exactly.",
        "- Start with a title line for the district and date range if available from the bundle.",
        "- Then TLDR with 5-7 bullets, summary only, no action items.",
        "- Then ## Potential Actions with exactly one featured action first, then all remaining actions including cleanups.",
        "- Then ## Your Officials with district supervisor, mayor, and state reps only.",
        "- Then concise narrative sections with no repetition from TLDR.",
        "- Include ## Citywide at the end.",
        "- Include 🔧 Dev Notes only for District 5.",
        "- If housing projects are discussed, use the timelines reference to calibrate whether something is normal, fast, or stalled.",
        "- Keep the report scannable in ~2 minutes.",
        "- Do not mention missing infrastructure or scraper limitations in the main narrative.",
    ]
    prompt = "\n".join(parts)
    prompt_file = root / f'tmp_prompt_d{d}.txt'
    prompt_file.write_text(prompt)
    with open(prompt_file, 'rb') as fin, open(out, 'wb') as fout:
        proc = subprocess.run(['codex', 'exec', '--full-auto', '-'], cwd=root, stdin=fin, stdout=fout)
    prompt_file.unlink(missing_ok=True)
    if proc.returncode != 0:
        raise SystemExit(f'District {d} failed with rc={proc.returncode}')
    print(f'District {d} written to {out}')
