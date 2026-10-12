# Startabnahme — Version 2.3
Dies ist ein kurzer ausführbarer Vertrag, kein zusätzlicher Forschungsauftrag.
## Vor dem ersten Werkzeugschritt
- aktive Offline-Dateien stimmen mit dem beabsichtigten GitHub-Stand überein;
- Loader hat den tatsächlichen Kontext aus start_context_order und active_log_files bereitgestellt;
- aktive Mission FRESH_DISCOVERY_2026_10_09; Archive und frühere Memory-/Scheduler-Aufträge nicht im Startkontext;
- Run-ID/Systemzeit und erfolgreich gelesene Dateihashes erzeugt; der Hash allein beweist nicht, dass der Modellaufruf den Inhalt erhalten hat;
- mindestens Dateilesen/-schreiben und ein für den gewählten Schritt geeignetes Recherche-/Ausführungswerkzeug sind tatsächlich verfügbar.
Ein Kontextpaket auf der Festplatte zählt nicht als an das Modell übergeben. Bei zu kleinem Kontextfenster Pflichtregeln nicht still abschneiden; nachweisbar phasenweise laden und aktuelles Hand-off erhalten.
## Erfolg des ersten Zyklus
Mindestens eine konkrete Quelle tatsächlich abgerufen oder ein sinnvoller lokaler Test tatsächlich ausgeführt; dazu Beleg, Gegenprüfung und aktualisierter nächster Auftrag.
Ein sauberer Testzyklus muss nicht den ganzen ersten Rechercheplan abschließen.
## Fortsetzung
Zweiter Zyklus übernimmt den aktualisierten CURRENT_WORK ohne erneute Initialisierung, Rückgriff auf Archive oder Wiederholung eines bereits geprüften Schritts ohne Grund.
Bei nicht erfülltem technischen Kriterium tatsächlichen Fehler erfassen. Nicht die Gesamtmission wegen eines fehlenden optionalen Tools stoppen.
## Kein Nachweis durch Dokumentenaudit
Der GitHub-Audit prüft Dokumente. Lokale Loader-/Scheduler-/Memory-Abnahme wurde noch nicht ausgeführt.

## Abnahme nach Briefing-Updates
Der nächste Kontextnachweis muss die tatsächlich geladenen neuen Briefing-Dateihashes zeigen; aktive Logs und Mission erhalten. Fachliche Abnahme gemäß 03_RESEARCH_PROTOCOL ist ein eigener Nachweis: Werkzeug-/Dateierfolg oder Konzeptanzahl allein reichen nicht.

## Fortschrittsabnahme nach Systemaudit 2026-10-12
Zwei tatsächliche aufeinanderfolgende Zyklen müssen einen konkreten Artefakt-/Teststand fortsetzen, statt ihn neu zu initialisieren. CURRENT_WORK muss fachlich aktualisiert sein; Runtime-Checkpoint-Text zählt dafür nicht. HANDOFF_REQUIRED bleibt sichtbar, bis diese Übergabe erfolgt ist. Exitcode und Werkzeugstatus müssen konsistent sein; der Steuerungs-Checkout bleibt auf agent-lab. Mock-Tests allein bestätigen keinen erfolgreichen lokalen Ollama-/Browser-Betrieb. Kein Logreset und keine größeren Limits als Ersatz für diese Abnahme.
