"""
models.py
---------
OOP-Datenmodelle fuer das Immobilienprojekt.
Definiert die Klasse `Inserat` zur strukturierten Speicherung
eines Immobilieninserats.
"""

from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class Inserat:
    """
    Repraesentiert ein einzelnes Immobilieninserat.
    Verwendet Python dataclass fuer saubere OOP-Struktur.
    """
    titel: str
    preis_raw: str
    flaeche_raw: str
    zimmer_raw: str
    ort_raw: str
    url: str = ""
    beschreibung: str = ""

    preis_chf: Optional[float] = field(default=None, init=False)
    flaeche_m2: Optional[float] = field(default=None, init=False)
    zimmer_anzahl: Optional[float] = field(default=None, init=False)
    plz: Optional[str] = field(default=None, init=False)
    stadt: Optional[str] = field(default=None, init=False)
    preis_pro_m2: Optional[float] = field(default=None, init=False)

    def __post_init__(self):
        self.preis_chf = self._parse_preis(self.preis_raw)
        self.flaeche_m2 = self._parse_flaeche(self.flaeche_raw)
        self.zimmer_anzahl = self._parse_zimmer(self.zimmer_raw)
        self.plz, self.stadt = self._parse_ort(self.ort_raw)
        self._berechne_preis_pro_m2()

    def _parse_preis(self, raw: str) -> Optional[float]:
        """Extrahiert CHF-Preis via Regex. Bsp: 'CHF 2\'450.- / Monat' -> 2450.0"""
        if not raw:
            return None
        cleaned = re.sub(r"['\\s]", "", raw)
        match = re.search(r"(\\d+(?:\\.\\d+)?)", cleaned)
        return float(match.group(1)) if match else None

    def _parse_flaeche(self, raw: str) -> Optional[float]:
        """Extrahiert m2-Flaeche via Regex. Bsp: '85 m2' -> 85.0"""
        if not raw:
            return None
        match = re.search(r"(\\d+(?:[.,]\\d+)?)\\s*m[2]?", raw, re.IGNORECASE)
        return float(match.group(1).replace(",", ".")) if match else None

    def _parse_zimmer(self, raw: str) -> Optional[float]:
        """Extrahiert Zimmeranzahl via Regex. Bsp: '3.5 Zimmer' -> 3.5"""
        if not raw:
            return None
        match = re.search(r"(\\d+(?:[.,]\\d+)?)", raw)
        return float(match.group(1).replace(",", ".")) if match else None

    def _parse_ort(self, raw: str) -> tuple:
        """Trennt PLZ und Stadtname via Regex. Bsp: '8001 Zuerich' -> ('8001', 'Zuerich')"""
        if not raw:
            return None, None
        match = re.match(r"(\\d{4})\\s+([^\\,]+)", raw.strip())
        if match:
            return match.group(1), match.group(2).strip()
        return None, raw.strip()

    def _berechne_preis_pro_m2(self):
        if self.preis_chf and self.flaeche_m2 and self.flaeche_m2 > 0:
            self.preis_pro_m2 = round(self.preis_chf / self.flaeche_m2, 2)

    def ist_valide(self) -> bool:
        return all([
            self.preis_chf is not None and 100 < self.preis_chf < 50000,
            self.flaeche_m2 is not None and 10 < self.flaeche_m2 < 1000,
            self.zimmer_anzahl is not None and 0 < self.zimmer_anzahl <= 20,
            self.plz is not None,
        ])

    def to_dict(self) -> dict:
        return {
            "titel": self.titel,
            "preis_chf": self.preis_chf,
            "flaeche_m2": self.flaeche_m2,
            "zimmer_anzahl": self.zimmer_anzahl,
            "plz": self.plz,
            "stadt": self.stadt,
            "preis_pro_m2": self.preis_pro_m2,
            "url": self.url,
            "beschreibung": self.beschreibung,
        }

    def __repr__(self):
        return f"Inserat('{self.stadt}', CHF {self.preis_chf}, {self.flaeche_m2}m2, {self.zimmer_anzahl} Zi.)"
