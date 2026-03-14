# 🧠 Business Idea Novelty Analyzer
### Semantic Similarity Based Business Idea Novelty Analysis
**MCA Final Year Project**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-2.0-green)
![BERT](https://img.shields.io/badge/Model-Sentence--BERT-orange)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama3-purple)

---

## 📌 About
A web application that analyzes how **novel or original** a business idea is by:
- Searching the web in real time for similar startups
- Comparing using **Sentence-BERT + Cosine Similarity**
- Generating an **Innovation Radar Chart**
- Providing **AI-powered strategic recommendations** via Groq Llama 3

---

## 🚀 Features
- 🔍 Real-time DuckDuckGo startup search
- 🤖 Sentence-BERT semantic similarity engine
- 📊 Innovation Radar Chart (5 dimensions)
- 💡 AI suggestions powered by Groq Llama 3.1
- 🏷️ Auto category detection (Fintech, Edtech, etc.)
- 🎨 Premium dark glassmorphism UI

---

## 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| AI Model | Sentence-BERT (all-MiniLM-L6-v2) |
| Similarity | Cosine Similarity (scikit-learn) |
| Search | DuckDuckGo real-time web search |
| AI Suggestions | Groq API (Llama 3.1) |
| Frontend | HTML, CSS, JavaScript, Chart.js |

---

## 📂 Project Structure
```
novelty_analysis/
├── app.py                  # Flask backend
├── similarity.py           # BERT + cosine similarity engine
├── ai_suggestions.py       # Groq AI recommendations
├── templates/
│   └── index.html          # Frontend UI
├── static/
│   ├── style.css           # Dark glassmorphism styling
│   └── script.js           # Radar chart + results display
├── data/
│   └── startups.csv        # Reference data
└── requirements.txt        # Python dependencies
```

---

## ⚙️ Installation

**1. Clone the repository**
```bash
git clone https://github.com/Ajay323687/business-idea-novelty.git
cd business-idea-novelty
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install flask sentence-transformers scikit-learn requests beautifulsoup4 python-dotenv numpy
```

**4. Create .env file**
```bash
echo GROQ_API_KEY=your_groq_api_key_here > .env
```

**5. Run the app**
```bash
python app.py
```

**6. Open browser**
```
http://127.0.0.1:5000
```

---

## 📊 How It Works
```
User Input → DuckDuckGo Search → Filter Real Startups
→ Sentence-BERT Encoding → Cosine Similarity
→ Novelty Score = (1 - avg_similarity) × 100
→ Innovation Radar Chart → Groq AI Suggestions
```

---

## 🎯 Base Papers
1. **Deep Text Understanding Model for Similar Case Matching** — IEEE Access 2024
2. **Contrastive Meta-Learner for Automatic Text Labeling and Semantic Textual Similarity** — IEEE Access 2024

---

## 👨‍💻 Author
**Ajay Maddigunta** — MCA Final Year Student

---
⭐ Star this repo if you found it useful!