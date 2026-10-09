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
