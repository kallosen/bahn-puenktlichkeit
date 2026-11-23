import math

import pandas as pd
import pytest

from bahnanalyse import kennzahlen as k
from bahnanalyse.laden import aufbereiten, kategorie


def halt(station="Berlin Hbf", zug="ICE", verspaetung=0, zeit="2026-10-05 08:15",
         ankunft_ausfall=False, abfahrt_ausfall=False):
    return {
        "station_name": station,
        "train_type": zug,
        "delay_in_min": verspaetung,
        "time": zeit,
        "arrival_is_canceled": ankunft_ausfall,
        "departure_is_canceled": abfahrt_ausfall,
    }


def daten(*halte):
    return aufbereiten(pd.DataFrame(halte))


def test_kategorie():
    assert kategorie("ICE") == "Fernverkehr"
    assert kategorie("RE") == "Regionalverkehr"
    assert kategorie("S") == "S-Bahn"
    assert kategorie(None) == "Unbekannt"


def test_fuenf_minuten_ist_puenktlich_sechs_nicht():
    df = daten(halt(verspaetung=5), halt(verspaetung=6))
    assert k.puenktlichkeitsquote(df) == 50.0


def test_ausfaelle_zaehlen_nicht_in_puenktlichkeit():
    df = daten(halt(verspaetung=0), halt(verspaetung=30, abfahrt_ausfall=True))
    assert k.puenktlichkeitsquote(df) == 100.0
    assert k.ausfallquote(df) == 50.0


def test_leere_daten():
    df = daten(halt())
    assert math.isnan(k.puenktlichkeitsquote(df.iloc[0:0]))


def test_nach_stunde():
    df = daten(
        halt(verspaetung=0, zeit="2026-10-05 08:00"),
        halt(verspaetung=20, zeit="2026-10-05 08:30"),
        halt(verspaetung=0, zeit="2026-10-05 17:10"),
    )
    stats = k.nach_stunde(df)
    assert stats.loc[8, "puenktlich_prozent"] == 50.0
    assert stats.loc[8, "mittlere_verspaetung_min"] == 10.0
    assert stats.loc[17, "puenktlich_prozent"] == 100.0


def test_rangliste_ignoriert_kleine_bahnhoefe():
    halte = [halt(station="Groß", verspaetung=10) for _ in range(5)]
    halte.append(halt(station="Klein", verspaetung=60))
    stats = k.bahnhof_rangliste(daten(*halte), min_halte=3)
    assert list(stats.index) == ["Groß"]


def test_nach_wochentag():
    df = daten(
        halt(verspaetung=0, zeit="2026-10-05 08:00"),   # Montag
        halt(verspaetung=10, zeit="2026-10-05 09:00"),  # Montag
        halt(verspaetung=0, zeit="2026-10-11 08:00"),   # Sonntag
    )
    stats = k.nach_wochentag(df)
    assert stats.loc["Mo", "puenktlich_prozent"] == 50.0
    assert stats.loc["So", "puenktlich_prozent"] == 100.0
