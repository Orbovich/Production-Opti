import unittest

from production_opti.agent import Classification, FoodProductionAgent, IncidentReport, Severity


class FoodProductionAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = FoodProductionAgent()

    def test_missing_information_is_not_classified_as_problem(self):
        result = self.agent.assess(IncidentReport(situation="Output looks low"))

        self.assertEqual(result.classification, Classification.INSUFFICIENT_DATA)
        self.assertTrue(result.missing_information)

    def test_small_recent_deviation_is_temporary(self):
        result = self.agent.assess(IncidentReport(
            situation="Output dipped briefly",
            current_value=97,
            baseline_value=100,
            known_duration_minutes=20,
            occurrences=1,
        ))

        self.assertEqual(result.classification, Classification.TEMPORARY_INCONVENience)

    def test_repeated_deviation_is_actual_problem(self):
        result = self.agent.assess(IncidentReport(
            situation="Output below target for several shifts",
            process_line="Line 2",
            current_value=82,
            baseline_value=100,
            known_duration_minutes=180,
            occurrences=3,
        ))

        self.assertEqual(result.classification, Classification.ACTUAL_PROBLEM)

    def test_safety_risk_is_immediate_and_critical(self):
        result = self.agent.assess(IncidentReport(
            situation="Temperature alarm",
            safety_or_quality_risk=True,
        ))

        self.assertEqual(result.classification, Classification.ACTUAL_PROBLEM)
        self.assertEqual(result.severity, Severity.CRITICAL)
        self.assertIn("approved", result.recommendations[0].lower())


if __name__ == "__main__":
    unittest.main()
