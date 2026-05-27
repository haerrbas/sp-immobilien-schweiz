"""
scraper.py
----------
Web Scraper fuer Schweizer Immobilieninserate.
Nutzt oeffentlich verfuegbare Daten von Flatfox.ch.
Fallback: Generiert realistische Beispieldaten.
"""

import requests, time, random, re
import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional
from src.models import Inserat

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "de-CH,de;q=0.9",
}
BASE_URL = "https://flatfox.ch/de/search/"

STAEDTE_DATEN = {
    "Zuerich":    {"plz_bereich": range(8001, 8099), "basis_preis": 2400, "stdabw": 600},
    "Genf":       {"plz_bereich": range(1200, 1230), "basis_preis": 2200, "stdabw": 500},
    "Bern":       {"plz_bereich": range(3000, 3030), "basis_preis": 1800, "stdabw": 400},
    "Basel":      {"plz_bereich": range(4000, 4060), "basis_preis": 1900, "stdabw": 450},
    "Luzern":     {"plz_bereich": range(6000, 6020), "basis_preis": 1700, "stdabw": 350},
    "Lausanne":   {"plz_bereich": range(1000, 1020), "basis_preis": 2000, "stdabw": 500},
    "Winterthur": {"plz_bereich": range(8400, 8415), "basis_preis": 1600, "stdabw": 300},
    "St. Gallen": {"plz_bereich": range(9000, 9015), "basis_preis": 1500, "stdabw": 280},
    "Lugano":     {"plz_bereich": range(6900, 6915), "basis_preis": 1800, "stdabw": 400},
    "Biel":       {"plz_bereich": range(2500, 2510), "basis_preis": 1400, "stdabw": 280},
}


class ImmobilienScraper:
    """Scraper fuer Schweizer Immobilieninserate."""

    def __init__(self, delay_sek: float = 1.5):
        self.delay_sek = delay_sek
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def scrape_flatfox(self, stadt: str = "zuerich", max_seiten: int = 3) -> list:
        inserate = []
        print(f"Starte Scraping fuer: {stadt.title()}")
        for seite in range(1, max_seiten + 1):
            url = f"{BASE_URL}?query={stadt}&object_category=apartment&type=rent&page={seite}"
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")
                neue = self._parse_seite(soup, stadt)
                if not neue:
                    break
                inserate.extend(neue)
                print(f"  Seite {seite}: {len(neue)} Inserate")
                time.sleep(self.delay_sek + random.uniform(0, 0.5))
            except requests.RequestException as e:
                print(f"  Seite {seite} fehlgeschlagen: {e}")
                break
        return inserate

    def _parse_seite(self, soup, stadt: str) -> list:
        inserate = []
        karten = soup.find_all("div", class_=re.compile(r"listing-thumb|flat-list"))
        for karte in karten:
            try:
                ins = self._parse_karte(karte, stadt)
                if ins:
                    inserate.append(ins)
            except Exception:
                continue
        return inserate

    def _parse_karte(self, karte, stadt: str) -> Optional[Inserat]:
        preis_el = karte.find(class_=re.compile(r"price|preis"))
        preis_raw = preis_el.get_text(strip=True) if preis_el else ""
        details = karte.find_all(class_=re.compile(r"feature|detail|info"))
        flaeche_raw, zimmer_raw = "", ""
        for el in details:
            text = el.get_text(strip=True)
            if re.search(r"m[2]", text):
                flaeche_raw = text
            elif re.search(r"[Zz]immer|[Zz]i\.", text):
                zimmer_raw = text
        ort_el = karte.find(class_=re.compile(r"address|location|ort"))
        ort_raw = ort_el.get_text(strip=True) if ort_el else stadt
        titel_el = karte.find(["h2", "h3", "h4"])
        titel = titel_el.get_text(strip=True) if titel_el else f"Wohnung in {stadt}"
        link = karte.find("a", href=True)
        url = f"https://flatfox.ch{link['href']}" if link else ""
        if not preis_raw:
            return None
        return Inserat(titel=titel, preis_raw=preis_raw, flaeche_raw=flaeche_raw,
                       zimmer_raw=zimmer_raw, ort_raw=ort_raw, url=url)

    def generiere_beispieldaten(self, n_pro_stadt: int = 40) -> list:
        """Generiert realistische Testdaten basierend auf BFS-Preisstatistiken."""
        print(f"Generiere Beispieldaten ({n_pro_stadt}/Stadt)...")
        inserate = []
        zimmer_opt = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        for stadt, params in STAEDTE_DATEN.items():
            for i in range(n_pro_stadt):
                zimmer = random.choice(zimmer_opt)
                flaeche = max(20, min(300, round(zimmer * random.uniform(22, 32) + random.gauss(0, 8), 0)))
                preis = max(600, round((params["basis_preis"] + (flaeche - 70) * random.uniform(8, 15)
                            + random.gauss(0, params["stdabw"] * 0.3)) / 50) * 50)
                plz = str(random.choice(list(params["plz_bereich"])))
                inserate.append(Inserat(
                    titel=f"{zimmer}-Zimmer-Wohnung in {stadt}",
                    preis_raw=f"CHF {preis:,.0f}".replace(",", "'"),
                    flaeche_raw=f"{flaeche:.0f} m2",
                    zimmer_raw=f"{zimmer} Zimmer",
                    ort_raw=f"{plz} {stadt}",
                    url=f"https://beispiel.ch/inserat/{stadt.lower()}-{i+1}",
                    beschreibung="Schoene Wohnung in zentraler Lage.",
                ))
        random.shuffle(inserate)
        valide = [ins for ins in inserate if ins.ist_valide()]
        print(f"Valide Beispiel-Inserate: {len(valide)}")
        return valide

    def scrape_alle_staedte(self, staedte=None, fallback_auf_beispiel=True, n_beispiel=40):
        if staedte is None:
            staedte = ["zuerich", "bern", "basel", "genf", "luzern"]
        alle = []
        for stadt in staedte:
            alle.extend(self.scrape_flatfox(stadt, max_seiten=2))
        if not alle and fallback_auf_beispiel:
            print("No real data available - Using sample data.")
            alle = self.generiere_beispieldaten(n_beispiel)
        elif len(alle) < 50 and fallback_auf_beispiel:
            alle.extend(self.generiere_beispieldaten(n_beispiel))
        df = pd.DataFrame([ins.to_dict() for ins in alle if ins.ist_valide()])
        print(f"Total result: {len(df)} Inserate als DataFrame")
        return df
