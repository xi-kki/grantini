"""
Grantini — Agentic Grant Research Bot
======================================
Free & open. Powered by Groq (llama-3.3-70b-versatile).

Give it any project — a URL or a description — and it will:
  1. Understand the project (mission, SDGs, stage, narratives)
  2. Search for 20+ relevant grant opportunities
  3. Score & prioritise by fit, effort, and likelihood
  4. Write a full, actionable funding report

Usage:
    python main.py --url https://yourproject.com
    python main.py --desc "We build X for Y in Z..."
    python main.py  (interactive prompt)

Get a FREE Groq API key at: https://console.groq.com
"""

import os
import sys
import re
import argparse
import textwrap
import urllib.request
import urllib.error
from datetime import datetime
from html.parser import HTMLParser

from groq import Groq

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
MODEL   = "llama-3.3-70b-versatile"
BANNER  = r"""
   ____                  _   _       _ 
  / ___|_ __ __ _ _ __ | |_(_)_ __ (_)
 | |  _| '__/ _` | '_ \| __| | '_ \| |
 | |_| | | | (_| | | | | |_| | | | | |
  \____|_|  \__,_|_| |_|\__|_|_| |_|_|

  Agentic Grant Research Bot · Free via Groq
  ─────────────────────────────────────────
"""


# ─────────────────────────────────────────────
# Minimal HTML → plain-text extractor
# ─────────────────────────────────────────────
class _TextExtractor(HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "head", "svg", "iframe"}

    def __init__(self):
        super().__init__()
        self._skip  = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.SKIP_TAGS:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag.lower() in self.SKIP_TAGS and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.chunks.append(text)


def fetch_url(url: str, max_chars: int = 8000) -> str:
    """Fetch a URL and return its plain-text content (truncated)."""
    print(f"  🌐 Fetching {url} …")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Grantini-Bot/1.0 (grant research; +https://github.com/xi-kki/grantini)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.URLError as e:
        print(f"  ⚠️  Could not fetch URL: {e}. Continuing with URL as context only.")
        return f"Project website: {url}\n(Could not fetch page content — please add a --desc for more detail.)"

    parser = _TextExtractor()
    parser.feed(raw)
    text = "\n".join(parser.chunks)
    # Collapse whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text[:max_chars]


# ─────────────────────────────────────────────
# Groq client
# ─────────────────────────────────────────────
def get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\n❌  GROQ_API_KEY not set.")
        print("    Get a FREE key at: https://console.groq.com")
        print("    Then run:")
        print("      PowerShell : $env:GROQ_API_KEY='gsk_...'")
        print("      Bash/Mac   : export GROQ_API_KEY='gsk_...'")
        sys.exit(1)
    return Groq(api_key=api_key)


def chat(client: Groq, system: str, user: str, max_tokens: int = 4096) -> str:
    """Single-turn chat with the Groq model."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        max_tokens=max_tokens,
        temperature=0.4,
    )
    return resp.choices[0].message.content


# ─────────────────────────────────────────────
# Pipeline steps
# ─────────────────────────────────────────────

def step_understand(client: Groq, project_context: str) -> str:
    print("\n🔍  [1/4] Analysing project profile …")
    system = (
        "You are an expert grant analyst and startup advisor specialised in "
        "global development, health-tech, climate, fintech, and impact investing. "
        "You help founders understand how to position their projects for grant funding."
    )
    user = f"""
Analyse the project below and extract key attributes that grant makers care about.

PROJECT CONTEXT:
{project_context}

Extract and structure the following clearly:
1. **Elevator Pitch** — 2-sentence grant-ready mission statement
2. **Problem & Solution** — what pain, who has it, how this solves it
3. **SDG Alignment** — which UN SDGs apply and exactly how
4. **Target Beneficiaries** — who benefits directly, scale potential
5. **Geography & Market** — primary market and expansion plans
6. **Stage & Traction** — current stage, any metrics or milestones
7. **Technology & Innovation** — what makes this novel or defensible
8. **Impact Thesis** — the theory of change (if X, then Y, leading to Z)
9. **Grant Narratives** — 4 compelling story angles for funders
10. **Honest Gaps** — what's missing that applications must address

Be specific. Avoid vague language. This output feeds the grant search step.
"""
    return chat(client, system, user, max_tokens=2048)


def step_search(client: Groq, profile: str) -> str:
    print("\n🌍  [2/4] Searching for grant opportunities …")
    system = (
        "You are a senior grant researcher with encyclopaedic knowledge of "
        "global funding: UN agencies, bilateral aid, foundations, accelerators, "
        "DFIs, fellowship programs, and prize competitions. "
        "You know real programs, real deadlines, real amounts."
    )
    user = f"""
Based on the project profile below, identify REAL, SPECIFIC grant and funding 
opportunities. Use your knowledge of actual programs (not invented ones).

PROJECT PROFILE:
{profile}

Return at least 20 opportunities across these categories. 
For each provide: Name | Funder | Typical Amount | Deadline/Cycle | URL (if known) | 1-line fit reason.

## 🏥 Global Health, Nutrition & Wellbeing
## 🌍 African / Emerging Market Tech & Impact
## ⚡ Bitcoin, Web3 & Financial Inclusion
## 🥗 Food Systems, Agriculture & Nutrition
## 🏛️ Government, DFI & Bilateral Aid
## 🚀 Startup Accelerators & Fellowships (with funding)
## 🏆 Competitions & Prize Programs

Be specific. Name real programs. Include amounts and deadlines where known.
"""
    return chat(client, system, user, max_tokens=4096)


def step_score(client: Groq, profile: str, grants: str) -> str:
    print("\n📊  [3/4] Scoring and prioritising …")
    system = (
        "You are a strategic grant advisor who helps founders prioritise where "
        "to spend their limited application bandwidth for maximum return."
    )
    user = f"""
Score and rank the opportunities below for this specific project.

PROJECT PROFILE:
{profile}

OPPORTUNITIES:
{grants}

Score each on:
- Fit (1–10): alignment with funder priorities
- Effort (1–10, lower = easier): application complexity  
- Likelihood (1–10): realistic chance of success at current stage

Then output:

## 🎯 TOP 5 — Apply This Month
For each: name, scores, why it's top, exactly what to prepare, key message to lead with.

## ⚡ NEXT 5 — Apply in 3 Months
What milestones to hit first, then apply.

## 📅 PIPELINE — 6–12 Month Horizon
What traction this project needs before applying.

## 💡 Quick Wins (competitions, prizes, no-application-needed)

## ⚠️ Application Strategy Tips
Common mistakes founders make, how to frame the narrative for this project specifically.
"""
    return chat(client, system, user, max_tokens=4096)


def step_report(
    client: Groq,
    profile: str,
    grants: str,
    scored: str,
    raw_context: str,
    source_label: str,
) -> str:
    print("\n📝  [4/4] Writing final report …")
    system = (
        "You are an expert grant writer. You produce clear, professional, "
        "immediately actionable funding reports that founders can share with "
        "their team and use directly in applications."
    )
    user = f"""
Write a complete, polished grant research report using all the inputs below.

SOURCE: {source_label}
RAW PROJECT CONTEXT (first 1000 chars): {raw_context[:1000]}
PROFILE ANALYSIS: {profile[:1500]}
GRANT OPPORTUNITIES: {grants[:2000]}
SCORING & PRIORITIES: {scored[:2000]}

Structure the report exactly like this:

---
# 💰 Grantini Funding Report
**Project**: [extract project name from context]  
**Generated**: {datetime.now().strftime('%B %d, %Y')}  
**Powered by**: Grantini · free at github.com/xi-kki/grantini

---

## Executive Summary
[3–4 sentences: total opportunity size, top recommendation, key insight]

## Funding Narrative (use in applications)
[How to tell this project's story to grant makers — 2–3 paragraphs covering 
 mission, impact, innovation, and why now. Ready to paste into applications.]

## 🎯 Top 5 — Apply This Month
[For each: name, funder, amount, deadline, fit score, direct action to take]

## ⚡ Next 5 — Apply in 3 Months
[For each: name, funder, amount, what to build first]

## 📅 Full Opportunity Table
| # | Grant / Program | Funder | Amount | Fit | Likelihood | Deadline |
|---|----------------|--------|--------|-----|------------|----------|
[fill all 20+ opportunities]

## Application Templates

### Mission Statement (paste-ready)
[2–3 sentence project mission for grant applications]

### Impact Framing (paste-ready)
[Quantified impact narrative — beneficiaries, scale, outcomes]

### Innovation Pitch (paste-ready)  
[What makes this technically/socially novel]

## 30-Day Action Plan
[Numbered daily actions the founder can execute immediately]

## 12-Month Funding Roadmap
[Month-by-month: what to apply for, traction milestones, goals]

## Key Resources
[Grant databases, communities, tools to find more opportunities]

---
*Generated by Grantini · github.com/xi-kki/grantini · Free & open source*
"""
    return chat(client, system, user, max_tokens=8192)


# ─────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────

def run(source: str, source_label: str) -> None:
    print(BANNER)
    print(f"  Project source : {source_label}")
    print(f"  Model          : {MODEL} (via Groq — free tier)")
    print(f"  Started        : {datetime.now().strftime('%H:%M:%S')}")
    print()

    client = get_client()

    profile = step_understand(client, source)
    grants  = step_search(client, profile)
    scored  = step_score(client, profile, grants)
    report  = step_report(client, profile, grants, scored, source, source_label)

    # ── Save ──
    os.makedirs("reports", exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join("reports", f"grantini_report_{ts}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)

    # ── Print ──
    print("\n" + "═" * 64)
    print(report)
    print("═" * 64)
    print(f"\n✅  Report saved → {path}")
    print("    Share with your team or paste into Notion / Google Docs.\n")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Grantini — free agentic grant research bot powered by Groq",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python main.py --url https://yourproject.com
          python main.py --desc "We build solar cold storage for farmers in Kenya..."
          python main.py   (interactive — will prompt you)

        Get a FREE Groq API key: https://console.groq.com
        """),
    )
    parser.add_argument("--url",  type=str, help="Project website URL to analyse")
    parser.add_argument("--desc", type=str, help="Project description (plain text)")
    args = parser.parse_args()

    if args.url and args.desc:
        # Both provided — combine them
        page_text = fetch_url(args.url)
        source = f"URL: {args.url}\n\nWEBSITE CONTENT:\n{page_text}\n\nADDITIONAL DESCRIPTION:\n{args.desc}"
        label  = args.url
    elif args.url:
        page_text = fetch_url(args.url)
        source = f"URL: {args.url}\n\nWEBSITE CONTENT:\n{page_text}"
        label  = args.url
    elif args.desc:
        source = args.desc
        label  = "text description"
    else:
        # Interactive mode
        print(BANNER)
        print("  No arguments provided — entering interactive mode.\n")
        choice = input("  Enter (1) a URL  or  (2) a description? [1/2]: ").strip()
        if choice == "1":
            url = input("  Project URL: ").strip()
            page_text = fetch_url(url)
            source = f"URL: {url}\n\nWEBSITE CONTENT:\n{page_text}"
            label  = url
        else:
            print("  Describe your project (press Enter twice when done):")
            lines, blank = [], 0
            while blank < 1:
                line = input()
                if line == "":
                    blank += 1
                else:
                    blank = 0
                    lines.append(line)
            source = "\n".join(lines)
            label  = "text description"

    run(source, label)


if __name__ == "__main__":
    main()
