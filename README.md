# 🏠 Schweizer Immobilienpreise – Scientific Programming Projekt FS2026

Analyse von Schweizer Immobilienpreisen auf Basis öffentlich verfügbarer Daten.

## 📋 Projektübersicht

**Forschungsfrage:** Welche Faktoren (Kanton, Fläche, Zimmeranzahl, PLZ) beeinflussen den Mietpreis in der Schweiz, und gibt es statistisch signifikante Preisunterschiede zwischen Regionen?

**Modul:** Scientific Programming – ZHAW FS2026

## 🗂️ Projektstruktur

```
sp-immobilien-schweiz/
├── notebooks/
│   ├── 01_data_collection.ipynb      # Web Scraping & API
│   ├── 02_data_preparation.ipynb     # Cleaning, Regex, OOP
│   ├── 03_statistical_analysis.ipynb # Korrelation, t-Test, p-Werte
│   └── 04_visualization.ipynb        # Plots, Karten, Dashboard
├── src/
│   ├── scraper.py                    # Web Scraper Klasse
│   ├── database.py                   # SQLite Datenbanklogik
│   └── models.py                     # OOP Datenmodelle
├── app/
│   └── streamlit_app.py              # Interaktive Web App
├── data/                             # ⚠️ in .gitignore (grosse Dateien)
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Setup & Installation

```bash
# 1. Repository klonen
git clone https://github.com/DEIN-USERNAME/sp-immobilien-schweiz.git
cd sp-immobilien-schweiz

# 2. Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Jupyter starten
jupyter notebook
```

## 📊 Module-Anforderungen (Checkliste)

### Pflichtanforderungen
- [x] Reale Daten gesammelt (Web Scraping / öffentliche Daten)
- [x] Datenaufbereitung mit Regex (Preise, Flächen, PLZ)
- [x] Python Datenstrukturen: Listen, Dicts, Sets, Tuples, DataFrames
- [x] Kontrollstrukturen und Loops
- [x] OOP (Klassen: `Inserat`, `ImmobilienScraper`, `Datenbank`)
- [x] Tabellen & Visualisierungen (matplotlib, seaborn, folium)
- [x] Statistische Analyse mit p-Wert (Korrelation, t-Test)
- [x] Code auf Moodle abgegeben

### Bonuspunkte
- [x] Web Scraper (BeautifulSoup + requests)
- [x] Datenbank (SQLite + SQL-Abfragen)
- [x] LLM-Unterstützung (Anthropic Claude API)
- [x] Web App (Streamlit)
- [x] GitHub Repo (dieses Repo 🎉)
- [x] Kreativität (Karte, Preisvorhersage, LLM-Parsing)

## 👥 Gruppe

| Name | Rolle |
|------|-------|
| Student A | Scraper, Datenbank |
| Student B | Analyse, Visualisierung, Web App |

## 📄 Lizenz
ZHAW – Scientific Programming FS2026

