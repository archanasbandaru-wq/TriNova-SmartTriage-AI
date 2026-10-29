
import unittest

from input_validation import validate_patient


VALID = {
    "age": 35,
    "complaint": "Mild headache",
    "pulse": 80,
    "spo2": 98,
    "systolic": 120,
    "diastolic": 80,
    "temperature": 37.0,
}


def check_patient(**changes):
    data = {**VALID, **changes}
    return validate_patient(**data)


class TestInputValidation(unittest.TestCase):

    def test_valid_patient(self):
        result = check_patient()
        self.assertTrue(result.can_predict)

    def test_negative_age(self):
        result = check_patient(age=-5)
        self.assertFalse(result.can_predict)
        self.assertTrue(any("age:" in e for e in result.errors))

    def test_nonnumeric_age(self):
        result = check_patient(age="abc")
        self.assertFalse(result.can_predict)

    def test_impossible_temperature(self):
        result = check_patient(temperature=96.0)
        self.assertFalse(result.can_predict)

    def test_high_spo2(self):
        result = check_patient(spo2=150)
        self.assertFalse(result.can_predict)

    def test_negative_spo2(self):
        result = check_patient(spo2=-10)
        self.assertFalse(result.can_predict)

    def test_missing_pulse(self):
        result = check_patient(pulse=None)
        self.assertFalse(result.can_predict)

    def test_missing_blood_pressure(self):
        result = check_patient(systolic=None, diastolic=None)
        self.assertFalse(result.can_predict)

    def test_empty_complaint(self):
        result = check_patient(complaint="   ")
        self.assertFalse(result.can_predict)

    def test_nan(self):
        result = check_patient(pulse=float("nan"))
        self.assertFalse(result.can_predict)

    def test_infinity(self):
        result = check_patient(spo2=float("inf"))
        self.assertFalse(result.can_predict)

    def test_suspicious_blood_pressure(self):
        result = check_patient(systolic=190)
        self.assertFalse(result.can_predict)
        self.assertTrue(result.warnings)

    def test_suspicious_pulse(self):
        result = check_patient(pulse=145)
        self.assertFalse(result.can_predict)
        self.assertTrue(result.warnings)

    def test_invalid_bp_relationship(self):
        result = check_patient(systolic=80, diastolic=100)
        self.assertFalse(result.can_predict)


if __name__ == "__main__":
    unittest.main()
