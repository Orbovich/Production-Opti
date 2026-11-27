import argparse
import json
import sys

from production_opti.agent import FoodProductionAgent, IncidentReport


def build_report(args: argparse.Namespace) -> IncidentReport:
    if args.input:
        with open(args.input, "r", encoding="utf-8") as source:
            data = json.load(source)
        return IncidentReport(**data)

    measurements = {}
    if args.measurement:
        for item in args.measurement:
            name, value = item.split("=", 1)
            measurements[name.strip()] = float(value)

    return IncidentReport(
        situation=args.situation,
        process_line=args.process_line,
        current_value=args.quantity,
        baseline_value=args.baseline,
        unit=args.unit,
        occurrences=args.occurrences,
        known_duration_minutes=args.duration,
        waste_rate_percent=args.waste,
        safety_or_quality_risk=args.safety_risk,
        measurements=measurements,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Production Opti decision-support agent"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    assess = subparsers.add_parser("assess")
    assess.add_argument("--input", help="Path to a JSON incident report")
    assess.add_argument("--situation", default="")
    assess.add_argument("--process-line", default="Unknown")
    assess.add_argument("--quantity", type=float)
    assess.add_argument("--baseline", type=float)
    assess.add_argument("--unit", default="units")
    assess.add_argument("--occurrences", type=int, default=1)
    assess.add_argument("--duration", type=float)
    assess.add_argument("--waste", type=float)
    assess.add_argument("--safety-risk", action="store_true")
    assess.add_argument("--measurement", action="append")

    args = parser.parse_args()
    report = build_report(args)
    assessment = FoodProductionAgent().assess(report)
    json.dump(assessment.to_dict(), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
