"""Kennzahlen zur Pünktlichkeit.

Definition wie bei der DB: Ein Halt gilt als pünktlich, wenn die Verspätung
unter 6 Minuten liegt. Ausgefallene Halte zählen nicht in die
Pünktlichkeitsquote, sondern werden getrennt als Ausfallquote ausgewiesen.
"""

import pandas as pd

PUENKTLICH_BIS_MIN = 5  # 0 bis 5 Minuten = pünktlich


def _gefahren(df: pd.DataFrame) -> pd.DataFrame:
    """Nur Halte, die stattgefunden haben und eine Verspätungsangabe haben."""
    return df[~df["ausgefallen"] & df["delay_in_min"].notna()]


def puenktlichkeitsquote(df: pd.DataFrame) -> float:
    """Anteil pünktlicher Halte in Prozent (0–100)."""
    gefahren = _gefahren(df)
    if gefahren.empty:
        return float("nan")
    return float((gefahren["delay_in_min"] <= PUENKTLICH_BIS_MIN).mean() * 100)


def ausfallquote(df: pd.DataFrame) -> float:
    """Anteil ausgefallener Halte in Prozent (0–100)."""
    if df.empty:
        return float("nan")
    return float(df["ausgefallen"].mean() * 100)


def nach_gruppe(df: pd.DataFrame, spalte: str, min_halte: int = 1) -> pd.DataFrame:
    """Kennzahlen je Gruppe (z. B. je Stunde, Kategorie oder Bahnhof).

    min_halte: Gruppen mit weniger Halten werden weggelassen, damit kleine
    Bahnhöfe mit drei Halten nicht die Rangliste verzerren.
    """
    gefahren = _gefahren(df)
    stats = gefahren.groupby(spalte).agg(
        halte=("delay_in_min", "size"),
        puenktlich_prozent=("delay_in_min", lambda s: (s <= PUENKTLICH_BIS_MIN).mean() * 100),
        mittlere_verspaetung_min=("delay_in_min", "mean"),
    )
    ausfaelle = df.groupby(spalte)["ausgefallen"].mean().mul(100).rename("ausfall_prozent")
    stats = stats.join(ausfaelle)
    return stats[stats["halte"] >= min_halte].round(1)


def nach_stunde(df: pd.DataFrame) -> pd.DataFrame:
    return nach_gruppe(df, "stunde")


def nach_kategorie(df: pd.DataFrame) -> pd.DataFrame:
    return nach_gruppe(df, "kategorie")


def bahnhof_rangliste(df: pd.DataFrame, min_halte: int = 10000, anzahl: int = 10) -> pd.DataFrame:
    """Die unpünktlichsten Bahnhöfe mit mindestens min_halte Halten."""
    stats = nach_gruppe(df, "station_name", min_halte=min_halte)
    return stats.sort_values("puenktlich_prozent").head(anzahl)


WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def nach_wochentag(df: pd.DataFrame) -> pd.DataFrame:
    """Kennzahlen je Wochentag (Montag bis Sonntag)."""
    stats = nach_gruppe(df, "wochentag")
    stats.index = [WOCHENTAGE[i] for i in stats.index]
    stats.index.name = "wochentag"
    return stats
