# Für den Erzähler

Der Erzähler ist ein Django-Staff-Benutzer. Melde dich über **Erzähler-Login** in der Kopfzeile an (`/gm/login/`); danach öffnet **Erzähler** in der Kopfzeile die Erzählerseite (`/gm/`). Der Erzähler kann jeden Charakter ohne dessen Passwort öffnen.

## Einstellungen
- **Zufällige Merkmale:** ob Spieler ihr zufälliges Volksmerkmal wählen dürfen, statt zu würfeln, und ob sie neu würfeln dürfen.
- **Hintergrundgeschichten** pro Charakter und die **höchste Startstufe** für neue Charaktere.
- **Admin-Modus für Spieler:** ob Spieler, die einen Charakter entsperrt haben, dort den Admin-Modus nutzen dürfen. Der Erzähler darf es immer.
- **Erweiterungen** und **deaktivierte Völker:** Eine eingeschaltete Erweiterung wird für neue Entscheidungen angeboten (Assistent, Stufenaufstieg, Planer, Admin-Modus, Zufallscharaktere, Katalog, Wiki-Suche); ein deaktiviertes Volk wird neuen Charakteren nicht angeboten. Charaktere behalten alles, was sie schon haben; Ausschalten entfernt nie etwas von einem Bogen.
- **Gruppen-Passphrase:** Ist sie gesetzt, muss jeder Browser sie einmal eingeben, bevor er etwas sieht. Eine neue Passphrase lässt jeden Browser sie erneut eingeben; *Gruppen-Passphrase entfernen* öffnet die Seite für alle, die sie finden. Der Erzähler braucht sie nie.
- **E-Mail für neue Rückmeldungen:** Jede neue Rückmeldung wird an diese Adresse geschickt, aber nur, wenn der Server Mail-Einstellungen hat (`EMAIL_HOST`); die Seite sagt dir, wenn sie fehlen.

## Charaktere
- **Passwort zurücksetzen:** Gib neben dem Charakter ein neues Passwort ein (mindestens 8 Zeichen) und klicke auf *Setzen*.
- **Löschen** verschiebt einen Charakter in den Papierkorb.
- Der **Admin-Modus** auf einem Bogen erlaubt Änderungen an Werten, die die Regeln sonst festlegen (manuelle Sonstiges-Werte, die Entscheidungen im Erstellungsassistenten, Stufenaufstiege ohne EP). Dort hinzugefügte Spezialisierungen und Augments sind mit **Erz.** markiert und werden von Regelprüfungen nie entfernt. Jedes Speichern zeigt, was sich geändert hat.

## Katalog
- Nur der Erzähler kann **Gegenstände aus dem Spielerhandbuch** ändern. Ein geänderter ist als *geändert* markiert; **Auf Buchwerte zurücksetzen** stellt die Werte aus dem Buch wieder her. Löschen blendet einen Buch-Gegenstand aus: Wähle im Quellen-Filter *Ausgeblendet*, um ihn zu finden und wiederherzustellen. Ein Neustart des Servers überschreibt diese Änderungen nie und holt ausgeblendete Gegenstände nicht zurück.
- **CSV exportieren** lädt den (gefilterten) Katalog im Importformat herunter; **Massenimport** bringt eine bearbeitete Datei mit Vorschau zurück (siehe *Inventar und Gegenstände*). Gelöschte eigene Gegenstände landen im Papierkorb.

## Feedback
Spieler schicken Fehler, Wünsche und Feedback über die Sprechblase unten rechts. Der Abschnitt *Feedback* listet sie mit Seite, Charakter und Browserdaten. Setze einen Status (neu, in Arbeit, erledigt, wird nicht behoben), halte eine **Notiz des Erzählers** fest oder lösche eine Nachricht.

## Spieltisch
- Die **Gruppenübersicht** zeigt jeden aktiven Charakter: TP, Wunden, verbleibende AP im Kampf, Haltung, aktive Effekte, letzte Änderung, ob ein Passwort gesetzt ist, und fehlgeschlagene Entsperrversuche. Sie aktualisiert sich alle 10 Sekunden.
- **Gruppenaktionen** geben jedem aktiven Charakter EP, allen eine Verschnaufpause oder beenden für alle den Kampfmodus. Die Änderung an jedem Charakter wird wie eine Spielaktion protokolliert.
- Das **Aktionsprotokoll** listet, wer was geändert hat (Erzähler, Spieler-Sitzung, anonym, System), mit Filtern für Charakter, Art der Aktion, wer und Zeitraum. Einträge bleiben 180 Tage.
- **Rückgängig:** Im *Verlauf* eines Charakters (Reiter Geschichte) nimmt **Letzte Aktion rückgängig** die letzte Spielaktion zurück und **Letzten Stufenaufstieg zurücknehmen** den letzten Stufenaufstieg (der TP-Zuwachs und der Eintrag im Stufenverlauf verschwinden mit). Abgelehnt wird es, wenn sich dieselben Werte seitdem wieder geändert haben, und bei Änderungen an Gegenständen, Begleitern, eigenen Modifikatoren und Texten; die änderst du von Hand.

## Export, Kopien und Sicherungen
- **Exportieren** lädt einen Charakter als JSON-Datei herunter (ohne Passwort). **Charakter importieren** macht aus so einer Datei einen *neuen* Charakter mit neuem Passwort; bestehende Charaktere werden nie überschrieben. Die Datei wird streng geprüft; passt sie nicht, wird sie mit Begründung abgelehnt.
- **Kopieren** legt eine Kopie eines Charakters unter neuem Namen und Passwort an.
- **Sicherungen:** Vor jedem Stufenaufstieg wird der Charakter gesichert; die letzten 10 pro Charakter lassen sich herunterladen und wie ein Export importieren.

## Papierkorb
Gelöschte Charaktere, Wiki-Seiten und eigene Katalog-Gegenstände landen im **Papierkorb** auf der Erzählerseite. **Wiederherstellen** holt sie zurück, **Endgültig löschen** entfernt sie sofort. Nach 30 Tagen im Papierkorb löscht sie die nächste Bereinigung endgültig (bei jedem Serverstart und, falls eingerichtet, nachts). *Verwaiste Entwürfe in den Papierkorb verschieben* sammelt Charaktere in Erstellung ein, die seit 30 Tagen niemand geändert hat.

## Backups
Der Server macht bei jedem Start (also vor jedem Update) ein Datenbank-Backup und, sobald der nächtliche Auftrag eingerichtet ist, jede Nacht; der Abschnitt *Server* der Erzählerseite zeigt die Zeit des neuesten. Den nächtlichen Auftrag einrichten und ein Backup zurückspielen sind Schritte auf dem Server: siehe README.

## Sonstiges
- Die Regel-Schalter ändern nie bestehende Charaktere; sie entscheiden nur, was als Nächstes angeboten wird.
- Tagebuch-Fassungen stellst du im Django-Admin wieder her (*Journal revisions*), Wiki-Fassungen im *Verlauf* der Seite.
