# Swiss Real Estate Prices - SP Project FS2026

> **Research Question:** Which factors (canton, floor area, number of rooms, ZIP code) influence rental prices in Switzerland, and are there statistically significant price differences between regions?

**Module:** Scientific Programming - ZHAW School of Management and Law - FS2026
**Group:** Basil Haerri [@haerrbas](https://github.com/haerrbas) / Sandro Oswald Schmuki [@schmusan](https://github.com/schmusan)

---

## Key Results

| Metric | Value |
|---|---|
| Dataset | 500 listings from 10 Swiss cities |
| Most expensive city | Zurich (avg CHF 2,517/mo.) |
| Most affordable city | Biel (avg CHF 1,522/mo.) |
| Correlation price-area | r = 0.80 (p < 0.001 ***) |
| Regression R2 | 0.645 - each additional m2 costs CHF 12.14 more |
| t-test Zurich vs. others | Significantly more expensive than 8 out of 9 cities |

---

## Project Structure

```
sp-immobilien-schweiz/
├── notebooks/
│   ├── 01_data_collection.ipynb      # Web scraping, regex, DB, data structures
│   ├── 02_data_preparation.ipynb     # Cleaning, loops, LLM support (Claude API)
│   ├── 03_statistical_analysis.ipynb # Pearson r, Welch t-test, p-values, regression
│   └── 04_visualization.ipynb        # Plots, Folium map, 4-panel dashboard
├── src/
│   ├── __init__.py
│   ├── models.py      # Class Listing (OOP + regex parsers)
│   ├── database.py    # SQLite + SQL queries (CREATE, INSERT, SELECT, JOIN, GROUP BY)
│   └── scraper.py     # Web scraper + sample data generator
├── app/
│   └── streamlit_app.py   # Interactive web app (4 tabs, filter sidebar)
├── data/              # excluded via .gitignore - no large files in repo
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

## Module Requirements (detailed)

### Mandatory Requirements (8/8)

---

#### 1. Collection of Real-World Data

The `ImmobilienScraper` in `src/scraper.py` sends HTTP requests to Flatfox.ch and parses the HTML response using BeautifulSoup. If the server is unreachable, a fallback generator uses realistic price statistics from the Swiss Federal Statistical Office (FSO, 2023/24).

```python
# src/scraper.py
def scrape_flatfox(self, city: str = "zuerich", max_pages: int = 3) -> list:
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}?query={city}&object_category=apartment&type=rent&page={page}"
        response = self.session.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        new_listings = self._parse_page(soup, city)
        listings.extend(new_listings)
        time.sleep(self.delay_sec)  # polite scraping
```

Output: list of `Listing` objects with price, area, rooms, ZIP code, URL.

---

#### 2. Data Preparation with Regular Expressions

All raw strings from the scraper are converted to numeric values. Four specialized regex parsers in `src/models.py`:

```python
# src/models.py - class Listing
def _parse_price(self, raw: str) -> Optional[float]:
    # "CHF 2'450.- / month" -> 2450.0
    cleaned = re.sub(r"['\s]", "", raw)
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    return float(match.group(1)) if match else None

def _parse_area(self, raw: str) -> Optional[float]:
    # "85 m2" -> 85.0  |  "67.5 m2" -> 67.5
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*m[2]?", raw, re.IGNORECASE)
    return float(match.group(1).replace(",", ".")) if match else None

def _parse_rooms(self, raw: str) -> Optional[float]:
    # "3.5 rooms" -> 3.5  |  "4-room" -> 4.0
    match = re.search(r"(\d+(?:[.,]\d+)?)", raw)
    return float(match.group(1).replace(",", ".")) if match else None

def _parse_location(self, raw: str) -> tuple:
    # "8001 Zurich, ZH" -> ("8001", "Zurich")
    match = re.match(r"(\d{4})\s+([^\,]+)", raw.strip())
    return (match.group(1), match.group(2).strip()) if match else (None, raw.strip())
```

Demonstrated in **Notebook 01**, Section 2 (Regex Parsing Demo).

---

#### 3. Python Built-in Data Structures

Explicit demonstration of all four data structures in **Notebook 01**, Section 3:

```python
# LIST - ordered collection of all city names
cities_list = list(df_raw['city'].dropna())
# -> ['Zurich', 'Bern', 'Zurich', 'Basel', ...]

# SET - unique cities without duplicates
unique_cities = set(cities_list)
# -> {'Zurich', 'Bern', 'Basel', 'Geneva', ...}

# DICT - average price per city (sorted descending)
prices_dict = {c: round(df[df['city']==c]['price_chf'].mean(), 0)
               for c in unique_cities}
prices_dict = dict(sorted(prices_dict.items(), key=lambda x: x[1], reverse=True))
# -> {'Zurich': 2517.0, 'Geneva': 2384.0, ...}

# TUPLE - immutable price range (min, max)
price_range = (df['price_chf'].min(), df['price_chf'].max())
# -> (700.0, 3700.0)
```

Additionally: `pandas DataFrame` as the central data format across all notebooks.

---

#### 4. Conditional Statements, Loop Control and Loops

**Notebook 02**, Section 2 - plausibility filter with for-loop + if/elif/else:

```python
excluded, kept = [], []

for idx, row in df.iterrows():            # FOR loop over all rows
    reason = None

    if not (300 <= row['price_chf'] <= 15000):       # IF
        reason = f"Price out of range: CHF {row['price_chf']:.0f}"
    elif not (15 <= row['area_m2'] <= 400):          # ELIF
        reason = f"Area out of range: {row['area_m2']:.0f} m2"
    elif not (0.5 <= row['rooms'] <= 12):            # ELIF
        reason = f"Rooms out of range: {row['rooms']}"

    if reason:
        excluded.append(reason)
    else:
        kept.append(idx)

df = df.loc[kept].copy()
```

Additional loop in **Notebook 02**, Section 3 (LLM batch processing):

```python
for start in range(0, min(len(df_with_desc), 30), batch_size):
    batch = df_with_desc['description'].iloc[start:start+batch_size].tolist()
    results.extend(llm_extract_features(batch))
```

---

#### 5. Object-Oriented Programming

The project uses OOP throughout with three classes:

**`Listing` (dataclass)** - `src/models.py`
- Fields: `title`, `price_raw`, `area_raw`, `rooms_raw`, `location_raw` + derived fields
- `__post_init__()`: automatic parsing of all raw strings after instantiation
- `is_valid()`: checks plausibility of all core fields
- `to_dict()`: conversion for pandas/DB

**`ImmobilienScraper`** - `src/scraper.py`
- `scrape_flatfox()`: HTTP requests + HTML parsing
- `generate_sample_data()`: FSO-based fallback generator
- `scrape_all_cities()`: orchestrates scraping + fallback logic

**`ImmobilienDB`** - `src/database.py`
- `_create_tables()`: CREATE TABLE IF NOT EXISTS
- `save_listing()`: INSERT OR IGNORE (duplicates are skipped)
- `bulk_save()`: iterates list of Listing objects
- `price_stats_by_city()`: SQL GROUP BY with AVG, MIN, MAX, COUNT
- `load_by_canton()`: SQL LEFT JOIN with canton table

---

#### 6. Tables and Visualizations

**Notebook 04** creates a 4-panel dashboard using matplotlib/seaborn:

| Plot | Type | Content |
|---|---|---|
| Panel 1 | Boxplot (seaborn) | Price distribution by city + median line |
| Panel 2 | Violinplot (seaborn) | Price distribution by number of rooms |
| Panel 3 | Horizontal bar chart | Average price/m2 per city |
| Panel 4 | Scatterplot (matplotlib) | Area vs. price, colored by city |
| Extra | Heatmap (seaborn) | Pearson correlation matrix |
| Extra | Regression scatterplot | Area vs. price + regression line |
| Extra | Folium map | Interactive CH map with price info per city |

Tables: `df.groupby('city').agg()` in Notebook 03 and in the Streamlit app.

---

#### 7. Statistical Analysis with p-value

Three statistical methods in **Notebook 03** (all with p-value):

**Pearson Correlation** (`scipy.stats.pearsonr`):
```python
for c1, c2 in combinations(['price_chf','area_m2','rooms','price_per_m2'], 2):
    r, p = stats.pearsonr(df[c1], df[c2])
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
    # Strongest: price_chf ~ area_m2 -> r=0.803, p=4.22e-114 ***
```

**Welch's t-test** (`scipy.stats.ttest_ind`, `equal_var=False`):
```python
# H0: no significant price difference between Zurich and other cities
for city in other_cities:
    t_stat, p_value = stats.ttest_ind(zurich_prices, group, equal_var=False)
    # Result: Zurich significantly more expensive than 8/9 cities (p < 0.05)
    # Exception: Geneva (p = 0.163 -> H0 retained)
```

**Linear Regression** (`scipy.stats.linregress`):
```python
slope, intercept, r_value, p_value, std_err = stats.linregress(area, price)
# Price = 12.14 x Area + 976.24
# R2 = 0.645, p = 4.22e-114 ***
```

---

#### 8. Code Submitted on Moodle

ZIP submission contains all notebooks, `src/`, `app/`, `requirements.txt` and `README.md`.
Large data files (`data/*.csv`, `*.db`) are excluded via `.gitignore`.

---

### Bonus Points (6/6)

---

#### B1. Web Scraper

`ImmobilienScraper.scrape_flatfox()` in `src/scraper.py`:

```python
self.session = requests.Session()
self.session.headers.update({"User-Agent": "Mozilla/5.0 ...", "Accept-Language": "de-CH"})

response = self.session.get(url, timeout=10)
response.raise_for_status()
soup = BeautifulSoup(response.text, "lxml")
cards = soup.find_all("div", class_=re.compile(r"listing-thumb|flat-list"))

for card in cards:
    price_raw = card.find(class_=re.compile(r"price")).get_text(strip=True)
    # -> Listing object with parsed values
```

Source: Flatfox.ch (public listing page, no authentication required).
Includes rate-limiting (`time.sleep`) for polite scraping.

---

#### B2. Database + SQL Queries

`ImmobilienDB` in `src/database.py` - four SQL patterns demonstrated:

```sql
-- CREATE TABLE
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, price_chf REAL, area_m2 REAL,
    rooms REAL, zip TEXT, city TEXT, ...
);

-- INSERT with duplicate protection
INSERT OR IGNORE INTO listings (title, price_chf, ...)
VALUES (:title, :price_chf, ...);

-- SELECT + GROUP BY + aggregate functions
SELECT city,
    COUNT(*)                   AS count,
    ROUND(AVG(price_chf), 0)  AS avg_price,
    ROUND(MIN(price_chf), 0)  AS min_price,
    ROUND(MAX(price_chf), 0)  AS max_price,
    ROUND(AVG(price_per_m2),2) AS price_per_m2
FROM listings
GROUP BY city
ORDER BY avg_price DESC;

-- LEFT JOIN with canton table
SELECT l.*, c.canton_code, c.canton_name, c.region
FROM listings l
LEFT JOIN cantons c ON l.zip = c.zip
WHERE c.canton_code = 'ZH';
```

---

#### B3. LLM Support (Claude API)

**Notebook 02**, Section 3 - classification of amenity features:

```python
def llm_extract_features(descriptions: list[str]) -> list[dict]:
    prompt = f"""Analyze {len(descriptions)} apartment descriptions.
Reply ONLY with a JSON array. Fields: balcony, parking, renovated, luxury (boolean).
Descriptions:
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
    # Returns structured JSON:
    # [{"balcony": true, "parking": false, "renovated": true, "luxury": false}, ...]
    return json.loads(re.search(r'\[.*\]', response.json()['content'][0]['text'], re.DOTALL).group())
```

The LLM features (`balcony`, `parking`, `renovated`, `luxury`) are integrated as new columns in the DataFrame and can be used as covariates in further analysis.

---

#### B4. Web Application (Streamlit)

`app/streamlit_app.py` - interactive data exploration:

- **Filter sidebar:** Multiselect for cities, price slider, rooms slider
- **KPI tiles:** Number of listings, average price, average area, number of cities
- **Tab 1 - Overview:** Boxplot price distribution + bar chart price/m2
- **Tab 2 - Analysis:** Scatter area/price with regression line + violin plot by room group
- **Tab 3 - Data:** Summary table + filtered raw data
- **Tab 4 - Statistics:** Pearson correlation matrix + Welch t-test table

Start: `streamlit run app/streamlit_app.py`

---

#### B5. GitHub Repository

Repository: **https://github.com/haerrbas/sp-immobilien-schweiz** (public)

- Complete project structure with `src/`, `notebooks/`, `app/`
- `.gitignore` excludes `data/*.csv`, `data/*.db`, `__pycache__/`
- `requirements.txt` with all dependencies
- This README with full documentation
- 2 contributors: [@haerrbas](https://github.com/haerrbas) + [@schmusan](https://github.com/schmusan)

---

#### B6. Creativity

Four creative extensions not covered in the lecture content:

**1. Interactive Folium Map** (Notebook 04):
Geographic map of Switzerland with circle markers per city. Circle size = number of listings, color = price level (green/orange/red). Clickable popups with price information.

**2. LLM Feature Extraction** (Notebook 02):
Automatic classification of amenity features from free-text descriptions via Claude API. Result: structured boolean features for further analysis.

**3. Price Category Classification** (Notebook 02):
Automatic labeling of each listing as `affordable / mid-range / expensive` based on absolute CHF thresholds - enables categorical group comparisons.

**4. Price/m2 Normalization**:
Derived feature `price_per_m2 = price_chf / area_m2` enables cross-city comparisons independent of apartment size. Visualized in Panel 3 of the dashboard and in the Streamlit app.

---

## Statistical Results

### Correlation Analysis (Pearson r)

| Variable 1 | Variable 2 | r | p-value | Sig. |
|---|---|---|---|---|
| price_chf | area_m2 | 0.803 | 4.22e-114 | *** |
| price_chf | rooms | 0.766 | 1.19e-97 | *** |
| area_m2 | rooms | 0.943 | 9.22e-241 | *** |
| price_chf | price_per_m2 | -0.326 | 8.41e-14 | *** |

### Linear Regression: Price ~ Area

```
Price = 12.14 x Area (m2) + 976.24
R2 = 0.645 (64.5% variance explained)
p-value = 4.22e-114 (*** highly significant)
-> Each additional m2 costs on average CHF 12.14 more in rent
```

### Welch t-test: Zurich vs. other cities (alpha = 0.05)

Zurich is significantly more expensive than Basel, Bern, Biel, Lausanne, Lugano, Lucerne, St. Gallen and Winterthur.
No significant difference vs. Geneva (p = 0.163, H0 retained).

---

## Technology Stack

| Tool | Version | Usage |
|---|---|---|
| Python | 3.11 | Programming language |
| pandas | 2.2 | Data processing, DataFrames |
| numpy | 1.26 | Numerical computations |
| matplotlib | 3.8 | Plots and visualizations |
| seaborn | 0.13 | Statistical graphics |
| scipy | 1.12 | Pearson r, t-test, linregress |
| sqlite3 | built-in | Database |
| BeautifulSoup | 4.12 | HTML parsing |
| requests | 2.31 | HTTP requests |
| streamlit | 1.32 | Web app |
| folium | 0.16 | Geographic maps |
| Anthropic Claude API | 0.21 | LLM data analysis |

---

## Group

| Name | GitHub |
|---|---|
| Basil Haerri | [@haerrbas](https://github.com/haerrbas) |
| Sandro Oswald Schmuki | [@schmusan](https://github.com/schmusan) |

---

*ZHAW School of Management and Law - Scientific Programming FS2026 - Dr. Mario Gellrich*
