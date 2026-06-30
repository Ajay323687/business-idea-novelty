# Real-Time Business Idea Novelty Analyzer

### AI-Powered Strategic Market Validation & Competitor Analysis
**MCA Final Year Project**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Backend-Flask-green)
![Exa](https://img.shields.io/badge/Search-Exa.ai-purple)
![SBERT](https://img.shields.io/badge/Vectors-SBERT-red)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203.3-orange)

---

## 🚀 About the Project

The **Business Idea Novelty Analyzer** is an advanced, real-time intelligence framework designed to evaluate the originality of emerging startup concepts. Rather than relying on static databases or simple keyword matching, this system leverages a cutting-edge, three-pillar AI architecture:

1. **Live Neural Retrieval (Exa AI):** Fetches highly contextual, real-time competitor descriptions across both Indian and Global markets.
2. **Semantic Vector Mathematics (Sentence-BERT):** Encodes business ideas into 384-dimensional spatial vectors to calculate a deterministic Cosine Similarity and Novelty Score, preventing LLM hallucinations.
3. **Generative Strategic Synthesis (Groq Llama 3.3 70B):** Generates 5 specific, actionable strategic recommendations (Pivot, Differentiation, Monetization) based strictly on the mathematical baseline.

---

## ✨ Core Features

- **Dual-Mission Competitor Discovery:** Simultaneously searches local (India) and international markets, automatically deduplicating overlapping parent companies.
- **Mathematical Novelty Scoring:** Utilizes the `all-MiniLM-L6-v2` transformer model to compute pure semantic distance.
- **5-Dimension Innovation Radar:** Visually maps Originality, Market Gap, Competition, Innovation, and Viability using Chart.js.
- **Interactive D3.js Heatmaps:** Renders dynamic 2D India map projections and a rotating 3D Global Orthographic globe for competitor localization.
- **AI Strategy Generation:** Delivers structured market diagnostics and actionable pivot strategies.
- **Native PDF Report Builder:** Asynchronously generates and downloads highly formatted A4 intelligence briefs directly from the browser.

---

## 🛠️ Technology Stack

| Architecture Layer | Technology Used |
| :--- | :--- |
| **Backend Routing** | Python, Flask |
| **Neural Information Retrieval** | Exa.ai API (`type="neural"`) |
| **Semantic Encoding & Math** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **Large Language Model (LLM)**| Groq API (`llama-3.3-70b-versatile`) |
| **Frontend UI/UX** | HTML5, CSS3, Vanilla JS |
| **Data Visualization** | Chart.js (Radar), D3.js (Spatial Maps) |
| **Evaluation Framework** | Pandas, Concurrent Futures (Multithreading) |

---

## 📂 Clean Project Structure

```text
novelty_analysis/
+-- app.py                    # Main Flask backend (Exa + SBERT + Groq pipeline)
+-- evaluator.py              # Bulk 100-idea multithreaded accuracy testing script
+-- full_test_dataset.json    # The 100-idea evaluation dataset
+-- full_evaluation_report.csv# Exported test results and latency logs
+-- templates/
|   +-- index.html            # Main web dashboard interface
+-- static/
|   +-- style.css             # UI styling
|   +-- script.js             # Frontend logic, charts, maps, and PDF generation
+-- requirements.txt          # Minimal Python dependencies
+-- .env                      # Secure API keys (Not committed to version control)

⚙️ Installation & Setup
Clone the repository and navigate to the directory:

Bash
cd novelty_analysis
Create and activate a virtual environment:

Bash
python -m venv venv
venv\Scripts\activate   # For Windows
# source venv/bin/activate  # For macOS/Linux
Install the required dependencies:

Bash
pip install -r requirements.txt
Configure your Environment Variables:
Create a .env file in the root directory and add your API keys:

Code snippet
EXA_API_KEY=your_exa_api_key_here
GROQ_API_KEY=your_groq_api_key_here
Run the Application:

Bash
python app.py
Access the Dashboard:
Open your web browser and navigate to: http://127.0.0.1:5000

📊 Evaluation Framework (Stress Testing)
This project includes a built-in testing layer (evaluator.py) designed to empirically validate the system's accuracy and concurrency handling.

By running python evaluator.py, the system spins up parallel multithreaded workers to process a 100-idea dataset (full_test_dataset.json) spanning 10 distinct industry sectors (FinTech, AgriTech, SaaS, etc.). It calculates SBERT novelty scores in bulk and categorizes them into strict market tiers (Pioneer, Promising, Saturated), exporting the final intelligence to full_evaluation_report.csv.

👨‍💻 Author
Maddhigunta Ajay Kumar

MCA Final Year Student

Vignan's Lara Institute of Technology & Science, Vadlamudi, Guntur, India.