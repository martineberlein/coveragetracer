from abc import ABC, abstractmethod
import os

from .report import CoverageReport


class CoverageAnalyzer(ABC):
    """Abstract base class for analyzing code coverage.

    Attributes:
        project_root: Root directory of the project.
    """

    def __init__(self, project_root: os.PathLike):
        self.project_root = project_root

    @abstractmethod
    def get_coverage(self, tests: list[str]) -> CoverageReport:
        """Run the provided tests with coverage and analyze results.

        Args:
            tests: List of test commands or scripts to execute.

        Returns:
            A CoverageReport instance with the coverage data.
        """
        pass

    @abstractmethod
    def append_coverage(self, test: str) -> CoverageReport:
        """
        Appends coverage data for an additional test.

        Args:
            test: The test script or command to run.

        Returns:
            A CoverageReport with updated coverage data.
        """
        pass
