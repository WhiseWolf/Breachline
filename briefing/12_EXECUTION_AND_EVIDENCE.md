# Ausführungs- und Evidenzvertrag
## Startnachweis
Für jeden realen Lauf eine eindeutige Run-ID erzeugen. Zeitstempel mit Systemuhr und Zeitzonenoffset/UTC erzeugen.
In logs/runs/<run-id>/manifest.json speichern:
- Runtime/Modell und tatsächlich verwendete Konfiguration, soweit auslesbar
- Workspace, Briefing- und Log-Verzeichnis
- erfolgreich gelesene Pflichtdateien mit SHA-256
- fehlende Dateien und tatsächliche Lesefehler
- Start-/Endzeit und tatsächlicher Status
Dieser Vertrag implementiert keinen Loader oder Scheduler. Wenn die Runtime ihn nicht unterstützt, eine lokale nachweisbare Lösung bauen und testen.
## Aktionen
Aktionen mit Eingaben, Werkzeug, Beginn/Ende, Exitstatus und Artefaktpfad protokollieren. Keine Zugangsdaten aufzeichnen.
Kein Gedankentranskript nötig; beobachtbare Aktionen und Ergebnisse genügen.
## Quellen
URL/Datei, genaue Belegstelle, tatsächliche Abrufzeit, Quellenart und unterstützte Behauptung speichern.
Modellwissen und Konzeptskizzen sind keine abgerufenen Quellen. Nicht abgerufene Links heißen UNVERIFIED.
## Tests
Hypothese, Testcode-/Commitstand, Ausführung, Rohmesswerte, Fehler, Ergebnis und Widerlegungskriterium.
Gameplay-Test: Browser/Version, Start-URL, tatsächliche Inputs, Screenshot/Trace, Konsolenfehler und Messwerte. Build allein ist kein Gameplay-Test.
Technische Tests nicht als Spaß-/Retentionnachweis deklarieren.
## Zustände
PLANNED, ATTEMPTED, EXECUTED, VERIFIED, FAILED, BLOCKED, UNASSESSED.
VERIFIED bedeutet konkret dokumentierte Prüfung; keine automatische Aufwertung durch Text oder Checkbox.
## Git und Kopien
Git-Operationen im verifizierten Checkout ausführen. Nur passende autorisierte Dateien stagen, kein pauschales git add für private Runtime-Daten.
Offline-Dateien und Repo-Kopien explizit synchronisieren; nie automatisch als identisch annehmen.

## Ablage neuer Spiele
Agentensteuerung: Checkout <workspace>/repo, Git-Branch agent-lab. Spielentwicklung: Git-Branch game/<spiel-slug> von main in einem separaten Git-Worktree, bevorzugte Worktree-Wurzel <workspace>/worktrees/<spiel-slug>. Innerhalb dieses Spiel-Worktrees lautet der relative Dateipfad games/<spiel-slug>/index.html. game/<spiel-slug> ist ein Branchname, kein Spiel-Dateipfad. Bestehende Worktrees und Prototypen zuerst mit tatsächlichen Dateien und git worktree list abgleichen; keine vorhandenen Varianten erneut erzeugen oder löschen. Bereits vorhandenen passenden Spiel-Worktree verwenden, wenn dessen Branch/Basis belegt sind.

Geprüfte Spiel-Dateien gezielt nach main übernehmen gemäß 13_AUTHORIZATIONS.md. Bestehende Spiele und URLs erhalten. Keinen Gesamtmerge von agent-lab nach main ausführen; den laufenden Steuerungs-Checkout nicht umschalten. Branch, absoluter Worktree-Pfad, relativer Spielpfad, Teststand, Commit und ausgelieferte URL in den aktiven Logs belegen. Branches sind keine eigenen Pages-Websites: die bestehende Pages-Quelle prüfen und Spiele über getrennte Pfade veröffentlichen.

## Fachliche Übergabe und Ausführungsergebnis
CURRENT_WORK enthält den tatsächlich erreichten Stand mit genauem Artefaktpfad/Testbeleg, wesentliche offene Prüfung und genau eine nächste ausführbare Aktion. Nach Schreiben eines Prototyps zuerst den vorhandenen Stand testen; nach einem Test dessen Ergebnis übernehmen. Die gleiche Datei nicht im nächsten Zyklus neu initialisieren.
Scheduler-Checkpoints und runtime_handoff.json sichern technische Evidenz, ersetzen aber keine fachliche Übergabe oder Gate-Abnahme. HANDOFF_REQUIRED bedeutet: vorhandene Runtime-Belege und aktuelle Dateien abgleichen und den fachlichen CURRENT_WORK-Stand nachholen, bevor weitere Varianten gebaut werden.
Ein Werkzeugaufruf ist kein Prozess- oder Produkterfolg. Exitcode ungleich 0, widersprüchliche Statusangaben oder Timeout niemals als erfolgreichen Git-/Testschritt übernehmen. Bei unklaren Schreibwirkungen tatsächlichen Zustand prüfen; nicht blind wiederholen. Eine Datei zurückzulesen ist kein ausgeführter Gameplay-Test.

