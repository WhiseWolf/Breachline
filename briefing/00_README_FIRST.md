# Einstieg — aktiver Agentenbetrieb
Stand: 2026-10-09. Die früheren Windows-/Ubuntu-Installationshinweise sind historisch; sie blockieren keinen bereits eingerichteten Betrieb.
## Ablage und Pfade
Aktuell beobachtete lokale Struktur:
- Workspace: /home/pagi/breachline-agent
- Aktive Offline-Briefings: /home/pagi/breachline-agent/briefing
- Aktive Offline-Logs: /home/pagi/breachline-agent/logs
- Git-Checkout: /home/pagi/breachline-agent/repo, Branch agent-lab
- briefing/ und logs/ im Checkout sind derzeit Kopien, keine automatisch synchronisierten Verzeichnisse.
Prüfe beim Start die tatsächlich verwendeten Pfade. Nie aus dem aktuellen Arbeitsverzeichnis auf die Quelle schließen. Nicht aus beiden Log-Kopien parallel einen Zustand zusammenmischen.
## Start
Lies zuerst 00_CONSTITUTION.md, dann AGENT_BRIEFING_FULL.md und alle Pflichtdateien aus agent_config.json. Relative Briefing-Pfade werden relativ zum Ordner dieser Konfigurationsdatei aufgelöst; Log-Pfade relativ zum dort beschriebenen Workspace.
MASTER_SYSTEM_PROMPT.md ist ein Einstiegspunkt, keine zweite Regelkopie.
Dokumentiere erfolgreiche Lesevorgänge und Dateihashes im Laufnachweis. Fehlt eine Datei, suche zuerst den korrekten Pfad. Kein neues Goal erzeugen, solange 01_GOAL.md existiert.
## Fortsetzung
Lies logs/CURRENT_WORK.md. Historische Logs unter logs/archive/ sind keine aktiven Aufträge und keine bestätigten Forschungsergebnisse.
Die Konfiguration beschreibt den gewünschten Vertrag. Ihre Existenz beweist nicht, dass der Runtime-Loader ihn implementiert.

## Neustart von Null — FRESH_DISCOVERY_2026_10_09
Nur die aktiven Logs dieser Mission laden. Archive und frühere Memory-/Scheduler-Aufträge nicht in den neuen Startkontext übernehmen. Nicht alte Konzepte bestätigen oder die frühere 64-%-Behauptung weiterverfolgen.
Ersten Auftrag ausschließlich aus logs/CURRENT_WORK.md übernehmen. Ein echter neuer lokaler Lauf muss nachgewiesen werden; GitHub-Dateireset allein setzt keine Runtime zurück.
