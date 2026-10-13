# Fehlgeschlagene Git-Inspektion: gezielte Klassifizierung und Wiederaufnahme

Beleg aus dem privaten Log-Snapshot: Der Agent führte git worktree list im Workspace statt im Checkout repo/ aus. Git meldete Exitcode 128, not a git repository. Die Shell-Ausführung war abgeschlossen und rein lesend. Der bisherige konservative Standard klassifizierte jedoch alle shell_exec-Aufrufe als potenziell schreibend und stoppte den Scheduler wegen vermeintlich unklarer Schreibwirkungen.

## Änderung
Eine kleine explizite Allowlist erkennt Git worktree list (optional --porcelain/-z) und ausgewählte rev-parse-Inspektionen. Optionales cd und git -C sind nur mit einfachen absoluten Pfaden erlaubt. Zusätzliche Befehle, Pipelines, Umleitungen, Substitutionen, Skripte und unbekannte Git-Optionen bleiben potenziell schreibend. Keine pauschale Lockerung für shell_exec.

Fehlgeschlagene Inspektionen behalten FAILED und ihren echten Exitcode, blockieren aber keine erlaubte Alternative. Der Agent muss Git im verifizierten Checkout ausführen; START_PROMPT nennt den konkreten -C-Aufruf.

Vorhandene alte Fehlerbelege werden ausschließlich bei exakt gepaarten strukturierten Call/Result-Daten, passender vollständiger Ergebnisdatei, nicht-null/nonzero Exitcode und eindeutiger Aufrufanzahl überprüft. Die Originalreceipts werden nicht geändert; read_only_action_review.json dokumentiert Klassifizierung und Beleg-Hashes. Keine Aktion wird wiederholt. Schreibfehler, fehlende/widersprüchliche Ergebnisse und PENDING bleiben blockiert.

## Validierung und lokale Übernahme
82 Tests bestanden. Außerdem wurde der tatsächlich hochgeladene Fehler-Snapshot in temporären Verzeichnissen durch die Wiederaufnahmeprüfung geprüft; Originalreceipts blieben unverändert. Kein Zugriff auf den Ubuntu-Host und kein echter Ollama-/Gameplay-Test in dieser Umgebung.

Bei bereits gestopptem Scheduler: agent-lab im bestehenden repo/ per git pull --ff-only aktualisieren und den Scheduler neu starten. START_PROMPT wird aus diesem Checkout geladen; für diese Änderung ist keine erneute Offline-Briefing-Kopie nötig. Den fehlgeschlagenen Run und seine Belege erhalten, nicht löschen.

Weitere Beobachtungen: Der neue Scheduler-/Briefing-Stand wurde tatsächlich geladen, die Kontextplanung korrigierte sich nach dem ersten Aufruf, und es gab in diesem Run keinen CONTEXT_ROLL. Ein Datei-Read-back beweist weiterhin kein funktionierendes Gameplay; CURRENT_WORK blieb wegen des vorzeitigen Fehlers fachlich unverändert.
