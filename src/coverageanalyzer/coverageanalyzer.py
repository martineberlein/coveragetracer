from typing import Optional, Dict, Set, Tuple, List
from abc import ABC, abstractmethod
import os
import subprocess
from pathlib import Path
import coverage

COVERAGE = "coverage"


class Report:
    """
    Represents a generic coverage report.

    Attributes:
        command: The command used to generate the report.
        successful: Indicates if the command ran successfully.
        raised_exception: Stores any exception raised during execution.
    """

    def __init__(self, command: str):
        self.command: str = command
        self.successful: Optional[bool] = None
        self.raised_exception: Optional[Exception] = None

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class CoverageReport(Report):
    """
    Coverage report detailing coverage data and executable lines.

    Attributes:
        coverage_data: Dictionary with files as keys and covered lines as values.
        total_executable_lines: Dictionary with files as keys and all executable lines as values.
    """

    def __init__(
        self,
        coverage_data: Dict[str, Set[int]],
        total_executable_lines: Dict[str, Set[int]],
    ):
        super().__init__(COVERAGE)
        self.coverage_data = coverage_data
        self.total_executable_lines = total_executable_lines

    def get_file_coverage(self, file: str) -> float:
        """
        Calculates the coverage for a specific file.

        Args:
            file: The path of the file to calculate coverage for.

        Returns:
            The coverage as a float between 0 and 1.
        """
        if file not in self.coverage_data:
            return 0.0

        total_lines = len(self.total_executable_lines[file])
        covered_lines = len(self.coverage_data[file])
        return covered_lines / total_lines

    def get_total_coverage(self) -> float:
        """
        Calculates the overall project coverage.

        Returns:
            The total coverage as a float between 0 and 1.
        """
        total_lines = sum(len(lines) for lines in self.total_executable_lines.values())
        covered_lines = sum(len(lines) for lines in self.coverage_data.values())
        return covered_lines / total_lines

    def __repr__(self):
        return (
            f"CoverageReport("
            f"{[str(Path(file).name) + ': ' + str(lines) for file, lines in self.coverage_data.items()]}, "
            f"coverage={self.get_total_coverage()})"
        )


class CoverageAnalyzer(ABC):
    """Abstract base class for analyzing code coverage.

    Attributes:
        project_root: Root directory of the project.
    """

    def __init__(self, project_root: os.PathLike):
        self.project_root = project_root

    @abstractmethod
    def get_coverage(self, tests: List[str]):
        """Run the provided tests with coverage and analyze results.

        Args:
            tests: List of test commands or scripts to execute.
        """
        pass


class CoveragePyAnalyzer(CoverageAnalyzer):
    """Analyzes code coverage using the coverage.py module.

    Attributes:
        project_root: Root directory of the project.
        harness: Optional path to a test harness.
        output: Optional path to coverage output file.
    """

    def __init__(
        self,
        project_root: os.PathLike,
        harness: Optional[os.PathLike] = None,
        output: Optional[os.PathLike] = None,
    ):
        super().__init__(project_root)
        self.output = output if output else Path(project_root) / ".coverage"
        self.harness = harness if harness else Path(project_root) / "harness.py"

    @staticmethod
    def get_all_executable_lines(cov: coverage.Coverage) -> Dict[str, Set[int]]:
        """
        Fetches all executable lines from the coverage data.

        Args:
            cov: A coverage.Coverage instance with loaded data.

        Returns:
            A dictionary with file paths as keys and sets of executable line numbers as values.
        """
        all_executable_lines = dict()
        data = cov.get_data()
        for file in data.measured_files():
            analysis = cov.analysis2(file)
            executable_lines = analysis[1]
            all_executable_lines[file] = set(executable_lines)
        return all_executable_lines

    def analyze_coverage_data(self) -> Tuple[Dict[str, Set[int]], Dict[str, Set[int]]]:
        """
        Analyzes the coverage data after test execution.

        Returns:
            A tuple containing:
                - coverage_data: Dictionary with covered lines for each file.
                - total_executable_lines: Dictionary with all executable lines for each file.
        """
        coverage_data = dict()
        cov = coverage.Coverage(data_file=self.output)
        cov.load()
        total_executable_lines = self.get_all_executable_lines(cov)

        for file in cov.get_data().measured_files():
            lines = cov.get_data().lines(file)
            clean_lines = total_executable_lines[file].intersection(lines)
            coverage_data[file] = set(clean_lines)

        return coverage_data, total_executable_lines

    def _run_command_for_test(self, command: List[str], test: str):
        """
        Runs coverage for a specific test.

        Args:
            command: List of command components to run.
            test: The specific test script or command.

        Returns:
            The result of the subprocess execution.
        """
        result = subprocess.run(
            command + [self.harness, test],
            text=True,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result

    def clean_coverage(self):
        """
        Removes existing coverage data.
        """
        subprocess.run(
            ["coverage", "erase", f"--data-file={self.output}"], cwd=self.project_root
        )

    def get_coverage(self, tests: List[str], clean: bool = True) -> CoverageReport:
        """Run the provided tests with coverage and analyze results.

        Args:
            tests: List of test commands or scripts to execute.
            clean: Whether to erase previous coverage data before running.

        Returns:
            A CoverageReport instance with the coverage data.
        """
        if clean:
            self.clean_coverage()

        command = [
            "coverage",
            "run",
            f"--data-file={self.output}",
            f"--source={self.project_root}",
        ]
        if len(tests) > 1:
            command.append("--append")

        for test in tests:
            self._run_command_for_test(command, test)

        coverage_data, total_executable_lines = self.analyze_coverage_data()
        return CoverageReport(coverage_data, total_executable_lines)

    def reset(self):
        """
        Resets coverage data by cleaning any existing coverage.
        """
        self.clean_coverage()

    def append_coverage(self, test):
        """
        Appends coverage data for an additional test.

        Args:
            test: The test script or command to run.

        Returns:
            A CoverageReport with updated coverage data.
        """
        command = [
            "coverage",
            "run",
            f"--data-file={self.output}",
            f"--source={self.project_root}",
            "--append",
        ]
        self._run_command_for_test(command, test)
        coverage_data, total_executable_lines = self.analyze_coverage_data()
        return CoverageReport(coverage_data, total_executable_lines)

