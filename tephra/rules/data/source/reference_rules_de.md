## 1. Kernregeln, die Charakterwerte beeinflussen (Kap. 1, S. 8–23)

### 1.1 Würfel
- Ein **d12** für alles. Wurf = d12 + passender Modifikator (Attribut, Fertigkeit oder Kampfwert).
- **Regel Nr. 1 – „1 ist 1":** Eine natürliche 1 zählt als 1, und es werden keine Boni addiert. *Ausnahme:* Mali gelten trotzdem (blind −4 bei einer natürlichen 1 → −3).
- **Regel Nr. 2 – Reine 12er werden nachgewürfelt:** Natürliche 12 → erneut würfeln und addieren; bei weiteren 12ern wiederholen. Eine 1 nach einer 12 = 13 (Regel Nr. 1 gilt dann nicht mehr). Gilt nicht für zufällige Trefferzonenwürfe bei gezielten Angriffen.

### 1.2 Vier Erfolgsstufen (S. 9)

| Stufe | Ergebnis | Bezeichnung |
|---|---|---|
| S1 | 1–9 | Gerade so bestanden |
| S2 | 10–19 | Solider Erfolg |
| S3 | 20–29 | Phänomenal |
| S4 | 30+ | Übermenschlich |

Formel: `tier = result >= 30 ? 4 : result >= 20 ? 3 : result >= 10 ? 2 : 1` (Ergebnisse < 1 durch Mali: Das Buch definiert keine Stufe 0; behandle sie nach Ermessen des Erzählers als S1/Fehlschlag – **in der Quelle unklar**).

### 1.3 Attribute & Fertigkeiten (S. 9–10, 18)
- Attribute beginnen bei 0. `Attribut = Σ(Punkte in seinen Fertigkeiten) + Misc` (der Bogen hat pro Attribut einen „Misc"-Kreis).
- Attribute werden für allgemeine Aktionen und **Widerstände** verwendet.
- **Gestufter Widerstand:** Jede Stufe über S1 beim Widerstandswurf senkt den eingehenden Effekt um 1 Stufe (S1 unverändert, S2 −1, S3 −2, S4 −3).
- **Explosionen ausweichen:** 1 AP, reflexiver Geschickwurf; du musst mindestens die Stufe/Marque der Explosion erreichen und dich höchstens um dein Tempo bewegen, um den Bereich zu verlassen.

| Attribut | Fertigkeiten |
|---|---|
| **Kraft** | Raufen, Raserei, Überwältigen, Zähigkeit |
| **List** | Spionage, Fachwissen, Showtalent, Taktik |
| **Geschick** | Pilot, Akrobatik, Schießkunst, Fechtkunst |
| **Geist** | Glaube, Anmut, Glück, Schamanismus |
| **Wissenschaften** | Alchemie, Waffenschmied, Automaten, Bio-Flux, Ingenieur, Tüftelei (+ Regelkapitel „Herstellung") |

### 1.4 Aktionspunkte (AP), Züge, Initiative (S. 10–11)
- AP pro Zug nach Stufe: **St. 1–3: 3 · St. 4–7: 4 · St. 8–11: 5 · St. 12: 6**.
- AP werden am Ende deines Zuges aufgefrischt; ungenutzte AP verfallen. Reflexive AP werden vom Vorrat des *nächsten* Zuges abgezogen.
- **Initiativewurf** = d12 + Ini-Bonus. Der Erzähler kann einen Situationsbonus (normalerweise **+6**) für Bereitschaft gewähren.
- Wer vor dem Kampf bereit ist, kann bereits in Haltung sein / die Waffen gezogen haben.

### 1.5 Trefferpunkte, Wunden, Heilung (S. 10–11)
- **TP** = ausschließlich die Summe der TP-Boni der Spezialisierungen (+ Volks-/Geschichts-/Gegenstandsmodifikatoren). Keine Basis-TP.
- **Wunden** beginnen bei **12** (sofern das Volk nichts anderes angibt) + Wnd-Boni der Spezialisierungen.
- Schaden senkt zuerst die TP; bei 0 TP geht der Schaden auf die Wunden. Jedes Mal, wenn du Wundenschaden nimmst → Trefferzone auswürfeln → **Wundeffekt**. Bei 0 Wunden und erneutem Treffer → jedes Mal **Tödlicher Effekt**.
- Unvorbereitet/außerhalb des Kampfes: keine TP, der Schaden geht direkt auf die Wunden.
- **Verschnaufpause** (15–30 Min. Rast): alle TP werden wiederhergestellt. **Wunden** heilen 1 pro Tag.
- **Erschöpft:** maximale TP halbiert (abgerundet).
- Bogenfelder: Trefferpunkte / Max. TP / Wunden / Max. Wunden.

### 1.6 Angriffsauflösung (S. 12)
1. **Genauigkeit gegen Ausweichen:** Angreifer d12+Gen; Verteidiger d12+Aus. Treffer, wenn Gen ≥ Aus.
2. **Schlagkraft gegen Verteidigung:** Angreifer d12+Sch → Stufe → `Schaden = Schadensklasse × Stufe`. Verteidiger d12+Ver → Stufe → absorbiert `Schutzklasse × Stufe` (Schutzklasse von der Rüstung).
- Nettoschaden = Schaden − Schutz (implizit; mindestens 0).

### 1.7 Standardaktionen & Kosten (S. 12–15)

| Aktion | AP | Anmerkungen |
|---|---|---|
| Nahkampfangriff (Waffe) | 2 | Die meisten Waffen |
| Waffenloser Angriff | 1 | SK 2 |
| Fernkampfangriff | variiert | siehe Waffe |
| Spezialisierungsangriff | Angriff + X | Mehrere verschiedene Spezialisierungen können sich bei einem Angriff stapeln; dieselbe kann nicht zweimal hinzugefügt werden |
| Gezielter Angriff | Angriff +1 | Zone wählen (d12-Tabelle), widerstehbar: Das Widerstandsattribut des Ziels muss den Schlagkraftwurf des Angreifers **übertreffen** (Genauigkeitswurf bei Schusswaffen/Armbrüsten) |
| Nicht-tödlicher Angriff | wie Angriff | keine Wundeffekte; Ziel bewusstlos bei 0 Wunden |
| Parieren | 1 (Unterbrechung) | benötigt Schild/Parierwaffe; +4 Ausweichen (Grundregel; siehe Parierwaffen) |
| Gegenstand ziehen/tauschen | 1 | |
| Haltung einnehmen | 1 | eine Haltung gleichzeitig; geht verloren, wenn du zurückgestoßen wirst oder liegst; kann zu Kampfbeginn kostenlos eingenommen werden. Jeder kennt den **Stand** (für überschwere Waffen). |
| Greifen | wie waffenlos (1) oder Peitsche (2) | Zone wählen, Gen gegen Aus, kein Schaden; Ziel befreit sich mit 1 AP Kraft/Geschick gegen Kraft/Geschick; gegriffene Hand kann keinen Gegenstand benutzen |
| Werfen (nach Greifen) | 2 | Kraft; S1 5 ft, S2 10 ft, S3 10 ft + liegend, S4 15 ft + liegend; Kraftstufen des Ziels senken; kleine Kreaturen +5 ft |
| Bewegen | 1 | 25 ft (volksabhängig) |
| Schusswaffe laden | variiert | siehe Waffe |
| Aufstehen | 1 | Knien kostenlos |
| Zerschmettern | wie Angriff | gegen geführten Gegenstand; Nahkampfwaffe SK −1 pro Stufe; Schusswaffe/Armbrust/Bogen SK −2 pro Stufe; Widerstand Geschick senkt Stufen; bei Verschnaufpause reparierbar |
| Gnadenstoß | 3 | hilfloses Ziel; reine 12 beim Schlag, natürliche 1 des Ziels bei der Verteidigung, direkt auf Wunden |
| Fenster einschlagen / Tür öffnen / Hebel ziehen | 1 | |

**Reflexive Angriffe:** Deckung verlassen (nur Fernkampf) sowie einen Gegenstand in Nahkampfreichweite benutzen/verbrauchen/ziehen (nur Nahkampf).

### 1.8 Tabelle der gezielten Angriffe (d12, S. 16–17)

| d12 | Zone | Widerstand | Effekt des gezielten Angriffs | Wundeffekt | Tödlicher Effekt |
|---|---|---|---|---|---|
| 1 | Kopf | Kraft | Desorientiert (−1 AP/Zug) bis zum Ende deines nächsten Zuges | Desorientiert, 1 Zug pro 3 Schaden, kann sich nicht neu orientieren | Enthauptet – sofortiger Tod |
| 2 | Augen | Geschick | −2 Gen & Aus bis zum Ende des nächsten Zuges | Geblendet bis zur Verschnaufpause: −4 Gen/Aus | Dauerhaft blind: −4 Gen/Aus, **−1 max. Wunden** |
| 3 | Ohren | List | −2 Aus bis zum Ende des nächsten Zuges | Taub bis zur Verschnaufpause: −2 Aus & Geräuschwürfe | Dauerhaft taub: −2 Aus, **−1 max. Wunden** |
| 4 | Hals | Kraft | Betäubt 1 AP | Blutend: 1 Wunde/Zug, 1 Zug pro 3 Schaden | Durchgeschnittene Kehle: Tod am Ende des nächsten Zuges |
| 5 | Torso | Kraft | 5 ft zurückgestoßen (Angreifer darf für 0 AP folgen) | Gebrochene Rippen: Jede Aktion erfordert Kraft S2, sonst verlierst du 1 AP; bis zur Verschnaufpause | Erschlagen |
| 6 | Leiste | Geist | Übelkeit: −2 auf alle Würfe, bis 3 AP ausgegeben wurden | Erbrechen: nur halbes Tempo für 3 Züge, −4 Aus | Ausgeweidet: 10 Schaden heilen vor Ende des nächsten Zuges, sonst Tod |
| 7–8 | Arm | Kraft | −2 auf Würfe mit diesem Arm bis zum Ende des nächsten Zuges | Verstauchter Arm: −6 auf Würfe mit ihm bis zur Verschnaufpause | Abgetrennter Arm: **−2 max. Wunden**, Aufgaben mit zwei Armen unmöglich/−6; Tod in 3 Zügen, außer 3 AP Verbinden |
| 9–10 | Hand | Geschick | Gehaltenen Gegenstand fallen lassen (1 AP zum Aufheben) | Geprellte Hand: kann bis zur Verschnaufpause nichts damit führen | Abgetrennte Hand: **−1 max. Wunden**; Tod in 6 Zügen, außer 3 AP Verbinden |
| 11–12 | Bein | Geschick | Wahl des Angreifers: verlangsamt (+1 AP zum Bewegen) oder gestolpert (liegend) | Verstauchtes Bein: −10 Tempo (min. 5), liegend; bis zur Verschnaufpause | Abgetrenntes Bein: −20 Tempo (min. 5), Aufgaben mit zwei Beinen −6, **−1 max. Wunden**; Tod in 3 Zügen, außer 3 AP Verbinden |

Effekte gezielter Angriffe stapeln sich nicht (sie werden nur erneuert), außer Torso-Rückstoß und Halsbetäubung. Gezielte Angriffe gegen ein Ziel in Wunden/Tödlichen Effekten treffen diese Zone automatisch.

### 1.9 Deckung (S. 20–21)

| Grad | Beispiele | Deckt bis zu | Ausweichbonus | Verstecken-Modifikator |
|---|---|---|---|---|
| Weiche Deckung | Sträucher, Segeltuch | – | Angreifer −4 Gen (−2 bei Silhouette); du erhältst denselben Malus auf Ausweichen | – |
| Dürftig (S1) | Pfosten, Beistelltisch, Person | 3 Zonen | +2 | – |
| Leicht (S2) | Busch, Sofa, Baum | 6 Zonen | +4 | – |
| Mittel (S3) | großer Baum, Fass, Graben, Ecke | 9 Zonen | +6 | −4 |
| Schwer (S4) | volle Wand, hinter Möbeln geduckt | 11 Zonen | +8 | ±0 |
| Vollständig | nichts sichtbar | alle | kann nicht anvisiert werden | +4 |

- **Volle Deckung nehmen:** 1 AP (oder am Ende einer Bewegung) hinter mittlerer/schwerer Deckung; Spähen kostet 0 AP, zählt aber als Verlassen der Deckung.
- **Blindes Feuern** aus voller Deckung: nur Hand/Hände sichtbar; −4 Gen (−8, wenn die Position unbekannt ist).
- Bemerken: Beide würfeln List (der Versteckte erhält den Deckungsmodifikator). Das Absuchen einer bestimmten Stelle findet automatisch.
- Niederschlag/Wind kann Deckung hinzufügen/aufwerten (Erzähler).

### 1.10 Statuseffekte (S. 22–23)

| Status | Mechanische Wirkung |
|---|---|
| Blutend (Status) | TP-Schaden (dann Wunden) bei jeder AP-Auffrischung, nicht absorbierbar, stapelt sich; jeder ausgegebene AP (Opfer/Angrenzender) negiert 5 Blutung |
| Geblendet | −4 Gen & Aus gegen das Ziel; schlechte Sicht/Nebel/wenig Licht −2 |
| Brennend S1/S2/S3/S4 | 2/4/8/16 nicht absorbierbarer Schaden pro Zug; AP zum Löschen 2/4/8/16; Zerstörung von Gegenständen eskaliert (S1 angesengt, S2 Holz/Organisches/Stoff zerstört, S3 Leder/Stoff/Holz, S4 selbst Metall unbrauchbar) |
| Verbrannt S1/S2/S3/S4 | −1/−3/−5/−7 auf alle Verteidigungswürfe (Zone brennt: Erzähler wendet es auf dieses Körperteil an) |
| Taub | −2 Aus; −2 auf geräuschbasierte Würfe |
| Desorientiert | −1 AP pro Zug; gib 3 AP aus, um dich neu zu orientieren |
| Ertrinkend | Kraftwurf jeden Zug, Zielstufe beginnt bei S2 und steigt; Fehlschlag → bewusstlos; Tod 3 Züge später |
| Wütend | −2 auf alle Würfe außer Angriffen gegen die Wutquelle; +2 Gen & Sch gegen die Quelle; 2 AP zum Beruhigen |
| Erschöpft | maximale TP halbiert (abgerundet) |
| Furcht S1 Verängstigt | −2 auf alle Widerstandswürfe (−4 gegen die Quelle) |
| Furcht S2 Erschrocken | −2 auf alle Würfe (−4 gegen die Quelle) |
| Furcht S3 Panisch | −2 auf alle Würfe (−4 gegen die Quelle); ≥1 AP/Zug für die Flucht; kann sich nicht nähern |
| Furcht S4 Blanke Angst | −4 auf alle Würfe (−6 gegen die Quelle); kann nur versuchen, sie zu überwinden (1 AP pro erneutem Wurf) |
| (Furcht allgemein) | 1 reflexiver AP, um die Überwindung zu versuchen; Geist ist immer als Widerstand nutzbar; endet bei der nächsten Pause |
| Übelkeit | −2 auf alle Würfe, bis 3 AP ausgegeben wurden |
| Gelähmt | hilflos; Schaden direkt auf Wunden; keine Aktionen |
| Liegend | −1 Gen/Aus/Sch/Ver; Tempo 5 ft; Aufstehen = 1 AP (zieht Reflexe); kann nicht aufstehen, solange gegriffen |
| Betäubt (X AP) | verliere X AP aus dem aktuellen Vorrat; weicht weiterhin aus/widersteht |

### 1.11 Schlachtfeldmodifikatoren (S. 23)
- **Fallen:** 1 Wunde pro 20 ft; jede Stufe über S1 beim Geschickwurf ignoriert 2 Wunden; würfle pro 2 erlittenen Wunden einen Wundeffekt.
- **Geländemalus aufs Tempo:** Gering −5 (schaukelndes Boot, lichter Wald) · Unsicher −10 (Wald, Felsen, Schnee) · Schwierig −15 (Sumpf, verschneites Gebirge) · Unmöglich −20 (dichter Dschungel, Geröll). Kriechen mit 5 ft ist immer möglich.

### 1.12 Soziale Hinweise (S. 19)
Listwurf, gestuft. Lügen erkennen (Widerstand List), Beschwichtigen/Einschüchtern (Widerstand Geist), Provozieren (Widerstand List). Nur erzählerisch.

### 1.13 Geschichten (S. 11)
Hintergrund-, Mitgliedschafts-, Persönlichkeits- und Veränderungsgeschichten; werden vom Erzähler gewährt/entfernt; geben Boni & Mali. Typischerweise 1 (oder 1–2) Hintergrund-/Persönlichkeitsgeschichten bei der Erschaffung. Details in §5.

---
## 2. Charaktererschaffung & Stufenaufstieg (Kap. 2, S. 24–27)

### 2.1 Schritte der Erschaffung
1. **Volk & Nationalität** – wende die Volksmerkmale an; würfle einen d12 auf der Zufallsmerkmal-Tabelle des Volkes (der Erzähler kann Wählen/Neuwürfeln erlauben). Wähle die Nationalität (Kap. 4) und Nationalitätsgeschichten.
2. **Fertigkeiten** – verteile **3** Punkte auf 1 Fertigkeit (primär), **2** Punkte auf 2 Fertigkeiten, **1** Punkt auf 3 Fertigkeiten. Kein Stapeln: 6 verschiedene Fertigkeiten auf Stufe 1.
3. **Attribute** – Attribut = Σ seiner Fertigkeiten.
4. **Spezialisierungen** – wähle **3**. Sie müssen aus Fertigkeiten mit ≥1 Punkt stammen (außer *allgemeine Spezialisierungen*). Notiere ihre Kampfwert-Boni.
5. **Augments** – jedes „Aug +X" aus Spezialisierungen = X Augment-Auswahlen aus einer Wissenschaftsfertigkeit, in der du Punkte hast; sie können unabhängig von der Slotgröße gelernt werden.
6. **Waffen & Rüstung** – wähle nach Größenklasse (Kap. 5). Genauigkeit/Schlagkraft und Ausweichen/Verteidigung stammen aus den Boni der Spezialisierungen.
7. **Ausrüstung** – alles aus der Liste der Startausrüstung (vernünftig); **10 Prinzen** Taschengeld.
8. **Abgeleitete Werte** – AP 3; Tempo = Volksbasis + Tempo-Boni der Spezialisierungen; Initiative = Ini-Boni; Wunden = 12 (sofern das Volk nichts anderes angibt) + Wnd; TP = Σ TP-Boni.
9. **Hintergrundgeschichten** – meist 1 (Richtlinien des Erzählers).
10. Name, Persönlichkeit usw.
### 2.2 Stufenaufstieg (S. 27)
- 12 Stufen; **12 EP pro Stufe** (Uhr). Bei jeder Stufe nach der 1.:
  - +2 Punkte in 1 beliebiger Fertigkeit, +1 Punkt in 2 *anderen* Fertigkeiten
  - Attribute neu berechnen
  - **1 neue Spezialisierung** lernen, ihre Boni anwenden
  - auf St. 4, 8, 12: +1 AP (3 → 4 → 5 → 6)
- Spezialisierungsslots auf dem Charakterbogen: St. 1 ×3, danach einer pro Stufe St. 2–12 → **14 Spezialisierungen auf St. 12**.
- **Fertigkeitspunkte insgesamt:** St. 1 = 3+2+2+1+1+1 = 10; jede Stufe +4 → St. 12 = 54.

**Umbau:**
- Spezialisierungen: Auf St. 4, 8, 12 darfst du eine Spezialisierung gegen eine andere **desselben Attributs** tauschen.
- Augments: Jedes Mal, wenn du ein neues Augment lernst, darfst du ein Augment gegen ein anderes **derselben Fertigkeit** tauschen.

### 2.3 Startprinzen nach Stufe

| Stufe | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Prinzen | 10 | 18 | 32 | 58 | 105 | 190 | 340 | 615 | 1.100 | 2.000 | 3.570 | 6.425 |

Charaktere höherer Stufe: auf St. 1 erschaffen, dann Stufe für Stufe aufsteigen.

### 2.4 Felder des Charakterbogens (S. 286–287) — Zielausgabe des Werkzeugs
- **Kopfzeile:** Spieler, Charaktername, Volk, Nationalität, Religion, Alter, Größe, Gewicht.
- **2 Waffenblöcke:** Beschreibung, Größe, Typ, Reichweite, AP zum Einsetzen, AP zum Laden, Genauigkeit, Schlagkraft, Schadensklasse (4 Kästchen → Stufen), Anmerkungen/Augments.
- **Kreise:** AP, Initiative, Tempo, Schwimmtempo, Klettertempo, Flugtempo; Stufentabelle (1–9 / 10–19 / 20–29 / 30+).
- **Rüstungsblock:** Beschreibung, Größe, Schutzklasse, Ausweichmalus, Tempomalus, Kletter-/Schwimmmalus, Anmerkungen/Augments; Kreise **Ausweichen**, **Verteidigung**.
- **Parierblock:** Gegenstand, Ausweichbonus (gegen Fernkampf ☐ / gegen Nahkampf ☐), „1 AP zum Aktivieren".
- **Gesundheit:** Trefferpunkte, Max. TP, Wunden, Max. Wunden; Wundeffekte, Tödliche Effekte, Statuseffekte; Körperschema mit 12 Zonen für gezielte Angriffe.
- **Attribute:** 22 Fertigkeiten mit Punkten; pro Attribut ein **Misc**-Feld und eine Summe. Erfahrungsuhr (1–12) und Stufe.
- **Seite 2 – Spezialisierungstabelle:** Zeilen St. 1, St. 1, St. 1, St. 2…St. 12; Spalten Genauigkeit, Ausweichen, Schlagkraft, Verteidigung, Initiative, Tempo, Augments, DIY, Wunden, Trefferpunkte; Zeile **Misc** und Zeile **Summen**.
- Geschichten, Volksmerkmale, Bargeld, Geld auf der Bank, Ausrüstung, Augments, Notizen.

**Implizite Formeln für das Werkzeug:**
```
Accuracy (per weapon) = Σspecialty Acc + misc + race/trait/story/weapon mods
Evade   = Σ Eva + misc + race mods − armor evade penalty (+ deflection when active)
Strike  = Σ Stk + misc + mods ; Defense = Σ Def + misc + mods
Priority= Σ Pri + mods ; Speed = race speed + Σ Spd + mods − armor speed penalty
HP max  = Σ HP + mods ; Wounds max = 12 (race-dependent) + Σ Wnd + mods − permanent losses
Augments known = Σ Aug ; DIY = Σ DIY
AP = 3 / 4 (L4) / 5 (L8) / 6 (L12)
```

---

## 3. Völker (Kap. 3, S. 28–49)

*Die Merkmalstexte unten sind Zusammenfassungen (noch nicht durch den Buchtext ersetzt – siehe §8).*

Legende: „Tempo" = Land / Schwimmen / Klettern in Fuß. Jedes Volk listet feste Merkmale, danach eine d12-Zufallsmerkmal-Tabelle.

### 3.1 Mensch (S. 29)
**Tempo:** 25 / 15 / 15.
**Fest:** wähle **zwei** von:
| Option | Effekt | Tags |
|---|---|---|
| Bevorzugtes Attribut | Wähle 1 Attribut: Bei einer natürlichen 1 mit diesem Attribut addierst du trotzdem Boni (nicht die seiner Fertigkeiten). | `[PASSIVE]` |
| Innovativ | +1 DIY, +2 Augments (nur wenn du mit einem Handwerk startest). | `[STAT:DIY +1] [STAT:Aug +2]` |
| Unerreicht | Du gewinnst alle Gleichstände bei Würfen (normalerweise gewinnt der Angreifer). | `[PASSIVE]` |
| Unnachgiebig | +3 TP zu Beginn, +1 TP pro gelernter Spezialisierung. | `[STAT:HP +3 +1×specialties]` |

**Zufällig (d12):**
| d12 | Merkmal | Effekt | Tags |
|---|---|---|---|
| 1 | An die Dunkelheit gewöhnt | Keine Mali durch schlechte Beleuchtung (Blindheit wirkt weiterhin). | `[COND]` |
| 2 | Anpassungsfähig | Keine Mali durch Umgebungen mit extremer Hitze/Kälte/Feuchtigkeit. | `[NARR]` |
| 3 | Schnell neu orientiert | Das Neuorientieren aus Desorientiert kostet 1 AP statt 3. | `[PASSIVE]` |
| 4 | Von Gefühlen getrieben | Kann einen Kampf nicht erschöpft beginnen, wenn ein Freund in Gefahr ist. | `[COND]` |
| 5 | Große Statur | +2 Schlagkraft. | `[STAT:Stk +2]` |
| 6 | Zäh & stämmig | +6 TP. | `[STAT:HP +6]` |
| 7 | Schwung | +5 Initiative, wenn du weißt, dass ein Kampf bevorsteht (nicht bei Hinterhalt). | `[COND] [STAT:Pri +5]` |
| 8 | Affenverwandtschaft | +10 ft Klettertempo. | `[STAT:Climb +10]` |
| 9 | Aufmerksam | +4 auf Listwürfe zum Bemerken. | `[COND]` |
| 10 | Flinke Füße | Landtempo 35 ft statt 25. | `[STAT:Spd base 35]` |
| 11 | Reaktionsschnell | +3 auf alle Initiativewürfe, auch überrascht. | `[STAT:Pri +3]` |
| 12 | Krawallmacher | +4 List zum Einschüchtern oder Provozieren. | `[COND]` |

### 3.2 Ayodin (S. 30–33)
**Tempo:** 25 / 35 / 15.
**Fest:**
- **Amphibisch:** atmet Luft und Wasser. `[NARR]`
- **Vielseitige Flügelflossen:** +1 Ausweichen. `[STAT:Eva +1]`

**Zufällig (d12):**
| d12 | Merkmal | Effekt | Tags |
|---|---|---|---|
| 1 | Blindsinn | Echoortung: sieht unabhängig vom Licht, außer wenn taub. | `[COND]` |
| 2 | In den Meeren geboren | +10 ft Schwimmtempo. | `[STAT:Swim +10]` |
| 3 | Eingebautes Bollwerk | Flossen zählen beim Parieren als Schilde. | `[GEAR]` |
| 4 | Ausdrucksstark | +3 List beim Überzeugen/Ändern von Gefühlen. | `[COND]` |
| 5 | Innere Stille | +2 List unter Druck / wenn eingeschüchtert oder provoziert. | `[COND]` |
| 6 | Meistertaucher | Kein Fallschaden bei der Landung im Wasser. | `[COND]` |
| 7 | Natürliche Berührung | Waffenlos SK 3. | `[GEAR] unarmed DC=3` |
| 8 | Passiv | +4 Geist, wenn als Widerstand benutzt. | `[COND]` |
| 9 | Mächtige Lähmung | Jeder, den du berührst: −3 auf seinen nächsten Ausweichwurf (endet am Ende seines nächsten Zuges). | `[COND]` |
| 10 | Schrecken der Tiefe | +3 Schlagkraft gegen angrenzende Feinde. | `[COND] [STAT:Stk +3 melee-adjacent]` |
| 11 | Vorhut | Angrenzende Verbündete +2 Ausweichen (stapelt sich nicht mit anderen, die es haben). | `[COND] aura` |
| 12 | Flügel als Arme | Flügel können einhändige Gegenstände halten (keine zweihändigen). | `[GEAR]` |

### 3.3 Elf (S. 34–37)
**Tempo:** 30 / 20 / 30.
**Fest:**
| Merkmal | Effekt | Tags |
|---|---|---|
| Grobknochig | +2 auf alle Kraftwürfe (Attribut). | `[PASSIVE]` |
| Zäh | +4 TP. | `[STAT:HP +4]` |
| Baumzerreißende Stärke | Waffenlos & Nahkampfwaffen +1 SK. | `[GEAR] melee/unarmed DC +1` |
| Schwache Seelen | −3 auf Geistwürfe (Attribut, nicht Geistfertigkeiten). | `[PASSIVE]` |
| Ausgezehrte Essenz | −1 Essenzmanipulationsslot (Bio-Flux). | `[GEAR]` |

**Zufällig (d12):**
| d12 | Merkmal | Effekt | Tags |
|---|---|---|---|
| 1 | Zahnräder der Welt | +6 List, um nicht-organische Störungen in einem Gebiet zu erkennen. | `[COND]` |
| 2 | Gefahrensinn | +3 Initiative. | `[STAT:Pri +3]` |
| 3 | Ohren zum Himmel | Hörwürfe +1 Stufe. | `[COND]` |
| 4 | Flug ohne Flügel | +10 ft Landtempo (→ 40). | `[STAT:Spd +10]` |
| 5 | Frucht der Gefallenen | Hebt Schwache Seelen auf; +3 Geist beim Einsatz von Heldentaten. | `[PASSIVE]` |
| 6 | Falsch besetzt | +2 List beim Informationen sammeln. | `[COND]` |
| 7 | Wie das Grab | Nachdem du einen ganzen Zug versteckt warst, +5, um unentdeckt zu bleiben. | `[COND]` |
| 8 | Edle Kreatur | Angriff +1 AP: +Schlagkraft in Höhe deiner Stufe. | `[ATTACK+1] [SCALE:Level]` |
| 9 | Wütende Loyalität | Wird ein angrenzender Verbündeter getroffen, reflexiver Nahkampfangriff gegen den Angreifer in Reichweite. | `[REFLEX]` |
| 10 | Eiserner Griff | +6, um etwas festzuhalten. | `[COND]` |
| 11 | Unaufhaltsam | Tempomali durch Wunden/Status um 10 ft verringert. | `[PASSIVE]` |
| 12 | Springender Räuber | +10 ft Weitsprung, +2 ft Hochsprung. | `[NARR]` |

### 3.4 Farishtaa (S. 38–41)
**Tempo:** 25 / 15 / 15.
**Fest:**
| Merkmal | Effekt | Tags |
|---|---|---|
| Zum Fliegen geboren | Beginne mit **2 Fertigkeitspunkten in Pilot** (zusätzlich zu den normalen Startpunkten; dort dürfen wie üblich Startpunkte hinzugefügt werden). | `[STAT:Ace +2]` |
| Durchdringender Blick | +1 Genauigkeit. | `[STAT:Acc +1]` |
| Unberechenbar | +2 List im Umgang mit Menschen. | `[COND]` |

**Zufällig (d12):**
| d12 | Merkmal | Effekt | Tags |
|---|---|---|---|
| 1 | Missglückte Operation | Erhalte die Elfenmerkmale Baumzerreißende Stärke und Schwache Seele. | `[GEAR] [PASSIVE]` |
| 2 | Tänzerkörper | +2 auf Geschickwürfe (Attribut). | `[PASSIVE]` |
| 3 | Emotionale Unnahbarkeit | Furchteffekte −1 Stufe (immun gegen Furcht S1). | `[PASSIVE]` |
| 4 | Sofortige Bewegung | 1 AP reflexiv bei Kampfbeginn: +8 auf den Initiativewurf. | `[REFLEX]` |
| 5 | Heiligenschein | 10-ft-Lichtaura + leichte Wärme, unterdrückbar. | `[NARR]` |
| 6 | Prominenter Wirt | Würfle stattdessen auf der **Elfen**-Zufallsmerkmal-Tabelle. | `[RULE]` |
| 7 | Oberflächliche Werte | +2 Ausweichen und Widerstand gegen gezielte Angriffe auf Kopf, Augen, Ohren. | `[COND]` |
| 8 | Geist der Engel | Eine natürliche 1 auf Geist (Attribut) addiert trotzdem Boni. | `[PASSIVE]` |
| 9 | Überlegenheitskomplex | Angrenzende Feinde −2 Verteidigung. | `[COND] aura` |
| 10 | Hauch von Wahnsinn | Bei 0 TP: +4 Genauigkeit und +4 Schlagkraft. | `[COND]` |
| 11 | Unerklärliche Erinnerungen | +2 auf alle Listwürfe. | `[PASSIVE]` |
| 12 | Unentwickelte Flügel | Kein Fallschaden, außer gefesselt/bewusstlos/bei schlechtem Wetter. | `[COND]` |

### 3.5 Gnom (S. 42–45)
**Tempo:** 15 / 10 / 10.
**Fest:**
| Merkmal | Effekt | Tags |
|---|---|---|
| Größerer Geist | +3 auf Geistwürfe. | `[PASSIVE]` |
| Leichter Körperbau | −2 auf Kraftwürfe. | `[PASSIVE]` |
| Kleine Statur | +1 Ausweichen. | `[STAT:Eva +1]` |
| Kleinere Waffen | Kann leichte Waffen nicht verbergen; waffenlos SK 1. | `[GEAR] unarmed DC=1` |
| Zufällige Volksmerkmale | Wähle 1 Merkmal **und** würfle 1 (Duplikate neu würfeln) → **2 Zufallsmerkmale**. | `[RULE]` |
| (kleine Kreatur) | Wird +5 ft weiter geworfen (Regel Greifen/Werfen). | `[NARR]` |

**Zufällig (d12):**
| d12 | Merkmal | Effekt | Tags |
|---|---|---|---|
| 1 | Sicht biegen | Sieht um Ecken bis zu 90°. | `[NARR]` |
| 2 | Tiefe Taschen | Kann leichte und mittlere Gegenstände verbergen. | `[NARR]` |
| 3 | Erdformung | 2 AP: Erde in einem 5-ft-Bereich um 5 ft heben/senken. | `[ACTION]` |
| 4 | Die Erde spüren | Spürt Vibrationen im Umkreis von 15 ft, wenn er den Boden berührt (vergleichender Listwurf gegen Schleichen). | `[COND]` |
| 5 | Wachstumsschub | 1 AP: Wechsel zur Elfengröße – nutze die Elfenvolksmerkmale statt der Gnomen, solange du groß bist. | `[ACTION] swaps race traits` |
| 6 | Lautlos | Lautlose Schritte; Schleichen +1 Stufe. | `[COND]` |
| 7 | Teile der Natur | 3 AP: ziehe ein leichtes einfaches Werkzeug/eine Waffe/Fackel aus Baum oder Erde. | `[ACTION]` |
| 8 | Durchdringender Blick | Fernkampfwaffen: doppelte Reichweite, +2 Genauigkeit. | `[GEAR] ranged Acc +2, range ×2` |
| 9 | Drahtseilmuskeln | Hebt Leichten Körperbau auf; +2 Schlagkraft; waffenlos SK 2. | `[STAT:Stk +2] [GEAR] unarmed DC=2` |
| 10 | Wasserwandeln | 1 AP pro Zug: auf ruhigem Wasser stehen. | `[ACTION]` |
| 11 | Windwandeln | 1 AP: 40 ft in eine Richtung gleiten. | `[ACTION]` |
| 12 | Drahtig | +1 zusätzliches Ausweichen. | `[STAT:Eva +1]` |

### 3.6 Satyr (S. 46–49)
**Tempo:** 35 / 10 / 10.
**Fest:**
| Merkmal | Effekt | Tags |
|---|---|---|
| Alkoholimmunität | Wird von Alkohol nicht negativ beeinflusst. | `[NARR]` |
| Einfühlsam | Würfle zweimal und nimm den höheren Wurf, wenn du Lügen erkennst. | `[COND]` |

**Zufällig (d12):**
| d12 | Merkmal | Effekt | Tags |
|---|---|---|---|
| 1 | Geborener Held | Heldentaten (Geist): zweimal würfeln, den höheren nehmen. | `[COND]` |
| 2 | Waffenbrüder | Angrenzend zu einem Satyr-Verbündeten: beide +2 Genauigkeit (keine Stapelung). | `[COND]` |
| 3 | Auf Dauer gebaut | +6 TP. | `[STAT:HP +6]` |
| 4 | Auf das Schlimmste gefasst | +4 auf Initiativewürfe. | `[STAT:Pri +4]` |
| 5 | Leichtfüßig | +10 ft Tempo (→ 45). | `[STAT:Spd +10]` |
| 6 | Furchteinflößender Kämpfer | Waffenlos SK 4 (Hörner/Hufe). | `[GEAR] unarmed DC=4` |
| 7 | Gehörnt & gefährlich | Waffenlose Hornangriffe verursachen +1 nicht absorbierbaren Blutungsschaden. | `[GEAR]` |
| 8 | Natürlicher Rausch | Ignoriere Erschöpfung, wenn du in den letzten Stunden Alkohol getrunken hast (nicht bei mehrtägiger Erschöpfung). | `[COND]` |
| 9 | Giftimmunität | Widerstand Kraft gegen Gift +1 Stufe. | `[COND]` |
| 10 | Beschützer | Angrenzende Verbündete +2 Verteidigung. | `[COND] aura` |
| 11 | Sicherer Huftritt | Ignoriere Tempomali von geringem & unsicherem Gelände. | `[COND]` |
| 12 | Vom Krieg unbeeindruckt | +4 auf den Widerstand gegen Betäubung. | `[COND]` |

### 3.7 Völkervergleich (für Standardwerte des Werkzeugs)

| Volk | Land | Schwimmen | Klettern | Feste Wertmods | Waffenlos SK | Anmerkungen |
|---|---|---|---|---|---|---|
| Mensch | 25 | 15 | 15 | 2 von 4 Optionen | 2 | |
| Ayodin | 25 | 35 | 15 | Aus +1 | 2 | amphibisch |
| Elf | 30 | 20 | 30 | TP +4, Nahkampf-SK +1, Kraftwürfe +2, Geistwürfe −3 | 3 (2+1) | −1 Essenzslot |
| Farishtaa | 25 | 15 | 15 | Gen +1, Pilot +2 Fertigkeitspunkte | 2 | |
| Gnom | 15 | 10 | 10 | Aus +1, Geistwürfe +3, Kraftwürfe −2 | 1 | 2 Zufallsmerkmale |
| Satyr | 35 | 10 | 10 | – | 2 | |

Kein Volk verändert in diesem Buch die Basis von 12 Wunden (geprüft: keine der Völkerseiten nennt eine andere Wundenzahl). Flugtempo kommt nur aus Ausrüstung/Augments/Fahrzeugen.

---
## 4. Nationalitäten, Organisationen, Geschichten & Religionen (Kap. 4, S. 50–71)

*Die Geschichtentexte unten sind Zusammenfassungen (noch nicht durch den Buchtext ersetzt – siehe §8).*

Geschichten sind überwiegend erzählerisch. Nur wenige tragen numerische Modifikatoren; diese sind markiert. Vorschlag für das Werkzeug: frei wählbare Liste mit optionalen Modifikatoren.

### 4.1 Nationalitäten (Hintergrundzusammenfassung)

| Nationalität | Region / Zusammenfassung | Bemerkenswerte Beziehungen |
|---|---|---|
| **Evanglessian** (am häufigsten) | Junges, von Menschen geführtes Imperium (gegründet von Velkya), Dampf, Eisenbahnen, Elitemilitär, Luftflotte; aufgeschlossener Schmelztiegel; Tailemy ist Staatsreligion. | Abneigung gegen paldoranische Piraten, ozeanische Ayodin, Hauds; gut mit Izedans, Dalvozzeans. |
| **Dalvozzean** | Von Farishtaa regierte Kastennation im Hohen Rilausischen Wald; Hauptstadt Daion (weiße Türme über dem Blätterdach, Slums darunter); regiert von den Neun Schwingen der Göttlichkeit (Tagesgesellschaft). | Spannungen mit Hauds (Siyesh) und Izedans; höflich zu seltenen Ayodin/Paldorans. |
| **Izedan** | Wüstennomaden und Aasfresser (die Quist), Karawanen, rituelle Narbenbildung, Dampfarmbrüste; blasse/bleichweiße Haut, oft kahl. | Schlecht mit Hauds; gut mit Valdru-Gnomen, Satyrn; fasziniert von Ayodin. |
| **Paldoran Exile** | Strahlenverseuchte Heimat (Ätherresonatoren); die Menschen leben auf riesigen Sturmschiffen und plündern nach Vorräten; Infernale Jinzium-Kirche. | Weithin gemieden; feindselig mit Salzwasser-Ayodin; misstrauisch gegenüber Zel Hauds; am besten aufgenommen in Evangless. |
| **Zel Haud** | Industrielle haudische Provinz Zelhost (Erzherzog Zimarati), matriarchalisch, sehr große Menschen; halbunabhängig von der Kaiserin in Siyesh. | Elitär gegenüber Nachbarn; Erbe der Satyr-Sklaverei. |

### 4.2 Nationalitätsgeschichten (S. 53–61)

| Nationalität | Geschichte | Voraussetzung | Effekt | Tags |
|---|---|---|---|---|
| Evangless | Ayodin des Exodus | Ayodin | Angesehen bei älteren Evanglessians (kämpften mit den Landbewohnern). | `[NARR]` |
| Evangless | Royalist | – | Im Bürgerkrieg auf der Seite der Automatenarmeen des Kaisers; besser mit Royalisten. | `[NARR]` |
| Evangless | Militarist | – | Auf der Seite des Militärputsches; besser mit Militaristen. | `[NARR]` |
| Evangless | Veteran | – | Bürgerkriegsveteran mit Kriegsgeschichten. | `[NARR]` |
| Evangless | Siedler des Westens | – | Kann Vieh leicht beruhigen und lenken. | `[NARR]` |
| Evangless | Eingebürgerter Tharmurianer | – | Wird als Fremder gesehen (weißes Haar, blass). | `[NARR]` |
| Evangless | Evanglessianischer Adel | – | Zugang zu den meisten Regierungsgebäuden. | `[NARR]` |
| Evangless | Von Evangless adoptiert | – | Darf 1 Nationalitätsgeschichte einer anderen Nationalität wählen. | `[RULE]` |
| Dalvozzea | Wilder Elf | – | Überlebt unbegrenzt in Wäldern ohne Vorräte. | `[NARR]` |
| Dalvozzea | Hochgeborener Elf | Elf | Etwas höheres Ansehen als ein durchschnittlicher Elf. | `[NARR]` |
| Dalvozzea | Farishtaa der zweiten Generation | Farishtaa | Als Farishtaa geboren; Elfen sind neidisch. | `[NARR]` |
| Dalvozzea | Mitglied der Nachtgesellschaft | Farishtaa | Zugang zu allen Einrichtungen außer denen der Tagesgesellschaft. | `[NARR]` |
| Dalvozzea | Miadruide | Gnom | Kommt mit Dalvozzeans außerhalb der Kasten gut aus. | `[NARR]` |
| Dalvozzea | Söldner des Weißen Turms | – | Wird wie die Nachtgesellschaft angesehen; Prestige stapelt sich damit. | `[NARR]` |
| Dalvozzea | Aschengel | – | Rebellentätowierung; Verbundenheit mit Rebellen; die Polizei behandelt dich als Terroristen. | `[NARR]` |
| Dalvozzea | Elf von Adoipa | Elf | Von anderen Elfen bewundert. | `[NARR]` |
| Izeda | Schüler des Schmerzes | – | Rituell vernarbt; Schmerz bremst dich nicht (das Buch nennt keine Zahl – **unklar**; vermutlich erzählerisch). | `[NARR]` |
| Izeda | Zum Sammeln erzogen | – | Kann Kleinkram aufsammeln/verkaufen. | `[NARR]` |
| Izeda | Asagnu-Karawanenführer | – | Stolze königliche Karawane. | `[NARR]` |
| Izeda | Karawanenführer der Weisheit | – | Verbundenheit mit Geiern. | `[NARR]` |
| Izeda | Sonnenzorn-Elf | Elf | Wüstenelf, übersteht Vorurteile. | `[NARR]` |
| Paldorus | Blinder Passagier | – | Kein Bürger der Kolonie. | `[NARR]` |
| Paldorus | Von Jinzi auserwählt | – | Persönlich von der Kirche eingeladen. | `[NARR]` |
| Paldorus | Paldoranischer Militant | – | Militärischer Plünderer; anderswo gemieden/gehängt. | `[NARR]` |
| Paldorus | Gestrandeter Verbannter | – | Vom Sturmschiff verstoßen. | `[NARR]` |
| Paldorus | Spuren der Strahlung | – | Leichte Hautablösung durch Strahlung. | `[NARR]` |
| Paldorus | **Sturmschiff-Ingenieur** | – | **Beginne mit 1 Punkt in Ingenieur** (Fertigkeit). | `[STAT:Engineer +1]` |
| Zelhost | Matriarchin | Weiblich | Haudische Männer verneigen sich vor dir. | `[NARR]` |
| Zelhost | Imperialer Traditionalist | – | Kommt mit siyeshischen Hauds gut aus. | `[NARR]` |
| Zelhost | Satyr-Diener | Satyr | Zuckt zusammen, wenn ein Haud die Hand hebt (außerhalb des Kampfes). | `[NARR]` |
| Zelhost | Ehre ohne Etikette | – | Hauds erkennen deine Ehrbarkeit an. | `[NARR]` |
| Zelhost | **Nationaler Zeitvertreib** | – | +4 Wissenschaften, um Augments in einer alchemistischen Lösung zu erkennen. | `[COND]` |

> Hinweis: „Deal with the Devil" auf S. 59 ist ein Hintergrundkasten (König Caeliph & Jayro Tiin), keine Geschichte.

### 4.3 Organisationen & Mitgliedschaftsgeschichten (S. 62–65)

| Organisation | Zusammenfassung | Mitgliedschaftsgeschichten (Effekt) |
|---|---|---|
| **Die Brimstones** | Bande aus dem westlichen Evangless im Dienst von Viehbaronen; Söldner. | Brimstone-Schläger (kostenloses minderwertiges Rindfleisch von den Baronen); **Kleine Regierung, große Knarre** (+2 Widerstand gegen Einschüchterung durch nichtmilitärische Beamte auf Baronsland) `[COND]` |
| **Der Karneval** | „Verrückte" Untergrundbewegung gegen Tyrannei mit Luftschiffflotte (Varas Dyrashi). | Karnevalist (Mitfahrt auf Karnevals-Luftschiffen); Karnevalskünstler (Schläferzelle; erkennt Mitglieder sofort) |
| **Kohlenstaub-Gewerkschaften** | Arbeitergewerkschaften. | Kohlenstaub-Arbeiter (+4 Bemerken, ob ein Arbeitsplatz unsicher ist) `[COND]`; Kohlenstaub-Protestler (findet wohlgesinnte Angestellte) |
| **Fulbourne-Gesellschaft** | Aristokratische Bruderschaft des alten Geldes; Informationshändler. | Fulbourne-Neuling (Zugang zu den Logen); Fulbourne-Späher (Erkennungszeichen ab S2 verraten altes Geld); Neues Blut der Fulbourne (Zugang zu den Akten der Gesellschaft über dich) |
| **Hochflieger** | Elite-Clubs der Piloten (Bar Silver Lining, Aldamiir). | Hochflieger (Abzeichen → uneingeschränkter evanglessianischer Luftraum); Bürgerkriegsass (arrangiert genehmigte Duelle); Legendärer Hochflieger (VIP-Pass) |
| **LaVrey National Detective Agency** | Größte Sicherheitstruppe (Jordana LaVrey). | LaVrey-Agent (erhält Auftragsmitteilungen); LaVrey-Detektiv (Dienstmarke); LaVrey-Zugwächter (hält Frachtzüge an) |
| **Renovatoren** | Bauen Wahrzeichen wieder auf (Jed K. Sampson), Analytische Maschinen. | Renovator (Wahrzeichen-Piktogramme); Renovator-Vorarbeiter (sofortige historische Aufzeichnungen über die Maschine); Renovator-Konstrukteur (Zugang zu Arbeitern) |
| **Söhne des Streits** | Sozialreformbewegung für ein Parlament. | Sohn des Streits (Freunde unter Militaristen/Gewerkschaften); Als Sohn geboren (Journalisten sind interessiert); Wohltätige Tochter (Verbündete an niederen Orten) |

### 4.4 Hintergrundgeschichten (S. 66–68)
Normalerweise 1 bei der Erschaffung (der Erzähler kann mehr erlauben).

| Geschichte | Effekt | Tags |
|---|---|---|
| Luftgeboren | Kämpfe ungehindert in der Luft. | `[COND]` |
| Barkeeper | Mixe jedes Getränk. | `[NARR]` |
| Einbrecher | List, um das Inventar eines Ziels zu erspähen, +1 Stufe. | `[COND]` |
| Viehtreiber | +1 Gen, um ein Tier mit einer Peitsche zu greifen. | `[COND]` |
| Koch | Wissenschaftenwurf zum Kochen: zweimal würfeln, den höheren nehmen. | `[COND]` |
| Geistlicher (erfordert eine Glaubens-Mitgliedschaftsgeschichte) | Jemanden von deinem Glauben zu überzeugen +1 Stufe. | `[COND]` |
| Schaffner | Kenne Aufbau/Funktion ziviler Zugwagen. | `[NARR]` |
| Cowboy | List zum Auskundschaften bei einer Verschnaufpause: zweimal würfeln, den höheren nehmen. | `[COND]` |
| Beutelschneider | Gegenstände unauffällig übergeben/nehmen, ohne Reflexe zu provozieren. | `[COND]` |
| Urkundenfälscher | Dokumente fälschen. | `[NARR]` |
| Waldsammler | Finde in der Wildnis immer Nahrung. | `[NARR]` |
| Glücksspieler | Setze in jeder Pause ≤10 Prinzen auf alles oder nichts (gerade/ungerade). | `[NARR]` |
| Landadel | Angestellte deines Anwesens +1 Kraft. | `[NARR]` |
| Geschickter Handwerker | Stelle alle Ausrüstungsgegenstände der „Abenteuergrundlagen" in einer Pause her. | `[NARR]` |
| Kinematiker | Bestimme die Reichweite einer Waffe per List. | `[NARR]` |
| Gesetzeshüter | +2 List, um Gesetzesbrecher auf frischer Tat zu ertappen. | `[COND]` |
| Bibliothekar | Recherche braucht die halbe Zeit. | `[NARR]` |
| Holzfäller | Sage voraus, wohin Bäume fallen. | `[NARR]` |
| Seemann | Kenne das Wasserleben in der Nähe. | `[NARR]` |
| Geldverleiher | Merke dir Namen/Orte; verleihe Geld. | `[NARR]` |
| Geheimnisvoller Zwilling | Übernimm Fertigkeiten, Spezialisierungen, EP und Geschichten eines soeben verstorbenen Gruppenmitglieds. | `[RULE]` |
| Adel | Siegelring; willkommen unter Eliten. | `[NARR]` |
| Arzt | List zum Diagnostizieren: zweimal würfeln, den höheren nehmen. | `[COND]` |
| Eisenbahnarbeiter | Kostenlose Fahrten in Personenzügen. | `[NARR]` |
| Reparateur | Repariere kaputte Gegenstände außerhalb des Kampfes, auch wenn du sie nicht herstellen kannst. | `[NARR]` |
| Rodeoreiter | +4 Geschick, um beim Abwerfen im Sattel zu bleiben. | `[COND]` |
| Von der Kirche erzogen (unter Tailemy aufgeführt) | +2 List, um etwas von einer tailemitischen Kirche zu bekommen. | `[COND]` |

### 4.5 Religionen & Glaubens-Mitgliedschaftsgeschichten (S. 69–71)

**Tailemy** – Staatsreligion von Evangless; die Geliebte Mutter opferte sich Aeon, um die Welt zu gebären; heiliges Buch *Aktailem*; geführt vom Triun (Paladin, Kreuzritter, Märtyrer); begrüßt Wandel & Technologie; Symbol Motte (+ Schlange = Aeon).

| Geschichte | Typ | Voraussetzung | Effekt | Tags |
|---|---|---|---|---|
| Kreuzritter von Tailemy | Glaubensmitgliedschaft | – | +1 Schlagkraft gegen jeden, der Ketzerei gegen die Geliebte Mutter erklärt hat. | `[COND] [STAT:Stk +1]` |
| Frommer von Tailemy | Persönlichkeit | – | In jeder Woche, in der du eine tailemitische Predigt besucht hast: +1 auf alle Geistwürfe. | `[COND]` |
| Märtyrer von Tailemy | Glaubensmitgliedschaft | – | Geistlicher; von Gläubigen gut behandelt. | `[NARR]` |
| Geweiht von Tailemy | Glaubensmitgliedschaft | jede andere tailemitische Mitgliedschaftsgeschichte | Darf Riten durchführen & die Kirche vertreten. | `[NARR]` |
| Paladin von Tailemy | Glaubensmitgliedschaft | – | **+1 Schutzklasse** bei der Verteidigung eines anderen Tailemiten. | `[COND] [STAT:Soak +1]` |
| Von der Kirche erzogen | Hintergrund | – | +2 List, um etwas von einer tailemitischen Kirche zu bekommen. | `[COND]` |

**Freier Wille** – haudische Religion (Kaiserin Zoleesha IV.) der Vernunft und Wissenschaft; Lehrer, Gelehrte, Hierophant; kein heiliges Buch, keine Riten.

| Geschichte | Voraussetzung | Effekt | Tags |
|---|---|---|---|
| Akolyth des Freien Willens | – | +1 Geist im Umgang mit Engstirnigen/Dogmatischen. | `[COND]` |
| Lehrer des Glaubens | – | Darf Gottesdienste leiten; +2 List an Tagen, an denen du das tust. | `[COND]` |
| Gelehrter des Freien Willens | Lehrer des Glaubens + veröffentlichte intellektuelle Arbeit | Vorteile des Lehrers; darf Freien Willen regional vertreten. | `[NARR]` |

**Jinzium** – älteste Religion; Sonnengott Jinzi; Seelen werden zu Sternen; Fraktionen: Ewige Kirche/Orthodoxe (Igi, der Elf, der in Feuer schreibt, Leitendes Paradigma), Erweckte (Dalvozzea, Neun Schwingen; geflügelte Farishtaa als Engel), Infernales Jinzium (Paldorans, Sechs Infernale).

| Geschichte | Voraussetzung | Effekt | Tags |
|---|---|---|---|
| Spross der Sonne | – | +2 Geist, um an hellen, blauen Tagen konzentriert zu bleiben. | `[COND]` |
| Archon | – | Darf Gottesdienste leiten; Hilfe & Obdach von Gemeinden. | `[NARR]` |
| Seele von Sol | Archon | Darf für die Kirche sprechen. | `[NARR]` |
| Orthodoxer Jinzist | – | Eine Predigt von Igi bestärkt deinen Glauben vollständig. | `[NARR]` |
| Sternengeborener Traditionalist | – | Rituale machen Agnostiker neugierig. | `[NARR]` |
| Engelsfieber | – | Nie erschöpft in Gegenwart einer geflügelten Farishtaa. | `[COND]` |

Ayodin-Religionen (S. 32, nur Hintergrund): **Harabe Mavi** (Mondgöttin Aeon; die Oberfläche gehört den Ayodin) und **Pfad des Gilkoroh** (Märtyrerheiliger; Süßwasser-Ayodin).

> Weitere Geschichtstypen, die erwähnt, aber in diesem Buch nicht mit vollständigen Tabellen aufgeführt werden: **Persönlichkeitsgeschichten** (z. B. *Yobbish*) und **Veränderungsgeschichten** (z. B. *Burn Victim*) – vom Erzähler vergeben; das Werkzeug sollte eigene Geschichten mit eigenen Modifikatoren erlauben.

---
## 5. Ausrüstung (Kap. 5, S. 72–87)

### 5.1 Währung – der Trust (S. 73)

| Münze | = |
|---|---|
| 1 Duke | teilbar in ½, ¼, ⅛ (magnetische Stücke) |
| 1 Prinz | 10 Dukes |
| 1 König | 10 Prinzen = 100 Dukes |

Richtpreise: Waren für eine Mahlzeit ≈ ¼ Duke (Krug Ale); gutes Schwert ≈ 5 Prinzen; durchschnittlicher Tageslohn 1–3 Dukes.

| Dienstleistung des Trusts | Kosten |
|---|---|
| Konto eröffnen | 5 Prinzen |
| Schließfach | 3 Prinzen |
| Schließfach im Tresor | 15 Prinzen |
| Einzahlen/Abheben bei der eigenen Filiale | kostenlos |
| Einzahlen/Abheben bei einer anderen Filiale | 1 Duke |
| Währung in Prinzen umtauschen | 1 Duke pro 5 Prinzen |

Bogenfelder: Bargeld, Geld auf der Bank.

### 5.2 Nahkampfwaffen (S. 74–75)
| Größe | Definition | AP | SK | Hände | Ziel | Spezialisierungs-Fertigkeitshinweis |
|---|---|---|---|---|---|---|
| Waffenlos | keine Waffe; kann nicht vom Waffenschmied verbessert werden | 1 | 2 (Volksmods!) | – | angrenzend | Raufen |
| Leicht | passt in die Tasche; verbergbar; alle kleinen Gegenstände zählen | 2 | 4 | 1 | angrenzend | Spionage |
| Mittel | einhändig, nicht verbergbar | 2 | 6 | 1 | angrenzend | Fechtkunst |
| Schwer | zweihändig | 2 | 8 | 2 | angrenzend | Überwältigen |
| Überschwer | zwei Hände zum Tragen und Schwingen; benötigt die Haltung **Stand** (1 AP; keine andere Haltung, solange du im Stand bist) | 2 | 10 | 2 | angrenzend | – |

Überschwer ohne Stand: −3 Genauigkeit und Schlagkraft (wie improvisiert).

**Varianten (kombinierbar, jeder Malus gilt):**

| Variante | Effekt | Erlaubt bei |
|---|---|---|
| Biegsam | kann Griffe ausführen (Peitsche, Kette, Flegel); −1 SK | allen |
| Stangenwaffe | +5 ft Reichweite (Angriff innerhalb von 10 ft); −1 SK | mittel und schwerer |
| Wurf | kann geworfen werden; −1 SK. Wurfweite: leicht 25 ft, mittel 75 ft, schwer 50 ft; −1 Gen pro 10 ft darüber hinaus. Nicht-Wurfwaffen höchstens 25 ft. Eine geworfene Waffe zählt für Spezialisierungen als **nicht Nahkampf**. | allen |
| Improvisiert | nicht als Waffe konstruiert; der Erzähler legt die Größenklasse fest; −3 Gen und Schlagkraft | – |

Beispiele: biegsame Stangenwaffe = −2 SK, Reichweite 10 ft, kann greifen; Bola = Wurf + biegsam.

Standardreichweite: angrenzend (5 ft); Stangenwaffe 10 ft.

### 5.3 Schusswaffen (S. 76–77)
**Schusswaffen verwenden Genauigkeit für den Schaden:** ein Wurf – Genauigkeit gegen Ausweichen zum Treffen, dann wird dasselbe Genauigkeitsergebnis für den Schaden in eine Stufe umgerechnet (Schlagkraft wird nicht verwendet). Zwischen den Schüssen muss nachgeladen werden.

| Größe | AP zum Feuern | SK | Hände | AP zum Laden | Basisreichweite | Distanzstufe (je −1 Gen) |
|---|---|---|---|---|---|---|
| Leicht | 2 | 2 | 1 | 0 | 50 ft | 10 ft |
| Mittel | 2 | 4 | 1 | 1 (einhändig) / 0 (zwei Hände) | 100 ft | 25 ft |
| Schwer | 2 | 6 | 2 | 1 | 200 ft | 50 ft |
| Überschwer | 2 | 8 | 2 | 2 | 300 ft | 100 ft |

Überschwer benötigt den Stand; ohne ihn −3 Genauigkeit.
**Doppelläufig** (keine Zusatzkosten): zweimal feuern, bevor nachgeladen wird; Nachladen +1 AP pro geladener Patrone.

**Munition** (Typwechsel: 1 AP):

| Munition | Effekt |
|---|---|
| Patrone | Grundwerte |
| Platzpatrone | kein Projektil |
| Schrot | kein Genauigkeitsverlust über die Distanz; stattdessen −1 SK pro Distanzstufe über die Basis hinaus |
| Scharfschützenpatrone | −1 Gen pro **2** Distanzstufen; −1 SK |
| Hochschadenspatrone | +2 SK; +1 AP Ladezeit |

### 5.4 Bögen (S. 78)
Bögen verwenden Genauigkeit zum Treffen und **Schlagkraft** für den Schaden (normal). Immer zwei Hände. Kein Laden.

| Größe | AP | SK | Basisreichweite | Distanzstufe |
|---|---|---|---|---|
| Leicht (inkl. Schleudern) | 2 | 3 | 25 ft | 10 ft |
| Mittel | 2 | 5 | 50 ft | 10 ft |
| Schwer | 3 | 7 | 75 ft | 25 ft |
| Überschwer | 3 | 9 (wird wie eine schwere Waffe geführt) | 200 ft | 75 ft |

Überschwere Bögen benötigen den Stand; ohne ihn −3 Genauigkeit.

### 5.5 Armbrüste (S. 79)
Wie Schusswaffen: **Genauigkeit bestimmt den Schaden** (einzelner Wurf).

| Größe | AP zum Feuern | SK | Hände | AP zum Laden | Basisreichweite | Distanzstufe |
|---|---|---|---|---|---|---|
| Leicht | 2 | 3 | 1 | 1 | 25 ft | 10 ft |
| Mittel („Pistolenarmbrust") | 2 | 5 | 1 | 1 | 50 ft | 10 ft |
| Schwer | 2 | 7 | 2 | 2 | 100 ft | 25 ft |
| Überschwer | 2 | 9 | 2 | 3 | 150 ft | 50 ft |

Überschwere Armbrüste benötigen den Stand; ohne ihn −3 Genauigkeit.

### 5.6 Pfeile & Bolzen (S. 78–79)
Bolzentyp wechseln: 1 AP; Pfeiltyp wechseln: kostenlos.

| Typ | Effekt |
|---|---|
| Standard | Grundwerte |
| Klingenspitze | −2 Gen; 1 Blutung pro Stufe des verursachten Schadens |
| Widerhaken | Entfernen kostet 2 AP (normalerweise 1); Seil anbringen für 1 AP → Klettern/Seilrutsche |
| Signal | sehr lauter Pfiff; −1 SK |

### 5.7 Rüstung (S. 80)
Schutz funktioniert wie Schadensklasse: `soak = Soak Class × Defense tier`.

| Typ | Schutzklasse | Ausweichmalus | Tempomalus | Kletter- & Schwimmmalus | Materialien | Anlegezeit | Anlegen mit Hilfe | Preis |
|---|---|---|---|---|---|---|---|---|
| Ungerüstet | 0 | 0 | 0 | 0 | keine/organisch/Textil | – | – | – |
| Minimal | 1 | 0 | 0 | 0 | Metall/organisch/Textil | 3 AP | – | 1 Prinz |
| Leicht | 2 | −1 | −5 ft | −5 ft | Metall/organisch/Textil | 6 AP | – | 5 Prinzen |
| Mittel | 3 | −2 | −5 ft | −10 ft | Metall/organisch | 24 AP | 12 AP | 15 Prinzen |
| Schwer | 4 | −3 | −10 ft | −15 ft | Metall/organisch | 3 Min. | 1 Min. | 40 Prinzen |
| Überschwer | 5 | −4 | −10 ft | −20 ft | Metall | 10 Min. | 3 Min. | 75 Prinzen |

(Anlegezeiten anhand des Seitenlayouts überprüft.)

### 5.8 Parierwaffen (S. 81)
Parieren = 1 AP (Unterbrechung), wann immer du angegriffen wirst; addiert einen Bonus auf diesen Ausweichwurf.

| Gegenstand | Ausweichbonus | gegen | Anmerkungen | Materialien | Preis |
|---|---|---|---|---|---|
| Parierdolch | +3 | nur Nahkampf | zählt auch als leichte Waffe | Metall/organisch/Holz | 1 Prinz |
| Umhang | +3 | nur Nahkampf | Hand bleibt frei, kann Griffe ausführen | organisch/Textil | 1 Prinz |
| Schild | +4 | Nahkampf **und** Fernkampf | kann in der Schildhand Dinge halten, dann aber nicht parieren | Metall/organisch/Holz | 4 Prinzen |

### 5.9 Tiere (S. 82–83)
Ein Tier führen: 1 AP pro Zug; es gibt seine eigenen AP zum Bewegen aus; es teilt sich deinen Zug. Andere Aktionen: Du und das Tier zahlt jeweils die normalen AP-Kosten.
Unterhalt ≈ 1 Duke/Tag.

| Tier | Kosten | AP | TP | Wunden | Ini | Tempo | Aus | Ver | Schutz (S1–S4) | Angriff |
|---|---|---|---|---|---|---|---|---|---|---|
| Pferd | 100 Pr | 3 | 16 | 9 | +0 | 50 ft (×2, wenn alle AP für Bewegung ausgegeben werden) | −1 | +1 | 3/6/9/12 (Fell) | Huf 2 AP, natürlich mittel, Gen +0, Sch +1, Schaden 6/12/18/24 |
| Hund | 35 Pr | 3 | 12 | 8 | +0 | 40 ft | +0 | +0 | 2/4/6/8 (Fell) | Biss 2 AP, natürlich mittel, Gen +1, Sch +3, Schaden 6/12/18/24; +1 Sch pro Verbündetem innerhalb von 25 ft mit Rudelinstinkt; kann bewegen–angreifen–bewegen |
| Greifvogel | 45 Pr | 3 | 11 | 8 | +0 | 25 ft, 45 ft Flug | +1 | +0 | 0 (ungerüstet) | Kralle 2 AP, natürlich leicht, Gen +3, Sch +1, Schaden 4/8/12/16; nach einem Sturzflug von 10+ ft: Widerstand Kraft des Ziels gegen Akrobatik (+2), sonst liegend |

| Tier | Fertigkeiten | Attribute | Spezialisierungen / Geschichten |
|---|---|---|---|
| Pferd | Akrobatik 2, Raufen 1, Überwältigen 1, Zähigkeit 2, Schamanismus 1 | Kraft 3, List 0, Geschick 2, Geist 1, Wiss 0 | Galopp, Groß; Vierbeiner, Natürliche Rüstung. Reitbar. Zusätzliche Beinzonen, keine Arme/Hände. |
| Hund | Spionage 1, Raserei 1, Zähigkeit 1, Showtalent 2, Taktik 2 | Kraft 2, List 4 (+2 Spürnase beim Fährtenlesen, +2 beim Wachen), Geschick 1, Geist 0, Wiss 0 | Satzsprung, Heulen (2 AP: Verbündete innerhalb von 25 ft +1/+2/+3/+4 Sch je nach Showtalent-Stufe beim nächsten Angriff); Vierbeiner, Wache, Natürliche Rüstung, Rudelinstinkt, Geruchssinn. Von Gnomen reitbar. |
| Greifvogel | Pilot 1, Akrobatik 2, Spionage 2, Zähigkeit 1, Taktik 1 | Kraft 1, List 3 (+10 beim Bemerken), Geschick 3, Geist 0, Wiss 0 | Tod von oben, Thermikgleiten (Haltung: doppeltes Flugtempo); Adlerauge, Angeborener Orientierungssinn, Klein, Flügel. Flügel = Beinzonen. |

### 5.10 Ausrüstung – Abenteuergrundlagen (S. 84–85)
Startcharaktere dürfen alles Vernünftige aus dieser Liste kostenlos nehmen.

| Gegenstand | Preis | Gegenstand | Preis |
|---|---|---|---|
| Rucksack | 2 Dukes | Tagebuch | 3 Dukes |
| Schlafrolle | 1 Duke | Leiter (10 ft) | 2 Dukes |
| Kabel (25 ft, Metall) | 5 Prinzen | Laterne (Licht 25 ft) | 2 Dukes |
| Köcher (2 Schriftrollen/Karten) | 1 Duke | Dietriche | 3 Dukes |
| Kette (10 ft) | 1 Prinz | Lupe | 1 Prinz |
| Kreide | 1 Duke | Metallbehälter | 4 Dukes |
| Holzkohle | 1 Duke | Musikinstrument | 2 Prinzen |
| Truhe | 1 Prinz | Stange (5 ft, Stahl) | 5 Dukes |
| Kleidung (Arbeit) | 3 Dukes | Stange (5 ft, Holz) | 1 Duke |
| Kleidung (Mittelschicht) | 1 Prinz | Seil (25 ft) | 4 Dukes |
| Kleidung (Landadel) | 5+ Prinzen | Rationen (1 Tag) | 2 Dukes |
| Brecheisen | 1 Prinz | Fernrohr | 10 Prinzen |
| Leuchtfackel | 10 Prinzen | Zelt | 2 Prinzen |
| Glasflasche | 1 Duke | Fackel | 1 Duke |
| Wurfanker | 3 Prinzen | Fläschchen (5er-Set) | 3 Dukes |
| Schlauch (10 ft) | 10 Prinzen | Schreibfeder | 1 Duke |

### 5.11 Waffen- & Rüstungspreise (S. 85)

| Waffe | Preis | Waffe | Preis |
|---|---|---|---|
| Leichte Nahkampfwaffe | 1 Prinz | Leichter Bogen | 5 Dukes |
| Mittlere Nahkampfwaffe | 7 Prinzen | Mittlerer Bogen | 1 Prinz |
| Schwere Nahkampfwaffe | 15 Prinzen | Schwerer Bogen | 5 Prinzen |
| Überschwere Nahkampfwaffe | *nicht aufgeführt* | Überschwerer Bogen | 17 Prinzen |
| Leichte Schusswaffe | 2 Prinzen | Leichte Armbrust | 2 Prinzen |
| Mittlere Schusswaffe | 5 Prinzen | Mittlere Armbrust | 4 Prinzen |
| Schwere Schusswaffe | 12 Prinzen | Schwere Armbrust | 7 Prinzen |
| Überschwere Schusswaffe | 20 Prinzen | Überschwere Armbrust | 14 Prinzen |

Preise für Rüstungen/Schilde: siehe §5.7 und §5.8.

### 5.12 Gegenstände zum Verkauf (S. 86–87, Markengegenstände)

| Gegenstand | Preis | Effekt | Tags |
|---|---|---|---|
| Elympia Dark (Dunkelbier) | 4 Pr/Glas, 40 Pr/Flasche (10 Gläser) | Eines der beliebtesten Getränke in Evangless: Dieses von Satyrn gebraute dunkle Lagerbier hebt jedem die Stimmung. Sein vollmundiger Geschmack stellt 4 Trefferpunkte pro Glas wieder her. Eine Flasche enthält 10 Gläser. Das Trinken kostet 1 AP pro Glas. Bitte trinke verantwortungsvoll. | `[ACTION]` |
| CRIMSON (Kleidungslinie) | 30 Pr | von Crimson Marshal Lucinda Mirasol. Diese umstrittene Modelinie des berüchtigten evanglessianischen Militaristen verdankt ihren Namen nicht bloß dem Rang ihrer Schöpferin; kein Stück kann bei Feuer der Stufe 1 Feuer fangen! Diese Kleidung zählt als minimale Rüstung und sieht garantiert zu jeder Jahreszeit absolut schneidig aus. | `[GEAR] armor=minimal` |
| Mindcuffs | 3 Pr | Entwickelt vom Dolby Home for the Scientifically Unstable; diese Handschellen können für Griffe mit einem Aktionspunkt benutzt werden. Sie lassen sich an höchstens zwei Körperteilen anbringen; gegriffene Hände oder Beine werden unbrauchbar. Perfekt, um jedes weltuntergangsmaschinenbesessene böse Genie am Bauen zu hindern: Das Ziel kann ein Körperteil nur befreien, indem es einen Widerstand Kraft der Stufe 2 schafft oder der Besitzer der Handschellen sie löst. | `[ACTION]` |
| Wasserfilter | 15 Pr | Ein unverzichtbares Gerät für Safarijäger und Wüstenplünderer gleichermaßen: Dieses praktische Werkzeug lässt sich an jede Feldflasche oder Flasche anbringen. Einfach umkippen, und alle Verunreinigungen laufen heraus, sodass nur das sauberste Wasser zurückbleibt. Es kann 15-mal benutzt werden, bevor es kaputtgeht, und ist verbergbar. | `[NARR]` |
| Any-Altitude Parachute | 4 Pr | Dieser hochmoderne Fallschirm von Spendo öffnet sich schnell für einen reflexiven Aktionspunkt, wann immer du fällst. Nie wieder Fallschaden! Er ist zwar nicht verbergbar, doch sein mehrstufiger Auslöseprozess schützt dich, ob du 5 Fuß oder 500 Fuß fällst! SPENDO-BRAND: 91,6 % GARANTIERT! | `[REFLEX]` |
| Spendo-Granate | 3 Pr | Manchmal muss man einfach etwas in die Luft jagen. Spendo versteht das. Deshalb hat er die Spendo-Granate erschaffen. Diese verbergbare Bombe ist eine Statuette des Gnoms Spendo höchstpersönlich (wenn Spendo nach Schießpulver röche, dunkelgrüne Haut und Kleidung hätte und tickende Geräusche wie eine Bombe machte). Das Aktivieren der Bombe kostet 1 Aktionspunkt, das Werfen 2 Aktionspunkte. Sie explodiert zu Beginn deines nächsten Zuges. Sie verursacht 10 Schaden bei allen im Zielfeld und in allen angrenzenden Feldern. Wer sich in diesen Feldern befindet, kann 1 Aktionspunkt ausgeben, um mit seinem Geschick der bevorstehenden Explosion zu widerstehen. Erzielt er ein Ergebnis von Stufe 2 oder höher, erleidet er keinen Schaden und verlässt den Explosionsbereich. SPENDO-BRAND: 91,6 % GARANTIERT! | `[ACTION]` |
| Spendo-Brand Illumitorch | 2 Pr | Ob du dich vor der Dunkelheit fürchtest oder einfach nichts darin siehst, der Gnom Spendo hat die perfekte Lösung! Fackeln sind heiß und können dich verbrennen; das ist gefährlich! Nimm stattdessen Spendos Illumitorches! Leicht mit einer Hand zu führen und verbergbar, bestehen Spendos Illumitorches aus kleinen handbetriebenen Glühbirnen, die Licht 25 Fuß um sich herum werfen. SPENDO-BRAND: 91,6 % GARANTIERT! | `[NARR]` |
| Der Rasen-Verformer (Kettensäge) | 32 Pr | Spendo präsentiert sein neuestes Produkt aus seiner Reihe von Landschaftsgärtnerei-Werkzeugen. Diese schicke Kettensäge, entworfen für Selbstjustiz-Gärtner, funktioniert als mittlere Waffe. Immer wenn du einen Gegner erfolgreich triffst, kannst du einen Aktionspunkt ausgeben, um ihm durch Drehen der Sägeblätter 1 nicht absorbierbaren Schaden zuzufügen. Das kannst du so oft tun, wie du während deines aktuellen Zuges noch Aktionspunkte hast. SPENDO-BRAND: 91,6 % GARANTIERT! | `[GEAR]` |
| Gas-Fabulous (Gasmaske) | 4 Pr | Nach einem Entwurf der Kohlenstaub-Gewerkschaften von Evangless verleiht diese praktische Gasmaske ihrem Träger +4 auf Widerstände gegen alchemistische Gase. Aber bei denen solltest du nicht kaufen, oh nein! Kauf deine Gasmaske bei Spendo, und seine fleißigen Handwerker passen das Aussehen der Maske kostenlos an! SPENDO-BRAND: 91,6 % GARANTIERT! | `[COND]` |
| Schutzbrille | 10 Pr | Spendo mag keinen Dreck in den Augen. Du solltest das auch nicht! Diese praktische Industriebrille schützt dich vor Schmutz und anderen Dingen! Sie gewährt dir +1 auf deine Schutzklasse gegen gezielte Angriffe auf deine Augen und +3 auf Widerstände Kraft gegen alles, was deine Augen beeinträchtigen würde. SPENDO-BRAND: 91,6 % GARANTIERT! | `[COND]` |
| Enterhakenpistole | 6 Pr | Perfekt für den flüchtenden Gentleman-Dieb: Diese Enterhakenpistole schießt bis zu 50 Fuß Kette, Seil oder Kabel und haftet an felsigen, magnetischen, rauen oder glatten Oberflächen. Sie erhöht dein Klettertempo um 20 Fuß, während du das Seil zu seiner Halterung einholst. Das Abfeuern kostet 1 Aktionspunkt, das Lösen 1 Aktionspunkt und das Einholen zum Klettern 1 Aktionspunkt. Aber Vorsicht: Dieses Schmuckstück ist nicht verbergbar. MaskedMen Inc. Unleash Your Inner Rogue! | `[GEAR]` |
| Sicherheitsketten | 10 Pr | Auf vielfachen Wunsch zurück: Red-Gate Security präsentiert stolz die Sicherheitsketten! An jedem Gegenstand anbringbar, kann eine einzelne Kette einen Gegenstand an den Händen seines Besitzers sichern und gewährt dem Träger +2 auf Widerstände dagegen, entwaffnet zu werden. reD-gate: Keeping Evangless Safe | `[COND]` |
| Getönte Brille | 10 Pr | Standardausgabe der evanglessianischen Militärpolizei: Diese stilvollen Brillenkunstwerke von Red-Gate Security schützen deine Augen vor den schädlichen Strahlen der Sonne ebenso wie vor Lichtblitzen. Beim Tragen erhältst du +3 auf den Widerstand dagegen, von Lichtblitzen geblendet zu werden. reD-gate: Keeping Evangless Safe | `[COND]` |
| Wärmesicht-Monokel | 10 Pr | Du steckst mitten in einer Kneipenschlägerei. Dein auserkorener Gegner kippt einen Tisch auf die Seite und duckt sich dahinter. Deine Neugier ist geweckt. Was macht er da hinten? Mit einem Wärmesicht-Monokel von MaskedMen Incorporated könntest du seine Wärmesignatur sehen, klar wie der Tag! Dieses praktische Monokel lässt dich Wärme durch alles hindurch sehen, was als dürftige Deckung gilt. MaskedMen Inc. Unleash Your Inner Rogue! | `[COND]` |
| Hidden Intentions (Gift) | 8 Pr/Dosis | Bei MaskedMen Incorporated glauben wir, dass Feingefühl die größte Waffe im Arsenal jedes Gentlemans ist. Gib einfach eine Dosis Hidden Intentions in das Essen oder Getränk deines Ziels. Da ein Widerstand List der Stufe 3 nötig ist, um die zugesetzte Zutat in der Mahlzeit zu bemerken, erleidet dein Ziel etwa 6 Sekunden oder drei Aktionspunkte nach dem Verzehr 6 nicht absorbierbaren Schaden. MaskedMen Inc. Unleash Your Inner Rogue! | `[ACTION]` |
| Reasonable Doubt (automatischer Dietrich) | 8 Pr | Das Premiumprodukt von MaskedMen Incorporated: Dieses automatisierte Dietrichgerät hält das Schloss fingerabdruckfrei. Es gibt 1 Aktionspunkt für das Knacken jedes Schlosses aus, an dem es angebracht ist, immer wenn deine Aktionspunkte aufgefrischt werden. Einhändig und verbergbar: Du kannst es für 1 Aktionspunkt an einem Schloss anbringen oder für 2 Aktionspunkte darauf werfen. MaskedMen Inc. Unleash Your Inner Rogue! *Obwohl es Gerüchte über die Legitimität und Moral von MaskedMen Incorporated gibt, waren alle ihre Agenten uns gegenüber sehr aufrichtig und geben uns keinen Grund, die Rechtmäßigkeit ihres Unternehmens anzuzweifeln. | `[ACTION]` |
| Graviton-Brett | 85 Pr | Ein kleines Schwebebrett, perfekt für alle, die stilvoll reisen wollen: Dieser Premium-Clanker von Burgenhind Industries fliegt vielleicht nicht durch die Luft, aber er gleitet schnell über Land und die Wasseroberfläche! Mit einem Tempo von 40 Fuß pro Aktionspunkt und 12 Wunden (bei jedem Schaden verliert es 5 Fuß Tempo) wirst du der Neid aller Fußgänger auf deinem Weg sein! Burgenhind Industries: Need a Lift? | `[GEAR] vehicle` |
| Die Modische Ankunft (Flugpack) | 3.200 Pr | Das Neueste an persönlichen Transport-Clankern von Burgenhind Industries: Dieses von einer Graviton-Sphäre angetriebene Pack hat eine stilvolle Messingoberfläche und passt bequem auf den Rücken jedes Gehrocks oder Korsetts. Für jeden Aktionspunkt, den du für seine Bewegung ausgibst, fliegt die Modische Ankunft bis zu 40 Fuß. Es hat 12 Wunden und verliert bei Schaden 5 Fuß Bewegung. Wer nicht modisch ankommt, warum dann überhaupt erscheinen? Burgenhind Industries: Need a Lift? | `[GEAR] Fly 40` |

---
