# AGENT LOOP

Dies ist die Standard-Arbeitsschleife.

## 0. Load
Bei jedem Start lesen:
1. `00_CONSTITUTION.md`
2. `01_GOAL.md`
3. `02_OPERATING_RULES.md`
4. `03_RESEARCH_PROTOCOL.md`
5. `04_EVIDENCE_AND_GATES.md`
6. `05_AUTONOMY_AND_ESCALATION.md`
7. `08_COST_AND_PREFLIGHT_POLICY.md`
8. `09_ADAPTATION_POLICY.md`
9. aktuelle Logs / Entscheidungen / Experimente

## 1. Orient
- aktueller Stand,
- stärkste offene Hypothese,
- größtes Informationsdefizit,
- wichtigster möglicher nächster Erkenntnisgewinn.

## 2. Select
Wähle genau den nächsten Schritt mit dem höchsten erwarteten Erkenntnis-/Produktwert bei 0 € Zusatzkosten.

## 3. Preflight
Kosten-, Sicherheits-, Freigabe- und Reversibilitätsprüfung durchführen.

## 4. Execute
Research, Test, Build oder Analyse durchführen.

## 5. Record
Speichere:
- Rohdaten,
- Quellen,
- Interpretation,
- Ergebnis,
- Unsicherheit.

## 6. Audit
Auditor / Red Team prüft:
- Halluzinationen,
- schwache Quellen,
- alternative Erklärungen,
- Confirmation Bias,
- Breachline-Bias,
- unnötige Komplexität,
- versteckte Kosten,
- falsche Kausalität.

## 7. Decide
- weiter,
- verwerfen,
- iterieren,
- neuen Test starten,
- Nutzerinput anfordern.

## 8. Learn
Wenn ein Prozessproblem gefunden wurde:
- Adaptation Policy anwenden,
- Änderung testen,
- gegebenenfalls übernehmen.

## 9. Continue
Wenn kein Nutzerinput nötig ist und ein sinnvoller nächster Schritt existiert:
weiterarbeiten.

Keine künstlichen Stopps.
Keine Endlosschleifen ohne neue Evidenz.
