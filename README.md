# 💰 Grantini — Agentic Grant Research Bot

> **Free & open source.** Give it any project — a URL or description — and it finds, scores, and prioritises the best grant funding opportunities for you.

Powered by **Groq** (`llama-3.3-70b-versatile`) — completely free, no credit card needed.

---

## What it does

Grantini runs a **4-step agentic pipeline**:

| Step | What happens |
|------|-------------|
| 🔍 **Understand** | Analyses your project — mission, SDGs, stage, impact thesis, grant narratives |
| 🌍 **Search** | Finds 20+ real grant opportunities across health, Africa/emerging markets, Bitcoin, food systems, DFIs, accelerators |
| 📊 **Score** | Ranks every opportunity by fit × likelihood × effort — sorted into apply-now, next, and pipeline tiers |
| 📝 **Report** | Writes a full polished report: 30-day action plan, paste-ready templates, 12-month roadmap |

---

## Quickstart

### 1. Get a free API key
Go to **[console.groq.com](https://console.groq.com)** → create account → copy your API key. It's free, no credit card.

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. Set your key

**PowerShell (Windows):**
```powershell
$env:GROQ_API_KEY = "gsk_your_key_here"
```

**Bash (Mac / Linux):**
```bash
export GROQ_API_KEY="gsk_your_key_here"
```

### 4. Run it

**From a URL:**
```bash
python main.py --url https://yourproject.com
```

**From a description:**
```bash
python main.py --desc "We build affordable solar-powered cold storage for smallholder farmers in Kenya..."
```

**Interactive mode (no args):**
```bash
python main.py
```

---

## Output

Reports are saved to `reports/grantini_report_YYYYMMDD_HHMMSS.md` and printed to the console.

Copy the output into Notion, Google Docs, or email it to your team.

---

## Examples

```bash
# Analyse a health-tech startup
python main.py --url https://kraiiv.xyz

# Analyse a climate project by description  
python main.py --desc "CoolRoot builds bamboo-based biochar for carbon sequestration with smallholder farmers in Ghana. Pre-revenue, 3-person team, Accra-based."

# Combine URL + extra context
python main.py --url https://myproject.org --desc "We are in the seed stage and have raised $50k from angels."
```

---

## Model & Cost

| Setting | Value |
|---------|-------|
| Model | `llama-3.3-70b-versatile` |
| Provider | Groq (free tier) |
| Cost | **$0** — free tier covers hundreds of reports/day |
| Speed | ~10–30 seconds per full report |

---

## Contributing

Pull requests welcome. Ideas:
- [ ] Web UI (Streamlit / Flask)
- [ ] More grant categories (climate, education, arts)
- [ ] Export to PDF
- [ ] Email the report

---

*Built with ❤️ · Free & open source · [github.com/xi-kki/grantini](https://github.com/xi-kki/grantini)*
