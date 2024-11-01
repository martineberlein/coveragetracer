import unittest
from pathlib import Path

from coverageanalyzer.coverageanalyzer import CoveragePyAnalyzer, CoverageReport

# Set up paths for the dummy project and test harness
PROJECT_ROOT = Path.cwd() / "resources" / "project"
HARNESS_PATH = Path.cwd() / "resources" / "harness.py"


class TestCoveragePyAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up a fresh CoveragePyAnalyzer instance before each test."""
        self.analyzer = CoveragePyAnalyzer(
            project_root=PROJECT_ROOT,
            harness=HARNESS_PATH
        )

    def test_initial_coverage_run(self):
        """Test that initial coverage analysis runs correctly and returns a CoverageReport."""
        tests = ["sqrt(4)", "cos(0)"]
        report = self.analyzer.get_coverage(tests=tests)

        self.assertIsInstance(report, CoverageReport)
        self.assertGreaterEqual(report.get_total_coverage(), 0)
        self.assertLessEqual(report.get_total_coverage(), 1)
        self.assertTrue(report.coverage_data)  # Ensure coverage data is populated

    def test_append_coverage(self):
        """Test that coverage can be incrementally added with new tests."""
        self.analyzer.reset()  # Ensure clean coverage data
        initial_tests = ["sqrt(16)"]
        initial_report = self.analyzer.get_coverage(tests=initial_tests)
        initial_coverage = initial_report.get_total_coverage()

        # Append additional tests and check that coverage is updated
        additional_tests = ["sin(10)"]
        updated_report = self.analyzer.append_coverage(additional_tests[0])
        updated_coverage = updated_report.get_total_coverage()

        self.assertGreaterEqual(updated_coverage, initial_coverage)
        self.assertGreater(updated_coverage, 0)

    def test_reset_clears_coverage(self):
        """Test that reset clears all coverage data."""
        self.analyzer.get_coverage(tests=["sqrt(4)", "sin(0)"])
        self.analyzer.reset()  # Reset should clear coverage data

        # Re-run and check that coverage starts fresh
        fresh_report = self.analyzer.get_coverage(tests=["tan(9)"])
        fresh_coverage = fresh_report.get_total_coverage()

        self.assertGreaterEqual(fresh_coverage, 0)
        self.assertLessEqual(fresh_coverage, 1)
        self.assertTrue(fresh_report.coverage_data)  # Coverage data should be populated again

    def test_clean_coverage(self):
        """Test that clean_coverage method erases previous coverage data."""
        # Run initial coverage to create data
        self.analyzer.get_coverage(tests=["sqrt(4)", "sin(0)"])
        self.analyzer.clean_coverage()  # Clean the coverage data

        # Check that the coverage file is erased by running again and seeing fresh coverage
        report = self.analyzer.get_coverage(tests=["sin(0)"])
        coverage = report.get_total_coverage()

        self.assertGreaterEqual(coverage, 0)
        self.assertLessEqual(coverage, 1)
        self.assertTrue(report.coverage_data)  # Ensure new coverage data is created

    def test_multiple_test_run(self):
        """Test running multiple tests with the same CoveragePyAnalyzer instance."""
        tests = ["sqrt(100)", "tan(1)", "cos(2)"]
        report = self.analyzer.get_coverage(tests=tests)

        self.assertIsInstance(report, CoverageReport)
        self.assertGreaterEqual(report.get_total_coverage(), 0)
        self.assertLessEqual(report.get_total_coverage(), 1)
        self.assertTrue(len(report.coverage_data) > 0)

    def test_context_manager_resets_coverage(self):
        """Test that CoveragePyAnalyzer as a context manager resets coverage data on enter and exit."""

        with CoveragePyAnalyzer(project_root=PROJECT_ROOT, harness=HARNESS_PATH) as analyzer:
            # Initial coverage run within the context
            report = analyzer.get_coverage(tests=["sqrt(4)"])
            initial_coverage = report.get_total_coverage()

            # Ensure initial coverage is within the valid range
            self.assertGreaterEqual(initial_coverage, 0)
            self.assertLessEqual(initial_coverage, 1)
            self.assertTrue(report.coverage_data)

        # After exiting the context, re-enter and verify coverage data is reset
        with CoveragePyAnalyzer(project_root=PROJECT_ROOT, harness=HARNESS_PATH) as analyzer:
            report = analyzer.get_coverage(tests=["cos(0)"])
            new_coverage = report.get_total_coverage()

            # Ensure the coverage run in the new context block is fresh and independent
            self.assertGreaterEqual(new_coverage, 0)
            self.assertLessEqual(new_coverage, 1)
            self.assertTrue(report.coverage_data)

            # Verify that coverage data has been reset by checking that new coverage
            self.assertGreater(initial_coverage, new_coverage)


if __name__ == "__main__":
    unittest.main()