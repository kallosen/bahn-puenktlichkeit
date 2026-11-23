"""Erzeugt Diagramme und eine Ergebnistabelle aus den heruntergeladenen Daten.

Beispiel:
    python scripts/report.py              # alle Bahnhöfe
    python scripts/report.py --bahnhof Berlin
"""

import argparse
import sys
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "src"))

from bahnanalyse import kennzahlen as k  # noqa: E402
from bahnanalyse.laden import lade_halte  # noqa: E402

DOCS = WURZEL / "docs"


def diagramm_stunde(df, pfad: Path) -> None:
    stats = k.nach_stunde(df)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(stats.index, stats["puenktlich_prozent"], color="#3b6ea5")
    ax.set_xlabel("Uhrzeit (Stunde)")
    ax.set_ylabel("Pünktlich (%)")
    ax.set_title("Pünktlichkeit nach Uhrzeit")
    ax.set_xticks(range(0, 24, 2))
    ax.set_ylim(0, 100)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(pfad, dpi=150)
    plt.close(fig)


def diagramm_kategorie(df, pfad: Path) -> None:
    stats = k.nach_kategorie(df).drop(index="Unbekannt", errors="ignore")
    stats = stats.sort_values("puenktlich_prozent")
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.barh(stats.index, stats["puenktlich_prozent"], color="#3b6ea5")
    for y, wert in enumerate(stats["puenktlich_prozent"]):
        ax.text(wert + 1, y, f"{wert:.1f} %", va="center")
    ax.set_xlim(0, 105)
    ax.set_xlabel("Pünktlich (%)")
    ax.set_title("Pünktlichkeit nach Zugkategorie")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(pfad, dpi=150)
    plt.close(fig)


def main() -> None:
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 10)
    parser = argparse.ArgumentParser()
    parser.add_argument("--bahnhof", help="Nur Bahnhöfe, deren Name diesen Text enthält")
    parser.add_argument("--min-halte", type=int, default=10000)
    args = parser.parse_args()

    dateien = sorted((WURZEL / "data").glob("data-*.parquet"))
    df = lade_halte(dateien, args.bahnhof)
    DOCS.mkdir(exist_ok=True)

    print(f"Halte gesamt:        {len(df):,}")
    print(f"Pünktlichkeitsquote: {k.puenktlichkeitsquote(df):.1f} %")
    print(f"Ausfallquote:        {k.ausfallquote(df):.1f} %\n")
    print(k.nach_kategorie(df), "\n")
    print(k.nach_wochentag(df), "\n")

    rangliste = k.bahnhof_rangliste(df, min_halte=args.min_halte)
    print("Unpünktlichste Bahnhöfe:")
    print(rangliste)
    rangliste.to_csv(DOCS / "bahnhof_rangliste.csv")

    diagramm_stunde(df, DOCS / "puenktlichkeit_stunde.png")
    diagramm_kategorie(df, DOCS / "puenktlichkeit_kategorie.png")
    print(f"\nDiagramme gespeichert in {DOCS}")


if __name__ == "__main__":
    main()
