# Production Opti

An initial decision-support agent for food production optimization.

Production Opti helps operators:

1. describe a production concern;
2. collect missing evidence;
3. separate transient inconveniences from persistent problems;
4. prioritize safe, practical interventions; and
5. define monitoring and validation steps.

This is a decision-support tool, **not** an authority for food-safety or regulatory decisions. Potential safety issues must be escalated to qualified personnel and applicable procedures.

## Included

- A typed Python domain model
- A deterministic assessment engine for the initial MVP
- A JSON-driven CLI
- Tests for temporary versus persistent classifications and safety escalation

## Run

```bash
python -m production_opti assess \
  --situation "Line 2 output dropped 18% for the third shift" \
  --process-line "Line 2" \
  --quantity 82 \
  --baseline 100 \
  --occurrences 3
```

For structured input:

```bash
python -m production_opti assess --input report.json
```

## Development

```bash
python -m unittest discover -s tests -v
```

## Design principles

- Ask for information only when it can change the decision.
- Escalate safety concerns immediately.
- Prefer evidence and explicit assumptions over certainty.
- Compare observations to an operating baseline.
- Treat uncertainty as uncertainty, not as a temporary condition.
- Never present a recommendation as a substitute for food-safety or regulatory procedures.
