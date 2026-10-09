# COST AND PREFLIGHT POLICY

Vor **jeder** neuen externen Abhängigkeit, Tool-Installation, Account-Nutzung oder Infrastrukturentscheidung muss der Agent einen Preflight durchführen.

## Mandatory Preflight

Prüfe:

1. Kostet diese Aktion jetzt Geld?
2. Kann sie später automatisch Kosten verursachen?
3. Benötigt sie Zahlungsdaten?
4. Ist sie nur zeitlich begrenzt kostenlos?
5. Existiert eine lokale oder dauerhaft kostenlose Alternative?
6. Ist die Aktion reversibel?
7. Verletzt sie einen Constitution-Guardrail?
8. Ist sie überhaupt nötig, um die aktuelle Hypothese zu testen?

## Entscheidung

Wenn 1–4 = JA:
- Aktion blockieren.
- kostenlose Alternative suchen.

Wenn 6 = NEIN oder 7 = JA:
- Aktion blockieren und Nutzer einbeziehen.

Wenn 8 = NEIN:
- Aktion nicht durchführen.

## Cost Ledger

Jede neue Abhängigkeit wird in `logs/COST_LEDGER.md` erfasst mit:
- Datum,
- Tool/Dienst,
- Kostenstatus,
- warum 0 €,
- mögliches zukünftiges Kostenrisiko,
- Ersatzstrategie.

Der erwartete Gesamtwert muss immer bleiben:

`ADDITIONAL_COST = 0.00 EUR`
