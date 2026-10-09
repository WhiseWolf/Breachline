# Agent Loop — Version 2.1
## 0. Load
Lies alle Pflichtdateien aus agent_config.json und aktive Logs. Pfade gemäß 00_README_FIRST.
Schreibe den Startnachweis gemäß 12_EXECUTION_AND_EVIDENCE. Nicht behaupten, Regeln geladen zu haben, wenn das Lesen nicht gelang.
## 1. Orient
CURRENT_WORK laden. Nur belegte Abschlüsse übernehmen; Archive dienen der Nachprüfung.
## 2. Select
Genau eine konkrete nächste Aktion mit erwartbarem Erkenntniswert auswählen. Abbruch-/Erfolgskriterium vor Ausführung festlegen.
## 3. Preflight
0-€-Budget, Scope, Reversibilität und bestehende Freigaben prüfen.
## 4. Execute
Werkzeug tatsächlich aufrufen; fehlende kostenlose lokale Werkzeuge projektlokal beschaffen und testen.
## 5. Record
Run-ID, Systemzeit, Werkzeug/Eingaben, Exitstatus, Rohdaten-/Artefaktpfade und Unsicherheit speichern.
## 6. Audit
Mindestens stärkstes Gegenargument, alternative Erklärung und Belegprüfung. Audit muss ein dokumentiertes Ergebnis liefern.
## 7. Decide
Geplant/versucht/ausgeführt/geprüft/bestätigt unterscheiden. Gates nur mit Belegen passieren.
## 8. Learn
Prozessänderungen nur gemäß Adaptation Policy; keine erfundenen Baselines.
## 9. Continue
CURRENT_WORK auf einen eindeutigen nächsten Auftrag aktualisieren. Sinnvoll und innerhalb der Freigaben weiterarbeiten.
Falls Runtime endet: tatsächlichen Endstatus dokumentieren; keine automatische Fortsetzung behaupten, solange sie nicht beobachtet wurde.
