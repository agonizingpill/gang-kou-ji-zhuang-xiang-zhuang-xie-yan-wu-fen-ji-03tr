"""门槛核心规则的单测：只依赖标准库，python3 -m unittest 即可运行。"""

import unittest

from src.thresholds import (
    PUBLISHED,
    WITHDRAWN,
    dispatchable_levels,
    effective_version,
    evaluate,
    next_version,
)


class EffectiveVersionTest(unittest.TestCase):
    def test_no_versions(self):
        self.assertIsNone(effective_version([]))

    def test_single_published(self):
        self.assertEqual(effective_version([(1, PUBLISHED)]), 1)

    def test_latest_published_wins(self):
        rows = [(1, PUBLISHED), (2, PUBLISHED), (3, PUBLISHED)]
        self.assertEqual(effective_version(rows), 3)

    def test_withdraw_current_falls_back_to_previous(self):
        # 夜班调高后撤回，白班标准版本恢复生效
        rows = [(1, PUBLISHED), (2, WITHDRAWN)]
        self.assertEqual(effective_version(rows), 1)

    def test_all_withdrawn_means_no_threshold(self):
        rows = [(1, WITHDRAWN), (2, WITHDRAWN)]
        self.assertIsNone(effective_version(rows))

    def test_withdraw_shadowed_version_keeps_current(self):
        rows = [(1, WITHDRAWN), (2, PUBLISHED)]
        self.assertEqual(effective_version(rows), 2)


class NextVersionTest(unittest.TestCase):
    def test_first_version(self):
        self.assertEqual(next_version([]), 1)

    def test_increments_max(self):
        self.assertEqual(next_version([1, 3, 2]), 4)


class EvaluateTest(unittest.TestCase):
    def test_no_threshold_always_classified(self):
        self.assertEqual(evaluate(0.01, None), "classified")

    def test_confidence_above_threshold(self):
        self.assertEqual(evaluate(0.9, 0.6), "classified")

    def test_confidence_equal_to_threshold_passes(self):
        self.assertEqual(evaluate(0.6, 0.6), "classified")

    def test_confidence_below_threshold_goes_to_review(self):
        self.assertEqual(evaluate(0.59, 0.6), "review")


class DispatchableLevelsTest(unittest.TestCase):
    def test_classified_case_dispatches_at_final_level(self):
        self.assertEqual(dispatchable_levels("classified", "major"), ["major"])

    def test_dispatched_case_keeps_level(self):
        self.assertEqual(dispatchable_levels("dispatched", "watch"), ["watch"])

    def test_review_case_not_dispatchable(self):
        self.assertEqual(dispatchable_levels("review", None), [])

    def test_failed_case_not_dispatchable(self):
        self.assertEqual(dispatchable_levels("failed", None), [])

    def test_classified_without_level_not_dispatchable(self):
        self.assertEqual(dispatchable_levels("classified", None), [])


if __name__ == "__main__":
    unittest.main()
