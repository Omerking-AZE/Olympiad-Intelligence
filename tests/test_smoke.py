import unittest

from src.student_rating import (
    calculate_data_confidence,
    calculate_effective_skill,
    calculate_consistency_score,
)


class TestStudentRating(unittest.TestCase):
    def test_data_confidence_is_zero_without_attempts(self):
        self.assertEqual(calculate_data_confidence(0), 0)

    def test_data_confidence_caps_at_one(self):
        self.assertEqual(calculate_data_confidence(20), 1)
        self.assertEqual(calculate_data_confidence(30), 1)

    def test_effective_skill_shrinks_small_samples_toward_neutral(self):
        self.assertEqual(calculate_effective_skill(95, 0), 55)
        self.assertGreater(calculate_effective_skill(95, 10), 55)
        self.assertLess(calculate_effective_skill(95, 10), 95)

    def test_consistency_returns_neutral_without_attempts(self):
        self.assertEqual(calculate_consistency_score(0, 0), 50.0)

    def test_consistency_is_bounded(self):
        self.assertGreaterEqual(calculate_consistency_score(10, 0), 0)
        self.assertLessEqual(calculate_consistency_score(10, 10), 100)


if __name__ == "__main__":
    unittest.main()
