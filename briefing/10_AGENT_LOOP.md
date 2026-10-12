# Agent Loop — Version 2.3
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
Nach jedem überprüfbaren Arbeitsschritt CURRENT_WORK fachlich aktualisieren: genauer Artefakt-/Teststand, Ergebnis, offene Prüfung, eine nächste Aktion. Der Scheduler archiviert zusätzlich die Historie und erhält beim Kontextwechsel die zuletzt abgeschlossene Tool-Austauschfolge sowie belegte Aktions-/Artefaktverweise. Diese technische Sicherung bestätigt keinen fachlichen Abschluss. Bei HANDOFF_REQUIRED zuerst die gespeicherten Runtime-Belege mit aktuellen Dateien abgleichen und den fachlichen Fortsetzungsstand nachholen. Bereits erstellten Code testen/verbessern, nicht erneut in einem anderen Ordner erzeugen. Regeln und Nutzeranweisungen bleiben erhalten.
Falls Runtime endet: tatsächlichen Endstatus dokumentieren; keine automatische Fortsetzung behaupten, solange sie nicht beobachtet wurde.

## Fortsetzung und fachliche Abnahme
Bei jedem Zyklus CURRENT_WORK am tatsächlich geladenen aktuellen Briefing prüfen. Selbst gesetzte Zahlenziele bei Bedarf durch inhaltliche Kriterien gemäß 03_RESEARCH_PROTOCOL ersetzen; Änderung begründen, belegte Ergebnisse erhalten. Ein Briefing-Update initialisiert die Mission nicht erneut.

In Audit/Decide prüfen, welche Aussage neu belegt/widerlegt wurde und ob das passende Gate erfüllt ist. CURRENT_WORK knapp halten: geprüfter Stand mit Belegpfaden, wesentliche Unsicherheit, genau eine nächste ausführbare Aktion mit beobachtbarem Erfolg-/Abbruchkriterium. Eine Arbeitsportion oder ein Lauf darf enden, ohne die Forschungsphase abzuschließen.

BLOCKED/NEEDS_USER nur auf eine tatsächlich blockierte Aktion und notwendige Nutzerhilfe beziehen. Forschungsunsicherheit, optionale Werkzeuge oder erreichte Mengen blockieren die Gesamtmission nicht. Wenn keine sinnvolle erlaubte unabhängige Arbeit verbleibt, mit geprüftem Grund warten.

## Von Prototypen zu echten Spielertests
Sobald ein kleines Testziel sinnvoll und technisch spielbar ist, die GitHub-Pages- und organische Social-Freigabe in 13_AUTHORIZATIONS.md nutzen. Nicht auf menschliche Retention warten, bevor erste Spieler eingeladen werden: Gate C begrenzt den größeren Ausbau, nicht den kleinen Test, der die fehlenden Daten erst liefern soll.
Vorab Hypothese, getestete Version, Messbarkeit und Beobachtungszeitpunkt festlegen. Testseite prüfen, geeigneten ehrlichen Testaufruf veröffentlichen, tatsächliche Auslieferung kontrollieren und verfügbare Daten später auswerten. Plattformzugriff ist nachzuweisen; geplante Beiträge nicht als veröffentlicht führen.
Keine Spieler bedeutet NO_PLAYER_DATA. Auffindbarkeit/Reichweite, technischen Zugang und Spielerwert getrennt prüfen. Während einer sinnvollen Beobachtungsfrist unabhängige erlaubte Arbeit fortsetzen; keine wiederholten Modellzyklen nur zum Nachsehen und keine künstliche Postingquote. Nach tatsächlichem Feedback begründet verbessern, erneut testen oder verwerfen.

