# ⚡ Creatrix — AI-Powered Creator Intelligence Platform

> Discover, evaluate, and activate the world's best YouTube creators for brand partnerships — powered by Groq LLM + YouTube Data API.

---

## 🚀 Quick Start

### 1. Clone / Download
```bash
cd creatrix
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add API Keys
Either:
- **Option A (Streamlit UI):** Enter your keys directly in the sidebar when the app launches — no `.env` needed.
- **Option B (.env file):** Copy `.env.example` to `.env` and fill in your keys.

```bash
cp .env.example .env
# Edit .env with your keys
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🔑 API Keys Required

| Key | Where to get it |
|-----|----------------|
| `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/) → Enable YouTube Data API v3 |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com/) |

---

## 📁 File Structure

```
creatrix/
├── app.py                    # Main Streamlit app
├── requirements.txt
├── .env.example
├── README.md
├── utils/
│   ├── youtube.py            # YouTube Data API v3 integration
│   ├── groq_analysis.py      # Groq LLM intelligence engine
│   ├── metrics.py            # Engagement & performance metrics
│   └── scoring.py            # Creator fit & brand safety scoring
└── components/
    ├── cards.py              # KPI, score, insight UI cards
    └── charts.py             # Plotly chart components
```

---

## ✨ Features

- **Channel Analysis** — Subscribers, views, engagement, upload cadence, Shorts ratio
- **Last 50 Video Deep-Dive** — Per-video performance, title patterns, viral signals
- **Creator Fit Engine** — 5-dimensional scoring (Fit, Audience, Safety, Readiness, Overall)
- **Groq AI Intelligence** — Match explanation, audience persona, content strategy
- **AI Insight Cards** — Growth strengths, weaknesses, viral patterns, monetization signals
- **Brand Safety Engine** — Low / Moderate / High risk classification
- **Sponsorship Intelligence** — Categories, CPM estimates, integration styles, CTA recommendations
- **Premium Dark UI** — Glassmorphism, Plotly charts, animated score gauges

---

## 🎨 Tech Stack

- **Frontend:** Streamlit + Custom CSS (glassmorphism dark theme)
- **Charts:** Plotly (animated, dark-themed)
- **AI:** Groq API — `llama-3.3-70b-versatile`
- **Data:** YouTube Data API v3
- **Backend:** Python (pandas, numpy, requests)

---

## 📝 Notes

- YouTube API has a **daily quota** of 10,000 units. Each full analysis uses ~200–400 units.
- Channel data and video data are **cached for 1 hour** to minimize API usage.
- Subscriber growth charts use simulated historical data (YouTube API does not expose historical subscriber counts).
- API keys entered in the Streamlit sidebar are **not stored** — they exist only in the session.

---

*Built with ⚡ by Creatrix*
