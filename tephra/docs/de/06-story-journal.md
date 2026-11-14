# Geschichtstagebuch

Der Reiter **Geschichte** ist dein Kampagnentagebuch: was passiert ist, warum du was tust, wen du getroffen hast.

- **+ Neuer Block** beginnt einen Block mit Überschrift (z. B. ein Tag oder eine Stadt). `# Überschrift` beginnt einen Block, `## Unterüberschrift` einen kleineren.
- Innerhalb eines Blocks: Leerzeilen trennen Absätze, `- ` beginnt eine Liste, `**fett**`, `*kursiv*`.
- Blöcke lassen sich einklappen, und das Suchfeld filtert sie.
- Das einzeilige Feld oben hängt eine Zeile ans Ende des Tagebuchs, ohne den Editor zu öffnen.
- Jede Änderung hebt den vorherigen Text auf; der Erzähler kann ihn wiederherstellen (Django-Admin → Journal revisions).

## Verlauf

Unter dem Tagebuch zeigt **Verlauf** die letzten 30 Änderungen am Charakter: wann, wer (Erzähler, eine Spieler-Sitzung, jemand ohne Freischaltung) und was sich geändert hat (alt → neu). Er ist nur lesbar. Der Erzähler kann dort die letzte Spielaktion rückgängig machen oder den letzten Stufenaufstieg zurücknehmen, solange sich dieselben Werte seitdem nicht geändert haben; Änderungen an Gegenständen, Begleitern und Texten werden nie automatisch zurückgenommen.
