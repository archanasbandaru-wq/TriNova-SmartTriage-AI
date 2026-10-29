
import unittest

from safety_rules import number, safety_check


class TestSafetyRules(unittest.TestCase):

    def test_normal_vitals(self):
        result = safety_check(
            age_years=30,
            spo2=98,
            pulse=80,
            systolic=120,
            diastolic=80,
            temperature=37,
        )
        self.assertEqual(result["minimum_urgency_level"], 5)
        self.assertFalse(result["needs_nurse_review"])

    def test_critical_low_oxygen(self):
        result = safety_check(age_years=45, spo2=82)
        self.assertEqual(result["minimum_urgency_level"], 1)

    def test_low_oxygen(self):
        result = safety_check(age_years=45, spo2=89)
        self.assertEqual(result["minimum_urgency_level"], 2)

    def test_moderately_low_oxygen(self):
        result = safety_check(age_years=45, spo2=93)
        self.assertEqual(result["minimum_urgency_level"], 3)

    def test_critical_low_blood_pressure(self):
        result = safety_check(age_years=50, systolic=75)
        self.assertEqual(result["minimum_urgency_level"], 1)

    def test_severe_pregnancy_blood_pressure(self):
        result = safety_check(
            age_years=28,
            pregnant=True,
            systolic=165,
            diastolic=112,
        )
        self.assertEqual(result["minimum_urgency_level"], 2)

    def test_infant_fever(self):
        result = safety_check(
            age_years=0.1,
            age_months=1.2,
            temperature=38.5,
        )
        self.assertEqual(result["minimum_urgency_level"], 2)

    def test_invalid_age_requires_review(self):
        result = safety_check(age_years=-5, spo2=98)
        self.assertTrue(result["needs_nurse_review"])

    def test_invalid_oxygen_requires_review(self):
        result = safety_check(age_years=30, spo2=150)
        self.assertTrue(result["needs_nurse_review"])

    def test_invalid_number(self):
        self.assertIsNone(number("invalid"))
        self.assertIsNone(number(float("nan")))

    def test_fahrenheit_conversion(self):
        result = safety_check(age_years=30, temperature=104)
        self.assertEqual(result["minimum_urgency_level"], 3)
        self.assertIn(
            "Temperature converted from Fahrenheit",
            result["reasons"],
        )


if __name__ == "__main__":
    unittest.main()
