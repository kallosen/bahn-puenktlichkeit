# Erklärung zum Projekt (für Vorstellungsgespräche)

## In einem Satz
Ich habe die offenen Verspätungsdaten der Deutschen Bahn mit Python und SQL ausgewertet:
wie pünktlich die Züge sind, wann und wo es am schlimmsten ist und wie viele ausfallen.

## Wie die Daten aussehen
- Eine Zeile = ein Halt eines Zuges an einem Bahnhof (z. B. ICE 123 in Berlin Hbf um 8:15).
- Wichtige Spalten: `station_name`, `train_type` (ICE, RE, S …), `delay_in_min`, `time`,
  `arrival_is_canceled` / `departure_is_canceled`.
- Format: Parquet, eine Datei pro Monat, mehrere Millionen Zeilen.

## Ablauf
1. `download.py` lädt die Monatsdateien herunter.
2. `laden.py` liest sie mit DuckDB und filtert per SQL (z. B. nur Berliner Bahnhöfe).
   Danach kommen neue Spalten dazu: Kategorie (Fern/Regional/S-Bahn), ausgefallen, Stunde, Wochentag.
3. `kennzahlen.py` rechnet die Quoten aus, alles mit pandas `groupby`.
4. `report.py` gibt die Tabellen aus und speichert die Diagramme.

## Fragen, die kommen können

**Warum DuckDB und nicht nur pandas?**
pandas lädt alles in den Arbeitsspeicher. DuckDB liest Parquet direkt und filtert vorher per SQL,
sodass nur die nötigen Spalten und Zeilen in pandas landen. Bei Millionen Zeilen ist das schneller
und braucht weniger Speicher.

**Warum Parquet?**
Spaltenbasiert und komprimiert. Man kann einzelne Spalten lesen, ohne die ganze Datei zu laden.

**Was heißt „pünktlich“?**
Wie bei der DB: unter 6 Minuten Verspätung. Im Code `delay_in_min <= 5`.

**Warum zählen Ausfälle nicht zur Pünktlichkeit?**
So macht es die DB auch. Ein ausgefallener Zug hat keine Verspätung. Deshalb weise ich die
Ausfallquote getrennt aus. Kritikpunkt: Dadurch wirkt die Pünktlichkeit besser, als sie für
Fahrgäste ist. Das steht auch im README.

**Warum mindestens 10.000 Halte im Monat in der Bahnhofs-Rangliste?**
Ein kleiner Bahnhof mit drei Halten, davon einer verspätet, hätte sonst 67 % Pünktlichkeit
und stünde ganz oben. Mit 1.000 Halten standen im ersten Lauf fast nur kleine Regionalbahnhöfe
an einer einzigen Strecke oben. Mit 10.000 (gut 300 Halte am Tag) vergleicht man echte Knotenpunkte.

**Wie hast du getestet?**
Mit kleinen, selbst gebauten Beispieldaten, bei denen ich das Ergebnis vorher kenne,
z. B. 5 Minuten Verspätung = pünktlich, 6 Minuten = nicht pünktlich. Die Tests laufen bei jedem
Push automatisch über GitHub Actions.

**Was würdest du als Nächstes machen?**
- Verspätungen entlang einer Zugfahrt verfolgen (wo entsteht sie, wo wird sie aufgeholt?)
  über `train_line_ride_id`.
- Ein interaktives Dashboard (z. B. Streamlit).
- Vergleich mit den offiziellen Pünktlichkeitszahlen der DB.

**Hast du das allein gebaut?**
Ehrlich antworten: mit Unterstützung von KI (Claude). Wichtig ist, dass du jede Datei erklären kannst.
