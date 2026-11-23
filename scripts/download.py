"""Lädt Monatsdateien des Datensatzes piebro/deutsche-bahn-data von Hugging Face.

Beispiel:
    python scripts/download.py 2026-08 2026-09 2026-10
"""

import sys
import urllib.request
from pathlib import Path

BASIS_URL = (
    "https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/"
    "monthly_processed_data/data-{monat}.parquet"
)
ZIEL = Path(__file__).resolve().parent.parent / "data"


def lade_monat(monat: str) -> Path:
    ZIEL.mkdir(exist_ok=True)
    datei = ZIEL / f"data-{monat}.parquet"
    if datei.exists():
        print(f"{datei.name} ist schon da, überspringe.")
        return datei
    url = BASIS_URL.format(monat=monat)
    print(f"Lade {url} ...")
    urllib.request.urlretrieve(url, datei)
    print(f"Gespeichert: {datei} ({datei.stat().st_size / 1e6:.0f} MB)")
    return datei


if __name__ == "__main__":
    monate = sys.argv[1:]
    if not monate:
        print("Bitte Monate angeben, z. B.: python scripts/download.py 2026-10")
        sys.exit(1)
    for m in monate:
        lade_monat(m)
