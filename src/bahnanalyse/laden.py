"""Lädt die Parquet-Dateien mit DuckDB und bereitet sie für die Auswertung auf.

DuckDB liest die Dateien direkt und filtert per SQL, bevor die Daten in pandas
landen. Ein Monat hat mehrere Millionen Zeilen, deshalb wird nur geladen,
was gebraucht wird.
"""

from pathlib import Path

import pandas as pd

# Zuordnung der Zuggattungen zu groben Kategorien.
FERNVERKEHR = {"ICE", "IC", "EC", "ECE", "RJ", "RJX", "NJ", "EN", "FLX", "TGV", "EST"}
S_BAHN = {"S"}

SPALTEN = [
    "station_name",
    "eva",
    "train_type",
    "train_number",
    "line_number",
    "train_line_ride_id",
    "delay_in_min",
    "time",
    "arrival_is_canceled",
    "departure_is_canceled",
]


def kategorie(zugtyp: str | None) -> str:
    """Ordnet eine Zuggattung (z. B. "ICE", "RE", "S") einer Kategorie zu."""
    if zugtyp is None or pd.isna(zugtyp):
        return "Unbekannt"
    if zugtyp in FERNVERKEHR:
        return "Fernverkehr"
    if zugtyp in S_BAHN:
        return "S-Bahn"
    return "Regionalverkehr"


def lade_halte(dateien: list[Path], bahnhof_filter: str | None = None) -> pd.DataFrame:
    """Lädt alle Halte aus den Parquet-Dateien.

    bahnhof_filter: optionaler Textteil des Bahnhofsnamens, z. B. "Berlin".
    """
    import duckdb  # erst hier importieren, damit die Tests ohne DuckDB laufen

    if not dateien:
        raise ValueError("Keine Parquet-Dateien angegeben. Erst scripts/download.py ausführen.")

    pfade = [str(p) for p in dateien]
    sql = f"SELECT {', '.join(SPALTEN)} FROM read_parquet(?)"
    parameter: list = [pfade]
    if bahnhof_filter:
        sql += " WHERE station_name ILIKE ?"
        parameter.append(f"%{bahnhof_filter}%")

    df = duckdb.execute(sql, parameter).df()
    return aufbereiten(df)


def aufbereiten(df: pd.DataFrame) -> pd.DataFrame:
    """Ergänzt abgeleitete Spalten: Kategorie, Ausfall, Stunde, Wochentag."""
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df["kategorie"] = df["train_type"].map(kategorie)
    df["ausgefallen"] = df["arrival_is_canceled"].fillna(False) | df["departure_is_canceled"].fillna(False)
    df["stunde"] = df["time"].dt.hour
    df["wochentag"] = df["time"].dt.day_of_week  # 0 = Montag
    return df
