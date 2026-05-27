# Swiss Real Estate Prices
## Scientific Programming - FS2026

**Basil Haerri / Sandro Oswald Schmuki**
ZHAW School of Management and Law

---

## 1. Introduction

### Background
- Rental prices in Switzerland are among the highest in Europe
- Strong regional differences between cities and cantons
- Data-driven analysis can benefit tenants and investors

### Research Questions
1. Which features (area, rooms, location) correlate most strongly with rental price?
2. Are there statistically significant price differences between Swiss cities?
3. How well can rental prices be explained by a linear regression?

---

## 2. Materials and Methods

### Data Collection
- Source: Flatfox.ch (web scraper using BeautifulSoup + requests)
- Fallback: Synthetic generator (500 listings, based on FSO price statistics 2023/24)
- Scope: 500 rental apartment listings from 10 Swiss cities

### Data Preparation
- Regex parsing: price, area, rooms, ZIP extracted from raw strings
- Plausibility filter: price CHF 300-15,000, area 15-400 m2, rooms 0.5-12
- Feature engineering: price/m2, price category, room group
- LLM analysis: Claude API classifies amenity features (balcony, parking, renovated)

### Statistical Methods
- Descriptive statistics: mean, median, standard deviation per city
- Correlation analysis: Pearson r with two-sided p-value (scipy.stats.pearsonr)
- t-test: Welch's independent t-test (scipy.stats.ttest_ind, equal_var=False)
- Regression: Simple linear regression (scipy.stats.linregress)

### Tools
Python 3.11, pandas, numpy, matplotlib, seaborn, scipy, sqlite3, BeautifulSoup, Streamlit, Anthropic Claude API

---

## 3. Results & Discussion

### Descriptive Statistics

| City | n | Avg CHF | Median | Std |
|---|---|---|---|---|
| Zurich | 50 | 2,517 | 2,475 | 494 |
| Geneva | 50 | 2,384 | 2,375 | 452 |
| Lausanne | 50 | 2,064 | 2,050 | 460 |
| Basel | 50 | 1,979 | 1,900 | 443 |
| Bern | 50 | 1,907 | 1,800 | 424 |
| Lucerne | 50 | 1,758 | 1,775 | 407 |
| Winterthur | 50 | 1,635 | 1,650 | 412 |
| Biel | 50 | 1,522 | 1,475 | 484 |

### Correlation Analysis (Pearson r)

| Variables | r | p-value | Significance |
|---|---|---|---|
| Price ~ Area | 0.803 | 4.22e-114 | *** |
| Price ~ Rooms | 0.766 | 1.19e-97 | *** |
| Area ~ Rooms | 0.943 | 9.22e-241 | *** |
| Price ~ Price/m2 | -0.326 | 8.41e-14 | *** |

Interpretation: Area and number of rooms are the strongest price predictors.

### Linear Regression: Price ~ Area

```
Price = 12.14 x Area (m2) + 976.24
R2 = 0.645  (64.5% of price variance explained)
p = 4.22e-114  (*** highly significant)
-> Each additional m2 costs on average CHF 12.14 more in rent
```

### t-test Results (alpha = 0.05, Welch's)
Zurich is significantly more expensive than 8 out of 9 other cities.
Exception: Geneva (p = 0.163 -> H0 retained - similar price level to Zurich).

---

## 4. Conclusions

1. Area is the strongest price predictor (r=0.80, p<0.001)
2. City location is significant - Zurich and Geneva significantly more expensive
3. Linear regression explains 64.5% of price variance
4. Pipeline runs fully automatically - from scraping to interactive web app

---

## Appendix: Points Evidence

### Mandatory Requirements

**1. Real-world data:**
`src/scraper.py` - HTTP GET on Flatfox.ch using BeautifulSoup

**2. Regex parsing:**
```python
def _parse_price(self, raw: str) -> Optional[float]:
    cleaned = re.sub(r"['\s]", "", raw)
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    return float(match.group(1)) if match else None
```
All 4 parsers in `src/models.py`: price, area, rooms, ZIP+city

**3. Data structures:**
Notebook 01, Cell 3: `list()`, `set()`, `dict(sorted(...))`, `tuple()` explicitly shown

**4. Control structures:**
Notebook 02: `for idx, row in df.iterrows()` + `if/elif/else` plausibility filter

**5. OOP:**
- `@dataclass class Listing` - 6 fields, `__post_init__`, `is_valid()`, `to_dict()`
- `class ImmobilienScraper` - `scrape_flatfox()`, `generate_sample_data()`, `scrape_all_cities()`
- `class ImmobilienDB` - `_create_tables()`, `save_listing()`, `bulk_save()`, `price_stats_by_city()`

**6. Visualizations:**
Notebook 04: 4-panel dashboard (boxplot, violin, bar chart, scatter), correlation heatmap, Folium map

**7. Statistics with p-value:**
- `scipy.stats.pearsonr` -> r + p-value for all variable pairs
- `scipy.stats.ttest_ind(equal_var=False)` -> Welch's t-test Zurich vs. each city
- `scipy.stats.linregress` -> regression p-value = 4.22e-114

**8. Moodle submission:** ZIP file with all notebooks, src/, app/

### Bonus Points

**B1 Web Scraper:** `ImmobilienScraper.scrape_flatfox()` - BeautifulSoup + requests

**B2 Database + SQL:** SQLite ImmobilienDB - CREATE TABLE, INSERT OR IGNORE, GROUP BY, LEFT JOIN

**B3 LLM:** Claude API in Notebook 02 - JSON-structured amenity classification

**B4 Web App:** Streamlit - filter sidebar, 4 tabs, KPIs, charts, statistics

**B5 GitHub:** https://github.com/haerrbas/sp-immobilien-schweiz (public, .gitignore for data/)

**B6 Creativity:** Folium map CH, price/m2 feature, price category function, LLM features
