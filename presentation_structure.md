# Schweizer Immobilienpreise
## Scientific Programming - FS2026

**Basil Haerri / [Student 2]**
ZHAW School of Management and Law

---

## 1. Introduction

### Background
- Wohnungsmieten in der Schweiz gehoeren zu den hoechsten in Europa
- Starke regionale Unterschiede zwischen Staedten und Kantonen
- Datengetriebene Analyse kann Mietern und Investoren nuetzen

### Research Questions
1. Welche Merkmale (Flaeche, Zimmer, Lage) korrelieren am staerksten mit dem Mietpreis?
2. Gibt es statistisch signifikante Preisunterschiede zwischen Schweizer Staedten?
3. Wie gut laesst sich der Mietpreis durch eine lineare Regression erklaeren?

---

## 2. Materials and Methods

### Data Collection
- Quelle: Flatfox.ch (Web Scraper mit BeautifulSoup + requests)
- Fallback: Synthetischer Generator (500 Inserate, basierend auf BFS-Preisstatistiken 2023/24)
- Umfang: 500 Mietwohnungsinserate aus 10 Schweizer Staedten

### Data Preparation
- Regex-Parsing: Preis, Flaeche, Zimmer, PLZ aus Rohstrings extrahiert
- Plausibilitaetsfilter via Loop + Conditionals (Preis CHF 300-15000, Flaeche 15-400 m2)
- Feature Engineering: Preis/m2, Preiskategorie, Zimmergruppe
- LLM-Analyse: Claude API klassifiziert Ausstattungsmerkmale (Balkon, Parking, Renoviert)

### Statistical Methods
- Deskriptive Statistik: Mittelwert, Median, Standardabweichung pro Stadt
- Korrelationsanalyse: Pearson r mit zweiseitigem p-Wert (scipy.stats.pearsonr)
- t-Test: Welch's unabhaengiger t-Test (scipy.stats.ttest_ind, equal_var=False)
- Regression: Einfache lineare Regression (scipy.stats.linregress)

### Tools
Python 3.11, pandas, numpy, matplotlib, seaborn, scipy, sqlite3, BeautifulSoup, Streamlit, Anthropic Claude API

---

## 3. Results & Discussion

### Descriptive Statistics

| Stadt | n | Avg CHF | Median | Std |
|---|---|---|---|---|
| Zuerich | 50 | 2517 | 2475 | 494 |
| Genf | 50 | 2384 | 2375 | 452 |
| Lausanne | 50 | 2064 | 2050 | 460 |
| Basel | 50 | 1979 | 1900 | 443 |
| Bern | 50 | 1907 | 1800 | 424 |
| Luzern | 50 | 1758 | 1775 | 407 |
| Winterthur | 50 | 1635 | 1650 | 412 |
| Biel | 50 | 1522 | 1475 | 484 |

### Correlation Analysis (Pearson r)

| Variables | r | p-Value | Significance |
|---|---|---|---|
| Preis ~ Flaeche | 0.803 | 4.22e-114 | *** |
| Preis ~ Zimmer | 0.766 | 1.19e-97 | *** |
| Flaeche ~ Zimmer | 0.943 | 9.22e-241 | *** |
| Preis ~ Preis/m2 | -0.326 | 8.41e-14 | *** |

Interpretation: Flaeche und Zimmeranzahl sind die staerksten Praediktoren.

### Linear Regression: Preis ~ Flaeche

```
Preis = 12.14 x Flaeche (m2) + 976.24
R2 = 0.645  (64.5% Varianzaufklaerung)
p = 4.22e-114  (*** hochsignifikant)
-> Jeder m2 mehr kostet CHF 12.14 mehr Miete
```

### t-Test Results (alpha = 0.05, Welch's)
Zuerich ist signifikant teurer als 8 von 9 Staedten.
Ausnahme: Genf (p = 0.163, H0 beibehalten).

---

## 4. Conclusions

1. Flaeche ist der staerkste Preispraeadiktor (r=0.80, p<0.001)
2. Stadtlage ist signifikant - Zuerich und Genf deutlich teurer
3. Lineare Regression erklaert 64.5% der Preisvarianz
4. Pipeline laeuft vollautomatisch - Scraping bis Web App

---

## Appendix: Punkte-Nachweis

### Pflichtanforderungen

**1. Reale Daten:** src/scraper.py - HTTP GET auf Flatfox.ch mit BeautifulSoup

**2. Regex-Parsing:**
```python
def _parse_preis(self, raw: str) -> Optional[float]:
    cleaned = re.sub(r"['\s]", "", raw)
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    return float(match.group(1)) if match else None
```

**3. Datenstrukturen:** Notebook 01 - list(), set(), dict(sorted()), tuple() explizit gezeigt

**4. Kontrollstrukturen:** Notebook 02 - for + if/elif/else Plausibilitaetsfilter

**5. OOP:** dataclass Inserat, class ImmobilienScraper, class ImmobilienDB

**6. Visualisierungen:** Notebook 04 - 4-Panel Dashboard, Heatmap, Regression, Folium-Karte

**7. Statistik mit p-Wert:** scipy.stats.pearsonr, ttest_ind, linregress - alle mit p-Werten

**8. Moodle:** ZIP-Abgabe

### Bonuspunkte

**B1 Web Scraper:** ImmobilienScraper.scrape_flatfox() mit BeautifulSoup + requests

**B2 Datenbank + SQL:** SQLite ImmobilienDB - CREATE TABLE, INSERT OR IGNORE, SELECT GROUP BY, LEFT JOIN

**B3 LLM:** Claude API in Notebook 02 - JSON-strukturierte Ausstattungsklassifikation

**B4 Web App:** Streamlit - Filter-Sidebar, 4 Tabs, KPIs, Charts, Korrelation, t-Test

**B5 GitHub:** https://github.com/haerrbas/sp-immobilien-schweiz (public, .gitignore fuer data/)

**B6 Kreativitaet:** Folium-Karte CH, Preis/m2-Feature, Preiskategorie-Funktion, LLM-Features
