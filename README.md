# Schweizer Immobilienpreise - SP-Projekt FS2026

> **Forschungsfrage:** Welche Faktoren (Kanton, Flaeche, Zimmeranzahl, PLZ) beeinflussen den Mietpreis in der Schweiz, und gibt es statistisch signifikante Preisunterschiede zwischen Regionen?

**Modul:** Scientific Programming - ZHAW School of Management and Law - FS2026
**Gruppe:** Basil Haerri [@haerrbas](https://github.com/haerrbas) / Sandro Oswald Schmuki [@schmusan](https://github.com/schmusan)

---

## Wichtigste Ergebnisse

| Kennzahl | Wert |
|---|---|
| Datensatz | 500 Inserate aus 10 Schweizer Staedten |
| Teuerste Stadt | Zuerich (Avg CHF 2517/Mt.) |
| Guenstigste Stadt | Biel (Avg CHF 1522/Mt.) |
| Korrelation Preis-Flaeche | r = 0.80 (p < 0.001 ***) |
| Regression R2 | 0.645 - jeder m2 kostet CHF 12.14 mehr |
| t-Test Zuerich vs. andere | Signifikant teurer als 8 von 9 Staedten |

---

## Projektstruktur

```
sp-immobilien-schweiz/
├── notebooks/
│   ├── 01_data_collection.ipynb      # Scraping, Regex, DB, Datenstrukturen
│   ├── 02_data_preparation.ipynb     # Bereinigung, Loops, LLM (Claude API)
│   ├── 03_statistical_analysis.ipynb # Pearson r, Welch t-Test, p-Werte, Regression
│   └── 04_visualization.ipynb        # Plots, Folium-Karte, 4-Panel Dashboard
├── src/
│   ├── __init__.py
│   ├── models.py      # Klasse Inserat (OOP + Regex-Parser)
│   ├── database.py    # SQLite + SQL (CREATE, INSERT, SELECT, JOIN, GROUP BY)
│   └── scraper.py     # Web Scraper + Beispieldaten-Generator
├── app/
│   └── streamlit_app.py   # Interaktive Web App (4 Tabs, Filter-Sidebar)
├── data/              # in .gitignore - keine grossen Dateien im Repo
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

## Modul-Anforderungen (detailliert)

### Pflichtanforderungen (8/8)

---

#### 1. Sammlung von realen Daten

Der `ImmobilienScraper` in `src/scraper.py` sendet HTTP-Requests an Flatfox.ch und parsed die HTML-Antwort mit BeautifulSoup. Falls der Server nicht erreichbar ist, greift ein Fallback-Generator auf realistische Preisstatistiken des BFS (Bundesamt fuer Statistik, 2023/24) zurueck.

```python
# src/scraper.py
def scrape_flatfox(self, stadt: str = "zuerich", max_seiten: int = 3) -> list:
    for seite in range(1, max_seiten + 1):
        url = f"{BASE_URL}?query={stadt}&object_category=apartment&type=rent&page={seite}"
        response = self.session.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        neue = self._parse_seite(soup, stadt)
        inserate.extend(neue)
        time.sleep(self.delay_sek)  # hoefliches Scraping
```

Ausgabe: Liste von `Inserat`-Objekten mit Preis, Flaeche, Zimmer, PLZ, URL.

---

#### 2. Datenaufbereitung mit Regular Expressions

Alle Rohstrings aus dem Scraper werden in numerische Werte umgewandelt. Vier spezialisierte Regex-Parser in `src/models.py`:

```python
# src/models.py - Klasse Inserat
def _parse_preis(self, raw: str) -> Optional[float]:
    # "CHF 2'450.- / Monat" -> 2450.0
    cleaned = re.sub(r"['\s]", "", raw)
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    return float(match.group(1)) if match else None

def _parse_flaeche(self, raw: str) -> Optional[float]:
    # "85 m2" -> 85.0  |  "67.5 m2" -> 67.5
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*m[2]?", raw, re.IGNORECASE)
    return float(match.group(1).replace(",", ".")) if match else None

def _parse_zimmer(self, raw: str) -> Optional[float]:
    # "3.5 Zimmer" -> 3.5  |  "4-Zi." -> 4.0
    match = re.search(r"(\d+(?:[.,]\d+)?)", raw)
    return float(match.group(1).replace(",", ".")) if match else None

def _parse_ort(self, raw: str) -> tuple:
    # "8001 Zuerich, ZH" -> ("8001", "Zuerich")
    match = re.match(r"(\d{4})\s+([^\,]+)", raw.strip())
    return (match.group(1), match.group(2).strip()) if match else (None, raw.strip())
```

Demonstriert in **Notebook 01**, Abschnitt 2 (Regex-Parsing Demo).

---

#### 3. Python Built-in Datenstrukturen

Explizite Demonstration aller vier Datenstrukturen in **Notebook 01**, Abschnitt 3:

```python
# LIST - geordnete Sammlung aller Stadtnamen
staedte_liste = list(df_roh['stadt'].dropna())
# -> ['Zuerich', 'Bern', 'Zuerich', 'Basel', ...]

# SET - einzigartige Staedte ohne Duplikate
einzigartige_staedte = set(staedte_liste)
# -> {'Zuerich', 'Bern', 'Basel', 'Genf', ...}

# DICT - Durchschnittspreis pro Stadt (sortiert absteigend)
preise_dict = {s: round(df[df['stadt']==s]['preis_chf'].mean(), 0)
               for s in einzigartige_staedte}
preise_dict = dict(sorted(preise_dict.items(), key=lambda x: x[1], reverse=True))
# -> {'Zuerich': 2517.0, 'Genf': 2384.0, ...}

# TUPLE - unveraenderliche Preisspanne (min, max)
preis_spanne = (df['preis_chf'].min(), df['preis_chf'].max())
# -> (700.0, 3700.0)
```

Zusaetzlich: `pandas DataFrame` als zentrales Datenformat in allen Notebooks.

---

#### 4. Kontrollstrukturen, Loop-Steuerung und Schleifen

**Notebook 02**, Abschnitt 2 - Plausibilitaetsfilter mit For-Loop + If/Elif/Else:

```python
ausgeschlossen, behalten = [], []

for idx, zeile in df.iterrows():          # FOR-Loop ueber alle Zeilen
    grund = None

    if not (300 <= zeile['preis_chf'] <= 15000):       # IF
        grund = f"Preis ausserhalb: CHF {zeile['preis_chf']:.0f}"
    elif not (15 <= zeile['flaeche_m2'] <= 400):       # ELIF
        grund = f"Flaeche ausserhalb: {zeile['flaeche_m2']:.0f} m2"
    elif not (0.5 <= zeile['zimmer_anzahl'] <= 12):    # ELIF
        grund = f"Zimmer ausserhalb: {zeile['zimmer_anzahl']}"

    if grund:                              # Bedingte Zuweisung
        ausgeschlossen.append(grund)
    else:
        behalten.append(idx)              # nur valide Zeilen behalten

df = df.loc[behalten].copy()
```

Weiterer Loop in **Notebook 02**, Abschnitt 3 (LLM-Batch-Verarbeitung):

```python
for start in range(0, min(len(df_mit_beschr), 30), batch_groesse):
    batch = df_mit_beschr['beschreibung'].iloc[start:start+batch_groesse].tolist()
    ergebnisse.extend(llm_extrahiere_ausstattung(batch))
```

---

#### 5. Prozedurales oder objektorientiertes Programmieren

Das Projekt verwendet durchgaengig **OOP** mit drei Klassen:

**`Inserat` (dataclass)** - `src/models.py`
- Felder: `titel`, `preis_raw`, `flaeche_raw`, `zimmer_raw`, `ort_raw` + abgeleitete Felder
- `__post_init__()`: automatisches Parsing aller Rohstrings nach Instanziierung
- `ist_valide()`: prueft Plausibilitaet aller Kernfelder
- `to_dict()`: Konvertierung fuer pandas/DB

**`ImmobilienScraper`** - `src/scraper.py`
- `scrape_flatfox()`: HTTP-Requests + HTML-Parsing
- `generiere_beispieldaten()`: BFS-basierter Fallback-Generator
- `scrape_alle_staedte()`: orchestriert Scraping + Fallback-Logik

**`ImmobilienDB`** - `src/database.py`
- `_erstelle_tabellen()`: CREATE TABLE IF NOT EXISTS
- `inserat_speichern()`: INSERT OR IGNORE (Duplikate werden uebersprungen)
- `bulk_speichern()`: iteriert Liste von Inserat-Objekten
- `preisstatistik_pro_stadt()`: SQL GROUP BY mit AVG, MIN, MAX, COUNT
- `nach_kanton_laden()`: SQL LEFT JOIN mit Kantonstabelle

---

#### 6. Tabellen und Visualisierungen

**Notebook 04** erstellt ein 4-Panel Dashboard mit matplotlib/seaborn:

| Plot | Typ | Inhalt |
|---|---|---|
| Panel 1 | Boxplot (seaborn) | Preisverteilung nach Stadt + Median-Linie |
| Panel 2 | Violinplot (seaborn) | Preisverteilung nach Zimmeranzahl |
| Panel 3 | Horizontales Balkendiagramm | Durchschnittlicher Preis/m2 pro Stadt |
| Panel 4 | Scatterplot (matplotlib) | Flaeche vs. Preis, farbig nach Stadt |
| Extra | Heatmap (seaborn) | Pearson-Korrelationsmatrix |
| Extra | Regressions-Scatterplot | Flaeche vs. Preis + Regressionslinie |
| Extra | Folium-Karte | Interaktive CH-Karte mit Preisinformation pro Stadt |

Tabellen: `df.groupby('stadt').agg()` in Notebook 03 und in der Streamlit App.

---

#### 7. Statistische Analyse mit p-Wert

Drei statistische Methoden in **Notebook 03** (alle mit p-Wert):

**Pearson-Korrelation** (`scipy.stats.pearsonr`):
```python
for c1, c2 in combinations(['preis_chf','flaeche_m2','zimmer_anzahl','preis_pro_m2'], 2):
    r, p = stats.pearsonr(df[c1], df[c2])
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
    # Staerkste Korrelation: preis_chf ~ flaeche_m2 -> r=0.803, p=4.22e-114 ***
```

**Welch's t-Test** (`scipy.stats.ttest_ind`, `equal_var=False`):
```python
# H0: kein signifikanter Preisunterschied zwischen Zuerich und anderen Staedten
for stadt in andere_staedte:
    t_stat, p_wert = stats.ttest_ind(zuerich_preise, gruppe, equal_var=False)
    # Ergebnis: Zuerich signifikant teurer als 8/9 Staedten (p < 0.05)
    # Ausnahme: Genf (p = 0.163 -> H0 beibehalten)
```

**Lineare Regression** (`scipy.stats.linregress`):
```python
steigung, achsenabschnitt, r_wert, p_wert, std_fehler = stats.linregress(flaeche, preis)
# Preis = 12.14 x Flaeche + 976.24
# R2 = 0.645, p = 4.22e-114 ***
```

---

#### 8. Code auf Moodle

ZIP-Abgabe enthaelt alle Notebooks, `src/`, `app/`, `requirements.txt` und `README.md`.
Grosse Datendateien (`data/*.csv`, `*.db`) sind via `.gitignore` ausgeschlossen.

---

### Bonuspunkte (6/6)

---

#### B1. Web Scraper

`ImmobilienScraper.scrape_flatfox()` in `src/scraper.py`:

```python
self.session = requests.Session()
self.session.headers.update({"User-Agent": "Mozilla/5.0 ...", "Accept-Language": "de-CH"})

response = self.session.get(url, timeout=10)
response.raise_for_status()
soup = BeautifulSoup(response.text, "lxml")
karten = soup.find_all("div", class_=re.compile(r"listing-thumb|flat-list"))

for karte in karten:
    preis_raw = karte.find(class_=re.compile(r"price|preis")).get_text(strip=True)
    # -> Inserat-Objekt mit geparsten Werten
```

Quelle: Flatfox.ch (oeffentliche Inseratsseite, keine Authentifizierung noetig).
Beinhaltet Rate-Limiting (`time.sleep`) fuer hoefliches Scraping.

---

#### B2. Datenbank + SQL

`ImmobilienDB` in `src/database.py` - vier SQL-Patterns demonstriert:

```sql
-- CREATE TABLE
CREATE TABLE IF NOT EXISTS inserate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT, preis_chf REAL, flaeche_m2 REAL,
    zimmer_anzahl REAL, plz TEXT, stadt TEXT, ...
);

-- INSERT mit Duplikat-Schutz
INSERT OR IGNORE INTO inserate (titel, preis_chf, ...)
VALUES (:titel, :preis_chf, ...);

-- SELECT + GROUP BY + Aggregatfunktionen
SELECT stadt,
    COUNT(*)                    AS anzahl,
    ROUND(AVG(preis_chf), 0)   AS mittlerer_preis,
    ROUND(MIN(preis_chf), 0)   AS min_preis,
    ROUND(MAX(preis_chf), 0)   AS max_preis,
    ROUND(AVG(preis_pro_m2),2) AS preis_pro_m2
FROM inserate
GROUP BY stadt
ORDER BY mittlerer_preis DESC;

-- LEFT JOIN mit Kantonstabelle
SELECT i.*, k.kanton_kuerzel, k.kanton_name, k.region
FROM inserate i
LEFT JOIN kantone k ON i.plz = k.plz
WHERE k.kanton_kuerzel = 'ZH';
```

---

#### B3. LLM-Unterstuetzung (Claude API)

**Notebook 02**, Abschnitt 3 - Klassifikation von Ausstattungsmerkmalen:

```python
def llm_extrahiere_ausstattung(beschreibungen: list[str]) -> list[dict]:
    prompt = f"""Analysiere {len(beschreibungen)} Wohnungsbeschreibungen.
Antworte NUR mit JSON-Array. Felder: balkon, parking, renoviert, luxus (boolean).
Beschreibungen:
{batch_text}
JSON:"""

    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={'Content-Type': 'application/json'},
        json={
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 1000,
            'messages': [{'role': 'user', 'content': prompt}]
        }
    )
    # Extrahiert strukturierte JSON-Antwort:
    # [{"balkon": true, "parking": false, "renoviert": true, "luxus": false}, ...]
    return json.loads(re.search(r'\[.*\]', response.json()['content'][0]['text'], re.DOTALL).group())
```

Die LLM-Features (`balkon`, `parking`, `renoviert`, `luxus`) werden als neue Spalten in den DataFrame integriert und koennen als Kovariaten in Folgeanalysen genutzt werden.

---

#### B4. Web Application (Streamlit)

`app/streamlit_app.py` - interaktive Datenexploration:

- **Filter-Sidebar:** Multiselect fuer Staedte, Preis-Slider, Zimmer-Slider
- **KPI-Kacheln:** Anzahl Inserate, Durchschnittspreis, Durchschnittsflaeche, Staedteanzahl
- **Tab 1 - Uebersicht:** Boxplot Preisverteilung + Balkendiagramm Preis/m2
- **Tab 2 - Analyse:** Scatter Flaeche/Preis mit Regressionslinie + Violinplot Zimmergruppen
- **Tab 3 - Daten:** Zusammenfassende Tabelle + gefilterte Rohdaten
- **Tab 4 - Statistik:** Pearson-Korrelationsmatrix + Welch t-Test Tabelle

Starten: `streamlit run app/streamlit_app.py`

---

#### B5. GitHub Repository

Repository: **https://github.com/haerrbas/sp-immobilien-schweiz** (public)

- Vollstaendige Projektstruktur mit `src/`, `notebooks/`, `app/`
- `.gitignore` schliesst `data/*.csv`, `data/*.db`, `__pycache__/` aus
- `requirements.txt` mit allen Abhaengigkeiten
- Dieses README mit vollstaendiger Dokumentation
- 2 Contributors: [@haerrbas](https://github.com/haerrbas) + [@schmusan](https://github.com/schmusan)

---

#### B6. Kreativitaet

Vier kreative Erweiterungen die nicht Teil der Vorlesungsinhalte waren:

**1. Interaktive Folium-Karte** (Notebook 04):
Geographische Karte der Schweiz mit CircleMarkern pro Stadt. Kreisgroesse = Anzahl Inserate, Farbe = Preisniveau (gruen/orange/rot). Klickbare Popups mit Preisinformation.

**2. LLM-Feature-Extraction** (Notebook 02):
Automatische Klassifikation von Ausstattungsmerkmalen aus Freitextbeschreibungen via Claude API. Ergebnis sind strukturierte boolean-Features fuer Weiteranalyse.

**3. Preiskategorie-Klassifikation** (Notebook 02):
Automatische Einstufung jedes Inserats in `guenstig / mittel / teuer` basierend auf absoluten CHF-Schwellwerten - ermoeglicht kategoriale Gruppenvergleiche.

**4. Preis/m2-Normierung**:
Abgeleitetes Feature `preis_pro_m2 = preis_chf / flaeche_m2` ermoeglicht staedteuebergreifende Vergleiche unabhaengig von der Wohnungsgroesse. Visualisiert in Panel 3 des Dashboards und in der Streamlit App.

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
R2 = 0.645 (64.5% Varianzaufklaerung)
p-Wert = 4.22e-114 (*** hochsignifikant)
-> Jeder zusaetzliche m2 kostet im Schnitt CHF 12.14 mehr Miete
```

### Welch t-Test: Zuerich vs. andere Staedte (alpha = 0.05)

Zuerich ist signifikant teurer als Basel, Bern, Biel, Lausanne, Lugano, Luzern, St. Gallen und Winterthur.
Kein signifikanter Unterschied zu Genf (p = 0.163, H0 beibehalten).

---

## Technologie-Stack

| Tool | Version | Verwendung |
|---|---|---|
| Python | 3.11 | Programmiersprache |
| pandas | 2.2 | Datenverarbeitung, DataFrames |
| numpy | 1.26 | Numerische Berechnungen |
| matplotlib | 3.8 | Plots und Visualisierungen |
| seaborn | 0.13 | Statistische Grafiken |
| scipy | 1.12 | Pearson r, t-Test, linregress |
| sqlite3 | built-in | Datenbank |
| BeautifulSoup | 4.12 | HTML-Parsing |
| requests | 2.31 | HTTP-Requests |
| streamlit | 1.32 | Web App |
| folium | 0.16 | Geographische Karten |
| Anthropic Claude API | 0.21 | LLM-Datenanalyse |

---

## Gruppe

| Name | GitHub |
|---|---|
| Basil Haerri | [@haerrbas](https://github.com/haerrbas) |
| Sandro Oswald Schmuki | [@schmusan](https://github.com/schmusan) |

---

*ZHAW School of Management and Law - Scientific Programming FS2026 - Dr. Mario Gellrich*
