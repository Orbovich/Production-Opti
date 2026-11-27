from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Iterable


class Severity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Classification(str, Enum):
    INSUFFICIENT_DATA = "insufficient_data"
    TEMPORARY_INCONVENience = "temporary_inconvenience"
    ACTUAL_PROBLEM = "actual_problem"


@dataclass
class IncidentReport:
    situation: str
    process_line: str = "Unknown"
    current_value: float | None = None
    baseline_value: float | None = None
    unit: str = "units"
    occurrences: int = 1
    known_duration_minutes: float | None = None
    waste_rate_percent: float | None = None
    safety_or_quality_risk: bool = False
    measurements: dict[str, float] = field(default_factory=dict)


@dataclass
class Assessment:
    classification: Classification
    severity: Severity
    confidence: float
    summary: str
    evidence: list[str]
    missing_information: list[str]
    possible_causes: list[str]
    recommendations: list[str]
    monitoring: list[str]

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "classification": self.classification.value,
            "severity": self.severity.value,
        }


class FoodProductionAgent:
    """Initial deterministic assessment engine for an operator-facing agent."""

    def assess(self, report: IncidentReport) -> Assessment:
        evidence: list[str] = []
        missing: list[str] = []

        if not report.situation.strip():
            missing.append("A clear description of the situation")

        if report.current_value is None:
            missing.append("Current measured value")
        if report.baseline_value is None:
            missing.append("Baseline or target value")

        if report.known_duration_minutes is None:
            missing.append("How long the condition has been present")

        if report.current_value is not None and report.baseline_value not in (None, 0):
            deviation = ((report.current_value - report.baseline_value) /
                         abs(report.baseline_value)) * 100
            evidence.append(
                f"Measured deviation is {deviation:+.1f}% from the baseline of "
                f"{report.baseline_value:g} {report.unit}."
            )
        else:
            deviation = None

        if report.occurrences > 1:
            evidence.append(
                f"The condition has been observed {report.occurrences} times."
            )

        if report.waste_rate_percent is not None:
            evidence.append(f"Reported waste rate is {report.waste_rate_percent:g}%.")

        if report.safety_or_quality_risk:
            classification = Classification.ACTUAL_PROBLEM
            severity = Severity.CRITICAL
            confidence = 0.99
            summary = (
                "Stop the unsafe or out-of-spec activity according to approved "
                "procedures and escalate immediately. This is not a temporary "
                "condition to self-correct."
            )
            possible_causes = [
                "Equipment or process parameter drift",
                "Incorrect recipe, ingredient, or process setup",
                "Environmental or sanitation condition outside limits",
            ]
            recommendations = [
                "Follow the site safety and food-quality hold/escalation procedure.",
                "Notify the responsible quality, safety, or line lead.",
                "Segregate and document potentially affected product until disposition is approved.",
            ]
            monitoring = [
                "Record affected product and process parameters.",
                "Do not release product until authorized by the responsible quality function.",
            ]
            return Assessment(classification, severity, confidence, summary,
                              evidence, missing, possible_causes,
                              recommendations, monitoring)

        if missing:
            classification = Classification.INSUFFICIENT_DATA
            severity = Severity.MEDIUM if report.occurrences > 1 else Severity.LOW
            confidence = 0.45
            summary = (
                "There is not enough evidence yet to classify this as a real "
                "problem or a temporary inconvenience."
            )
            possible_causes = [
                "Normal short-term process variation",
                "Recent change in equipment, ingredients, schedule, or staffing",
                "Measurement or reporting error",
            ]
            recommendations = [
                "Collect the missing measurements and compare them with the approved operating baseline.",
                "Monitor for a bounded interval using the line's normal operating procedure.",
            ]
            monitoring = [
                "Check whether the deviation repeats at the next agreed measurement interval.",
                "Preserve process and quality records for verification.",
            ]
            return Assessment(classification, severity, confidence, summary,
                              evidence, missing, possible_causes,
                              recommendations, monitoring)

        repeated = report.occurrences >= 3
        large_deviation = deviation is not None and abs(deviation) >= 10
        long_running = (report.known_duration_minutes or 0) >= 60
        waste_concern = (report.waste_rate_percent or 0) >= 5

        actual_problem = repeated or large_deviation or long_running or waste_concern

        if actual_problem:
            classification = Classification.ACTUAL_PROBLEM
            severity = Severity.HIGH if large_deviation or waste_concern else Severity.MEDIUM
            confidence = 0.82 if repeated or long_running else 0.68
            summary = (
                f"The condition on {report.process_line} is likely a real process "
                "problem rather than a harmless short-term fluctuation."
            )
            possible_causes = self._likely_causes(report)
            recommendations = [
                "Verify measurement equipment and the approved baseline.",
                "Check for recent changes in recipe, settings, maintenance, materials, staffing, or schedule.",
                "Correct the highest-confidence root cause using approved operating procedures.",
                "Validate the intervention and keep the change reversible during the test period.",
            ]
            monitoring = [
                "Measure output, waste, and relevant process parameters after the intervention.",
                "Compare results against the approved baseline for at least the next two production periods.",
                "Return to the escalation procedure if the deviation continues or worsens.",
            ]
        else:
            classification = Classification.TEMPORARY_INCONVENience
            severity = Severity.LOW
            confidence = 0.58
            summary = (
                f"The condition on {report.process_line} may be temporary, but it "
                "should be monitored before a major corrective action is made."
            )
            possible_causes = [
                "Short-term process variation",
                "Transient staffing, material, or scheduling change",
                "Minor measurement timing or sampling variance",
            ]
            recommendations = [
                "Avoid a permanent or costly change based on this evidence alone.",
                "Confirm the operating settings and complete normal monitoring.",
                "Escalate if the deviation repeats or exceeds agreed limits.",
            ]
            monitoring = [
                "Take another measurement after one normal production cycle.",
                "Record whether output, waste, and quality indicators return to baseline.",
            ]

        return Assessment(classification, severity, confidence, summary,
                          evidence, missing, possible_causes,
                          recommendations, monitoring)

    @staticmethod
    def _likely_causes(report: IncidentReport) -> list[str]:
        causes = [
            "Process parameters outside the approved operating range",
            "Recent change in ingredients, settings, maintenance, or staffing",
            "Equipment, tooling, or automation drift",
        ]
        causes.extend(
            f"Measurement context: {name}={value:g}"
            for name, value in report.measurements.items()
        )
        return causes
