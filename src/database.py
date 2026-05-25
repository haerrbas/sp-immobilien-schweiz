"""
database.py
-----------
SQLite-Datenbanklogik fuer das Immobilienprojekt.
Speichert und liest Inserate via SQLAlchemy + raw SQL-Queries.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional
from src.models import Inserat


DB_PATH = Path("data/immobilien.db")


class ImmobilienDB:
    """
    Verwaltet die SQLite-Datenbank fuer Immobilieninserate.
    Demonstriert: CREATE, INSERT, SELECT mit SQL-Queries.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._erstelle_tabellen()

    def _verbinden(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _erstelle_tabellen(self):
        sql = """
        CREATE TABLE IF NOT EXISTS inserate (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            titel           TEXT,
            preis_chf       REAL,
            flaeche_m2      REAL,
            zimmer_anzahl   REAL,
            plz             TEXT,
            stadt           TEXT,
            preis_pro_m2    REAL,
            url             TEXT UNIQUE,
            beschreibung    TEXT,
            erstellt_am     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS kantone (
            plz             TEXT PRIMARY KEY,
            kanton_kuerzel  TEXT,
            kanton_name     TEXT,
            region          TEXT
        );
        """
        with self._verbinden() as con:
            con.executescript(sql)

    def inserat_speichern(self, inserat: Inserat) -> bool:
        sql = """
        INSERT OR IGNORE INTO inserate
            (titel, preis_chf, flaeche_m2, zimmer_anzahl, plz, stadt,
             preis_pro_m2, url, beschreibung)
        VALUES
            (:titel, :preis_chf, :flaeche_m2, :zimmer_anzahl, :plz, :stadt,
             :preis_pro_m2, :url, :beschreibung)
        """
        with self._verbinden() as con:
            cursor = con.execute(sql, inserat.to_dict())
            return cursor.rowcount > 0

    def bulk_speichern(self, inserate: list) -> int:
        gespeichert = 0
        for ins in inserate:
            if ins.ist_valide() and self.inserat_speichern(ins):
                gespeichert += 1
        print(f"Gespeichert: {gespeichert} von {len(inserate)}")
        return gespeichert

    def alle_laden(self) -> pd.DataFrame:
        sql = "SELECT * FROM inserate ORDER BY erstellt_am DESC"
        with self._verbinden() as con:
            return pd.read_sql_query(sql, con)

    def nach_kanton_laden(self, kanton_kuerzel: str) -> pd.DataFrame:
        sql = """
        SELECT i.*, k.kanton_kuerzel, k.kanton_name, k.region
        FROM inserate i
        LEFT JOIN kantone k ON i.plz = k.plz
        WHERE k.kanton_kuerzel = ?
        ORDER BY i.preis_chf
        """
        with self._verbinden() as con:
            return pd.read_sql_query(sql, con, params=(kanton_kuerzel,))

    def preisstatistik_pro_stadt(self) -> pd.DataFrame:
        sql = """
        SELECT
            stadt, plz,
            COUNT(*)                     AS anzahl_inserate,
            ROUND(AVG(preis_chf), 0)     AS mittlerer_preis,
            ROUND(MIN(preis_chf), 0)     AS min_preis,
            ROUND(MAX(preis_chf), 0)     AS max_preis,
            ROUND(AVG(preis_pro_m2), 2)  AS mittlerer_preis_pro_m2,
            ROUND(AVG(flaeche_m2), 1)    AS mittlere_flaeche,
            ROUND(AVG(zimmer_anzahl), 1) AS mittlere_zimmer
        FROM inserate
        WHERE stadt IS NOT NULL AND preis_chf IS NOT NULL
        GROUP BY stadt, plz
        HAVING COUNT(*) >= 2
        ORDER BY mittlerer_preis DESC
        """
        with self._verbinden() as con:
            return pd.read_sql_query(sql, con)

    def kantone_befuellen(self):
        kantone_data = [
            ("8001","ZH","Zuerich","Deutschschweiz"),("8002","ZH","Zuerich","Deutschschweiz"),
            ("8003","ZH","Zuerich","Deutschschweiz"),("8004","ZH","Zuerich","Deutschschweiz"),
            ("8005","ZH","Zuerich","Deutschschweiz"),("8008","ZH","Zuerich","Deutschschweiz"),
            ("8032","ZH","Zuerich","Deutschschweiz"),("8048","ZH","Zuerich","Deutschschweiz"),
            ("8050","ZH","Zuerich","Deutschschweiz"),("8051","ZH","Zuerich","Deutschschweiz"),
            ("8052","ZH","Zuerich","Deutschschweiz"),("8055","ZH","Zuerich","Deutschschweiz"),
            ("3000","BE","Bern","Deutschschweiz"),("3011","BE","Bern","Deutschschweiz"),
            ("3012","BE","Bern","Deutschschweiz"),("3013","BE","Bern","Deutschschweiz"),
            ("1200","GE","Genf","Romandie"),("1201","GE","Genf","Romandie"),
            ("1202","GE","Genf","Romandie"),("1203","GE","Genf","Romandie"),
            ("1000","VD","Waadt","Romandie"),("1003","VD","Waadt","Romandie"),
            ("6000","LU","Luzern","Deutschschweiz"),("6002","LU","Luzern","Deutschschweiz"),
            ("4000","BS","Basel-Stadt","Deutschschweiz"),("4051","BS","Basel-Stadt","Deutschschweiz"),
            ("6900","TI","Tessin","Tessin"),("6901","TI","Tessin","Tessin"),
        ]
        sql = "INSERT OR IGNORE INTO kantone (plz, kanton_kuerzel, kanton_name, region) VALUES (?, ?, ?, ?)"
        with self._verbinden() as con:
            con.executemany(sql, kantone_data)
        print(f"PLZ-Kanton-Eintraege geladen: {len(kantone_data)}")

    def anzahl_inserate(self) -> int:
        with self._verbinden() as con:
            return con.execute("SELECT COUNT(*) FROM inserate").fetchone()[0]

    def __repr__(self):
        return f"ImmobilienDB('{self.db_path}', {self.anzahl_inserate()} Inserate)"
