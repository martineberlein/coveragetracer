from typing import Optional
from abc import ABC, abstractmethod


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


class CoverageReport(Report, ABC):
    """
    Abstract base class for coverage reports.
    """

    def __init__(self):
        super().__init__("CoverageReport")

    @abstractmethod
    def get_file_coverage(self, file: str) -> float:
        """
        Calculates the coverage for a specific file.

        Args:
            file: The path of the file to calculate coverage for.

        Returns:
            The coverage as a float between 0 and 1.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_total_coverage(self) -> float:
        """
        Calculates the overall project coverage.

        Returns:
            The total coverage as a float between 0 and 1.
        """
        raise NotImplementedError()
