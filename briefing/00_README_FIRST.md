# Offline-Handoff für den lokalen Game-Agenten

Dieses Paket ist dafür gedacht, nach der Ubuntu-Installation ohne Copy/Paste aus ChatGPT weiterarbeiten zu können.

## Ziel
Die Agentenregeln sind dauerhaft als Dateien gespeichert. Der lokale Agent soll sie bei jedem Start erneut lesen, statt sich auf einen einmaligen Prompt oder Chat-Verlauf zu verlassen.

## Empfohlene Ablage vor dem Neustart
Kopiere die ZIP-Datei zusätzlich auf eine vorhandene NTFS-Datenpartition, z. B.:

`G:\BreachlineAgentPack\`

Nicht nur auf den Ubuntu-Installationsstick legen.

## Nach dem ersten Ubuntu-Login
Noch nichts autonom starten. Zuerst Netzwerk, NVIDIA-Treiber, Ollama und Laufzeitumgebung gemeinsam sauber einrichten.

Der lokale Agent soll beim Start mindestens diese Dateien lesen:

1. `AGENT_BRIEFING_FULL.md`
2. `01_GOAL.md`
3. `02_OPERATING_RULES.md`
4. `03_RESEARCH_PROTOCOL.md`
5. `04_EVIDENCE_AND_GATES.md`
6. `05_AUTONOMY_AND_ESCALATION.md`

`07_CURRENT_HANDOFF.md` beschreibt den aktuellen technischen Stand des Test-PCs.


## Version 2.0 – wichtige Änderung

Vor jedem Agentenstart muss `00_CONSTITUTION.md` als höchste Autorität geladen werden.

Der 0-€-Guardrail ist jetzt absolut:
`ADDITIONAL_COST = 0.00 EUR`

Der Agent darf diesen Wert nicht selbst verändern oder umgehen.

Empfohlene Startreihenfolge:
1. `00_CONSTITUTION.md`
2. `AGENT_BRIEFING_FULL.md`
3. `10_AGENT_LOOP.md`
4. restliche Regel- und Kontextdateien
