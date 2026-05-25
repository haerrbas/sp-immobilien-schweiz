# Schweizer Immobilienpreise - SP-Projekt FS2026

> **Forschungsfrage:** Welche Faktoren (Kanton, Flaeche, Zimmeranzahl, PLZ) beeinflussen den Mietpreis in der Schweiz, und gibt es statistisch signifikante Preisunterschiede zwischen Regionen?

**Modul:** Scientific Programming - ZHAW School of Management and Law - FS2026

---

## Wichtigste Ergebnisse

| Kennzahl | Wert |
|---|---|
| Datensatz | 500 Inserate aus 10 Schweizer Staedten |
| Teuerste Stadt | Zuerich (Avg CHF 2517/Mt.) |
| Guenstigste Stadt | Biel (Avg CHF 1522/Mt.) |
| Korrelation Preis-Flaeche | r = 0.80 (p < 0.001 ***) |
| Regression R2 | 0.645 - jeder m2 kostet CHF 12.14 mehr |
| t-Test Zuerich vs. andere | Signifikant teurer als 8 von 9 Staedten (alpha = 0.05) |

---

## Projektstruktur

```
sp-immobilien-schweiz/
├── notebooks/
│   ├── 01_data_collection.ipynb      # Scraping, Regex, DB, Datenstrukturen
│   ├── 02_data_preparation.ipynb     # Bereinigung, Loops, LLM (Claude API)
│   ├── 03_statistical_analysis.ipynb # Pearson r, Welch t-Test, p-Werte
│   └── 04_visualization.ipynb        # Plots, Folium-Karte, Dashboard
├── src/
│   ├── __init__.py
│   ├── models.py      # Klasse Inserat (OOP + Regex-Parser)
│   ├── database.py    # SQLite + SQL-Queries
│   └── scraper.py     # Web Scraper + Beispieldaten-Generator
├── app/
│   └── streamlit_app.py   # Interaktive Web App (4 Tabs, Filter-Sidebar)
├── data/              # in .gitignore
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Quickstart

```bash
git clone https://github.com/haerrbas/sp-immobilien-schweiz.git
cd sp-immobilien-schweiz
pip install -r requirements.txt
jupyter notebook notebooks/01_data_collection.ipynb
streamlit run app/streamlit_app.py
```

---

## Modul-Anforderungen

### Pflichtanforderungen (8/8)

| # | Anforderung | Umsetzung |
|---|---|---|
| 1 | Reale Daten sammeln | Web Scraper (Flatfox.ch) + Fallback-Generator |
| 2 | Datenaufbereitung via Regex | _parse_preis(), _parse_flaeche(), _parse_ort() in models.py |
| 3 | Python Datenstrukturen | List, Dict, Set, Tuple in Notebook 01 |
| 4 | Kontrollstrukturen & Loops | Plausibilitaetsfilter, Batch-Verarbeitung in Notebook 02 |
| 5 | OOP | Klassen: Inserat, ImmobilienScraper, ImmobilienDB |
| 6 | Tabellen & Visualisierungen | matplotlib, seaborn: Boxplot, Violin, Scatter, Heatmap |
| 7 | Statistik mit p-Wert | Pearson r, Welch t-Test, Lineare Regression in Notebook 03 |
| 8 | Code auf Moodle | ZIP-Abgabe |

### Bonuspunkte (6/6)

| # | Bonus | Umsetzung |
|---|---|---|
| 1 | Web Scraper | ImmobilienScraper.scrape_flatfox() mit BeautifulSoup + requests |
| 2 | Datenbank + SQL | SQLite via ImmobilienDB - CREATE, INSERT OR IGNORE, GROUP BY, JOIN |
| 3 | LLM-Unterstuetzung | Claude API in Notebook 02 - klassifiziert Ausstattung aus Beschreibungen |
| 4 | Web App | Streamlit mit Filter-Sidebar, 4 Tabs, KPIs, interaktiven Charts |
| 5 | GitHub Repo | Dieses oeffentliche Repository |
| 6 | Kreativitaet | Folium-Karte CH, Preis/m2-Heatmap, Preis-Kategorie-Klassifikation |

---

## Statistische Ergebnisse

### Korrelationsanalyse (Pearson r)

| Variable 1 | Variable 2 | r | p-Wert | Sig. |
|---|---|---|---|---|
| preis_chf | flaeche_m2 | 0.803 | 4.22e-114 | *** |
| preis_chf | zimmer_anzahl | 0.766 | 1.19e-97 | *** |
| flaeche_m2 | zimmer_anzahl | 0.943 | 9.22e-241 | *** |
| preis_chf | preis_pro_m2 | -0.326 | 8.41e-14 | *** |

### Lineare Regression: Preis ~ Flaeche

```
Preis = 12.14 x Flaeche (m2) + 976.24
R2 = 0.645  (64.5% Varianzaufklaerung)
p-Wert = 4.22e-114  (hochsignifikant ***)
Jeder zusaetzliche m2 kostet im Schnitt CHF 12.14 mehr Miete
```

### t-Test: Zuerich vs. andere Staedte (Welch, alpha = 0.05)

Zuerich ist signifikant teurer als Basel, Bern, Biel, Lausanne, Lugano, Luzern, St. Gallen und Winterthur. Kein signifikanter Unterschied zu Genf (p = 0.163).

---

## Technologie-Stack

| Tool | Verwendung |
|---|---|
| Python 3.11 | Programmiersprache |
| pandas, numpy | Datenverarbeitung |
| matplotlib, seaborn | Visualisierungen |
| scipy.stats | Statistik (Pearson, t-Test, linregress) |
| BeautifulSoup, requests | Web Scraping |
| sqlite3 | Datenbank |
| streamlit | Web App |
| folium | Geographische Karte |
| Anthropic Claude API | LLM-Datenanalyse |

---

## Gruppe

| Name | GitHub |
|---|---|
| Basil Haerri | [@haerrbas](https://github.com/haerrbas) |
| Student 2 | (tbd) |

---

*ZHAW School of Management and Law - Scientific Programming FS2026 - Dr. Mario Gellrich*
