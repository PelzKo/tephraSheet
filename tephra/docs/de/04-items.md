# Inventar und Gegenstände

- **Etwas gefunden?** Gib im Inventar-Reiter einen Namen (Decke, Flasche, Haifischzahn …), eine Anzahl und Notizen ein: Es wird als *allgemeiner Gegenstand* hinzugefügt.
- **Aus dem Katalog** zeigt alle Gegenstände; *bezahlen* zieht den Preis von deinem Bargeld ab (nur wenn es reicht). Filtere nach Quelle (*Buch*, *geänderte* Buch-Gegenstände, *eigene*) und Erweiterung; lange Listen haben Seiten.
- **Kopieren** öffnet den Objekt-Ersteller mit einer Kopie eines Katalog-Gegenstands, gespeichert als eigener Gegenstand.
- **CSV exportieren** lädt den (gefilterten) Katalog im Importformat herunter: In einer Tabellenkalkulation bearbeiten und mit **Massenimport** zurückholen. Die Import-Vorschau zeigt je Zeile, ob sie neu ist, einen vorhandenen Gegenstand aktualisiert, unverändert ist oder übersprungen wird (Gegenstände aus dem Spielerhandbuch kann nur die Spielleitung ändern).
- Gegenstände aus dem Spielerhandbuch kann nur die Spielleitung ändern. Geänderte sind als *geändert* markiert und haben **Auf Buchwerte zurücksetzen**; Löschen blendet sie aus (Filter *Ausgeblendet* zum Wiederherstellen). Ein Neustart des Servers überschreibt diese Änderungen nie.
- **Gegenstand erstellen** öffnet den Objekt-Ersteller: Wähle Art und Größe, die Regeln füllen Schadensklasse, AP, Reichweite und Rüstungswerte aus („auto“). Waffen können einen **Genauigkeitsbonus** bekommen, Nahkampfwaffen und Bögen einen **Schlagkraftbonus**. Rüstungsabzüge werden als Zahl eingegeben und abgezogen.
- Jeder Gegenstand, den du erstellst, wird auch **im gemeinsamen Katalog gespeichert**, damit alle ihn nutzen können.
- Wähle, wo ein Gegenstand ist (linke/rechte Hand, Rüstung, Parierwaffe, getragen, mitgeführt, verstaut). Nur getragene und gehaltene Gegenstände wirken. Ein zweihändiger Gegenstand kommt in die linke Hand und blockiert die rechte.
- **Aus dem Katalog:** Durchsuche den Katalog direkt im Inventar-Reiter und füge einen Gegenstand hinzu, ohne den Bogen zu verlassen.
- **Geben** übergibt einen Gegenstand (oder einen Teil eines Stapels) an einen anderen Charakter, den du entsperrt hast; beide Tagebücher vermerken es.
- Auf Seite 2 öffnet ein Tippen auf eine Ausrüstungszeile mit Anzahl (Munition, Stapel) − / +.

## Format für den Massenimport
Der **Massenimport** (Katalog) nimmt eine CSV-Datei oder eine eingefügte Tabelle: aus einer Tabellenkalkulation, CSV mit `,` oder `;` oder eine Markdown-Tabelle. Die erste Zeile benennt die Spalten; nötig ist nur `name`. *CSV-Vorlage herunterladen* liefert eine Beispieldatei.

- Nützliche Spalten: `kind` (melee, firearm, bow, crossbow, armor, deflection, ammo, gear, animal, vehicle …), `size`, `variants` (flexible / polearm / throwing / impromptu / double-barreled), `material`, `price` (`5 pr`, `3 d`), `augments` (`Accurate II; Damaging I`), `description`, `quantity`. Die Spaltennamen und Werte sind englisch; gängige andere Namen werden verstanden (z. B. *type* für kind, *cost* für price, *qty* für quantity).
- Leere Zahlenspalten (Schadensklasse, AP, Reichweite, Schutz …) nehmen die Größentabellen der Regeln.
- Die Vorschau zeigt jede Zeile mit ihren Problemen; importiert werden nur Zeilen ohne Probleme. Aus dem Inventar eines Charakters geöffnet, wählst du, ob sie in dieses Inventar oder in den gemeinsamen Katalog kommen.
- Die Datei von **CSV exportieren** hat dasselbe Format (mit dem genauen Preis in Dukes und ein paar Spalten mehr), du kannst sie also bearbeiten und wieder importieren.
