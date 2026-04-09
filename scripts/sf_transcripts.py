#!/usr/bin/env python3
"""
SF SmartTranscripts Parser — fetches and parses meeting transcripts from
sfgovernmentconnection.com (SmartTranscripts by Tom Evslin).

This is a DATA SOURCE script — it extracts structured data for the agent to analyze.
The agent handles summarization using its own context and style guidelines.

Source: https://sfgovernmentconnection.com
Coverage: Board of Supervisors, committees (Land Use, Budget, etc.), Planning Commission, SFUSD
Lag: ~1 week behind real-time

Usage:
    python sf_transcripts.py --url URL [--json]
    python sf_transcripts.py --body "Budget_and_Finance_Committee" --date 2026-03-25 [--json]
    python sf_transcripts.py --list-recent [--days 14]

Output: JSON with meeting metadata, agenda items (with pre-made summaries), and full transcript.
"""

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import datetime, timedelta


BASE_URL = "https://sfgovernmentconnection.com/meetings"

# Known body URL slugs
BODIES = {
    "board": "Board_of_Supervisors",
    "bos": "Board_of_Supervisors",
    "land_use": "Board_of_Supervisors/Land_Use_and_Transportation_Committee",
    "budget": "Board_of_Supervisors/Budget_and_Finance_Committee",
    "rules": "Board_of_Supervisors/Rules_Committee",
    "gov_audit": "Board_of_Supervisors/Government_Audit_and_Oversight_Committee",
    "public_safety": "Board_of_Supervisors/Public_Safety_and_Neighborhood_Services_Committee",
    "planning": "Planning_Commission",
    "sfusd": "Education_SFUSD_Board_of",
}


# ---------------------------------------------------------------------------
# HTML Parser for SmartTranscripts
# ---------------------------------------------------------------------------

class SmartTranscriptParser(HTMLParser):
    """
    Extracts structured data from sfgovernmentconnection.com transcript pages:
      - meeting metadata (from <script id="meeting-data">)
      - agenda items with summaries (from <nav id="agenda">)
      - speaker-tagged transcript (from <div id="text-container">)
    """

    def __init__(self):
        super().__init__()
        self._in_agenda = False
        self._in_agenda_li = False
        self._in_agenda_link = False
        self._in_agenda_summary = False
        self._in_text_container = False
        self._in_speaker_tag = False
        self._in_utterance = False
        self._in_meeting_data = False
        self._in_meeting_title = False
        self._depth_text_container = 0

        self.meeting_title = ""
        self.meeting_data = {}
        self.agenda_items = []
        self.transcript = []

        self._current_agenda_item = {}
        self._current_speaker = ""
        self._current_utterances = []
        self._current_utterance_text = ""
        self._current_start_time = None
        self._buf = ""

    def _flush_utterance(self):
        if self._current_utterance_text.strip():
            self._current_utterances.append({
                "text": self._current_utterance_text.strip(),
                "start_time": self._current_start_time,
            })
        self._current_utterance_text = ""
        self._current_start_time = None

    def _flush_speaker_block(self):
        self._flush_utterance()
        if self._current_speaker and self._current_utterances:
            self.transcript.append({
                "speaker": self._current_speaker,
                "utterances": self._current_utterances,
            })
        self._current_speaker = ""
        self._current_utterances = []

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)

        if tag == "h2" and attrs_d.get("id") == "meeting-title":
            self._in_meeting_title = True
            self._buf = ""

        if tag == "nav" and attrs_d.get("id") == "agenda":
            self._in_agenda = True

        if self._in_agenda:
            if tag == "li":
                self._in_agenda_li = True
                self._current_agenda_item = {"title": "", "href": "", "summary": ""}
            elif tag == "a" and self._in_agenda_li:
                self._in_agenda_link = True
                self._current_agenda_item["href"] = attrs_d.get("href", "")
                self._buf = ""
            elif tag == "div" and "agenda-summary" in attrs_d.get("class", ""):
                self._in_agenda_summary = True
                self._buf = ""

        if tag == "div" and attrs_d.get("id") == "text-container":
            self._in_text_container = True
            self._depth_text_container = 1

        if self._in_text_container:
            if tag == "div" and not (attrs_d.get("id") == "text-container"):
                self._depth_text_container += 1
            if tag == "p":
                self._flush_speaker_block()
            if tag == "strong":
                self._in_speaker_tag = True
                self._buf = ""
            if tag == "span" and "utterance" in attrs_d.get("class", ""):
                self._flush_utterance()
                self._in_utterance = True
                self._current_start_time = attrs_d.get("data-start-time")

        if tag == "script" and attrs_d.get("id") == "meeting-data":
            self._in_meeting_data = True
            self._buf = ""

    def handle_endtag(self, tag):
        if tag == "h2" and self._in_meeting_title:
            self._in_meeting_title = False
            self.meeting_title = self._buf.strip()

        if self._in_agenda:
            if tag == "nav":
                self._in_agenda = False
            elif tag == "a" and self._in_agenda_link:
                self._in_agenda_link = False
                self._current_agenda_item["title"] = self._buf.strip()
            elif tag == "div" and self._in_agenda_summary:
                self._in_agenda_summary = False
                self._current_agenda_item["summary"] = self._buf.strip()
            elif tag == "li" and self._in_agenda_li:
                self._in_agenda_li = False
                if self._current_agenda_item.get("title"):
                    self.agenda_items.append(self._current_agenda_item)

        if self._in_text_container:
            if tag == "div":
                self._depth_text_container -= 1
                if self._depth_text_container <= 0:
                    self._flush_speaker_block()
                    self._in_text_container = False
            if tag == "strong" and self._in_speaker_tag:
                self._in_speaker_tag = False
                raw = self._buf.strip()
                match = re.match(r"\[(.+)\]:?", raw)
                self._current_speaker = match.group(1) if match else raw.rstrip(":")
            if tag == "span" and self._in_utterance:
                self._in_utterance = False

        if tag == "script" and self._in_meeting_data:
            self._in_meeting_data = False
            try:
                self.meeting_data = json.loads(self._buf)
            except json.JSONDecodeError:
                pass

    def handle_data(self, data):
        if self._in_meeting_title:
            self._buf += data
        if self._in_agenda_link or self._in_agenda_summary:
            self._buf += data
        if self._in_speaker_tag:
            self._buf += data
        if self._in_utterance:
            self._current_utterance_text += data
        if self._in_meeting_data:
            self._buf += data


# ---------------------------------------------------------------------------
# Fetch + Parse
# ---------------------------------------------------------------------------

def build_url(body: str, date: str) -> str:
    """Build SmartTranscripts URL from body slug and date."""
    body_slug = BODIES.get(body.lower(), body)
    # Try with _00-00 suffix first (newer format)
    return f"{BASE_URL}/{body_slug}/{date}_00-00/transcript.html"


def fetch_transcript(url: str) -> str:
    """Fetch raw HTML from a SmartTranscripts URL."""
    req = Request(url, headers={"User-Agent": "CivicClaw/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except HTTPError as e:
        if e.code == 404:
            # Try without _HH-MM suffix (older format)
            alt = re.sub(r"_\d{2}-\d{2}/transcript", "/transcript", url)
            if alt != url:
                req2 = Request(alt, headers={"User-Agent": "CivicClaw/1.0"})
                try:
                    with urlopen(req2, timeout=30) as resp:
                        return resp.read().decode("utf-8")
                except HTTPError:
                    pass
        return None
    except URLError:
        return None


def parse_transcript(html: str) -> dict:
    """Parse SmartTranscripts HTML into structured data."""
    parser = SmartTranscriptParser()
    parser.feed(html)

    # Flatten transcript for easier consumption
    transcript_flat = []
    for block in parser.transcript:
        speaker = block["speaker"]
        text = " ".join(u["text"] for u in block["utterances"])
        transcript_flat.append({"speaker": speaker, "text": text})

    return {
        "title": parser.meeting_title or parser.meeting_data.get("title", ""),
        "video_url": parser.meeting_data.get("video_url", ""),
        "speakers": parser.meeting_data.get("speakers", []),
        "agenda_items": parser.agenda_items,
        "transcript": transcript_flat,
        "source": "SmartTranscripts (sfgovernmentconnection.com)",
    }


def check_availability(body: str, date: str) -> bool:
    """Check if a transcript is available for a given body and date."""
    url = build_url(body, date)
    req = Request(url, method="HEAD", headers={"User-Agent": "CivicClaw/1.0"})
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except:
        # Try alternate URL format
        alt = re.sub(r"_\d{2}-\d{2}/transcript", "/transcript", url)
        if alt != url:
            req2 = Request(alt, method="HEAD", headers={"User-Agent": "CivicClaw/1.0"})
            try:
                with urlopen(req2, timeout=10) as resp:
                    return resp.status == 200
            except:
                pass
        return False


def list_recent(days: int = 14) -> list:
    """Scan for available transcripts in the last N days."""
    results = []
    today = datetime.now()
    
    for body_key, body_slug in BODIES.items():
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if check_availability(body_slug, date):
                results.append({
                    "body": body_key,
                    "body_slug": body_slug,
                    "date": date,
                    "url": build_url(body_slug, date),
                })
    
    return sorted(results, key=lambda x: x["date"], reverse=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fetch and parse SF meeting transcripts from SmartTranscripts"
    )
    
    parser.add_argument("--url", help="Direct SmartTranscripts URL")
    parser.add_argument("--body", help="Body slug (e.g., 'budget', 'land_use', 'board')")
    parser.add_argument("--date", help="Meeting date (YYYY-MM-DD)")
    parser.add_argument("--list-recent", action="store_true", help="List available transcripts")
    parser.add_argument("--days", type=int, default=14, help="Days to scan for --list-recent")
    parser.add_argument("--json", action="store_true", help="Output JSON (default)")
    
    args = parser.parse_args()
    
    if args.list_recent:
        print("Scanning for recent transcripts...", file=sys.stderr)
        results = list_recent(args.days)
        print(json.dumps(results, indent=2))
        return
    
    if args.url:
        url = args.url
    elif args.body and args.date:
        url = build_url(args.body, args.date)
    else:
        parser.error("Provide --url, or both --body and --date, or --list-recent")
    
    print(f"Fetching: {url}", file=sys.stderr)
    html = fetch_transcript(url)
    
    if not html:
        print(json.dumps({"error": "Transcript not found", "url": url}))
        sys.exit(1)
    
    parsed = parse_transcript(html)
    parsed["url"] = url
    
    print(f"Parsed: {parsed['title']} | {len(parsed['agenda_items'])} items | {len(parsed['transcript'])} blocks", file=sys.stderr)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
