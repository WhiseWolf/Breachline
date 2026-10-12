# Fortschrittskorrektur nach Systemaudit 2026-10-12

Die geprüfte Ausgangsversion verlor beim Rollen die letzten Tool-Ergebnisse, zählte eigene Checkpoints in current_work_changed und übernahm widersprüchliche Shell-Statusangaben als Erfolg. Wiederholungen und ein falsch umgeschalteter Steuerungs-Checkout sind im privaten Audit belegt.

## Korrigiertes Verhalten
- Fachlicher CURRENT_WORK-Inhalt wird ohne automatisch ergänzten Checkpoint-Abschnitt verglichen. HANDOFF_REQUIRED und strukturierte runtime_handoff.json zeigen fehlende Übergabe; der nächste Zyklus erhält reale Aktions-/Artefaktbelege statt nur Assistant-Absichten. Das ist keine Gameplay- oder Gate-Abnahme.
- Die zuletzt abgeschlossene vollständige Tool-Austauschfolge bleibt nach Kontextrollen erhalten. Nur ältere abgeschlossene Dialoge werden archiviert. Neue Regeln und offene Tool-Protokolle bleiben geschützt.
- Die unveränderte Regel-/Tool-Präfixgröße wird anhand der ersten tatsächlichen Prompt-Nutzung mit 20 Prozent plus 512 Tokens Reserve geplant; neue Historie verwendet weiter die konservative Schätzung. Bei geändertem Präfix oder unerwartet höherer Nutzung wird die Kalibrierung verworfen. Echte Überschreitungen bleiben blockiert.
- Die bestehende registrierte Shell wird unter Beibehaltung ihres Sicherheits-/Executorpfads auf echten Exitstatus geprüft. Widersprüche sind Fehler. Unklare Schreibwirkungen werden nicht automatisch wiederholt. Git-Checkout/Switch-Operationen durch den Scheduler sind blockiert; tatsächlicher Steuerungs-Branch wird vor/nach Shell-Aufrufen kontrolliert.
- Branchname, Worktree-Wurzel und relativer Spielpfad sind im Briefing eindeutig. Bestehende Varianten müssen zuerst inventarisiert und erhalten werden.
- Erkannte Credential-Formate werden in gespeicherten Belegen maskiert; keine Garantie für beliebige unbekannte Geheimnisse. ToolCalls werden strukturiert gespeichert. Runtime-Version und Shell-Quellhash werden dokumentiert; vollständige Modell-/Rust-Build-Provenienz ist damit noch nicht garantiert.
- Voll-Log-Kopien schließen Git-Verwaltungsdaten aus, erhalten aber alle eigentlichen Logs/Runs. Metadaten-Diagnosen verwenden jetzt ebenfalls das private Log-Repository.

## Validierung
72 Standardbibliothek-Tests bestanden, darunter 16 neue Regressionstests für die Audit-Befunde. Die erste Fassung dieser Regressionstests wurde auch gegen die alte Runtime ausgeführt: erwartetes Scheitern mit fünf Assertion-Fehlern und sieben fehlenden neuen Schnittstellen, kein erfolgreicher alter Stand.
Geprüft sind unter anderem zwei aufeinanderfolgende simulierte Agentzyklen, echtes lokales Git-Branch-Verhalten, letzter vollständiger Tool-Dialog, Shell-Exit-Widersprüche, Kontextkalibrierung und sichere Briefing-Übernahme. Keine echte Ollama-/Browser-/Social-Abnahme in dieser Umgebung.

## Lokale Übernahme
Anleitung in runtime/README.md. Alten Scheduler geordnet stoppen, vorhandenen Checkout ohne Reset auf agent-lab zurückbringen, per fast-forward aktualisieren, runtime/sync_briefing.py ausführen und Scheduler neu starten. Helper sichert geänderte Offline-Briefings; unbekannte lokale Änderungen führen vor der Übernahme zum Abbruch. Logs, Mission, Prototypen und config.toml bleiben erhalten.
Ein GitHub-Commit aktualisiert keinen bereits laufenden Python-Prozess. Erfolg auf Ubuntu anhand neuer Manifest-Hashes und zweier realer fortsetzender Zyklen prüfen. Keine größeren Laufgrenzen, keine neuen Cloud-Kosten und kein vollständiger Merge von agent-lab nach main.
