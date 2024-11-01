from typing import Optional, Dict, Set, Tuple, List
from abc import ABC, abstractmethod
import os
import subprocess
from pathlib import Path
import coverage
import ast

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

    def __enter__(self):
        """Enter the runtime context related to this object."""
        self.reset()  # Automatically reset (clean) coverage on entering the context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context, ensuring coverage data is reset."""
        self.reset()  # Clean up coverage data when exiting the context

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


class Block:
    """Represents a code block in a Python file, such as a function or class.

    Attributes:
        start_line (int): The starting line number of the block.
        end_line (int): The ending line number of the block.
        type (str): The type of the block (e.g., "Function", "Class").
        code (str): The original source code for the block.
    """

    def __init__(self, start_line: int, end_line: int, block_type: str, code: str):
        self.start_line = start_line
        self.end_line = end_line
        self.type = block_type
        self.code = code

    def __repr__(self):
        return f"Block(type={self.type}, lines={self.start_line}-{self.end_line})"


class BlockAnalyzer:
    """Analyzes Python files in a directory, identifying and storing code blocks.

    Attributes:
        file_blocks (Dict[Path, List[Block]]): A dictionary mapping file paths to lists of Block objects,
            representing each identifiable code block in the files.

    Args:
        project_root (os.PathLike): The root directory containing the Python files to analyze.
    """

    def __init__(self, project_root: os.PathLike):
        self.file_blocks: Dict[Path, List[Block]] = {}
        self.collect_code_blocks_for_directory(Path(project_root))

    def collect_code_blocks_for_directory(self, directory: Path):
        """Recursively collects code blocks from all Python files in a directory.

        Args:
            directory (Path): The path of the directory to analyze.
        """
        for file in directory.rglob("*.py"):
            self.file_blocks[file] = self.get_code_blocks(file)

    @staticmethod
    def get_code_blocks(file: Path) -> List[Block]:
        """Extracts code blocks from a single Python file.

        Args:
            file (Path): The path of the Python file to analyze.

        Returns:
            List[Block]: A list of Block objects representing each identifiable code block in the file.
        """
        try:
            visitor = BlockASTVisitor(file)
            return visitor.extract_code_blocks()
        except SyntaxError as e:
            print(f"Syntax error in file {file}: {e}")
            return []


class BlockASTVisitor(ast.NodeVisitor):
    """A visitor that traverses the AST of a Python file to extract code blocks.

    Attributes:
        file_path (Path): The path of the file being analyzed.
        blocks (List[Block]): A list of Block objects representing the identified code blocks in the file.
        tree (ast.AST): The parsed AST of the Python file.
        code_lines (List[str]): The lines of code in the file, used for extracting block text.

    Args:
        file_path (Path): The path of the Python file to be analyzed.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.blocks = []

        code = self.read_file()
        self.tree = ast.parse(code)
        self.code_lines = None  # Initialize to None for lazy loading of lines

    def read_file(self) -> str:
        """Reads the file's contents.

        Returns:
            str: The complete text of the file.
        """
        return self.file_path.read_text()

    def extract_code_blocks(self) -> List[Block]:
        """Extracts all code blocks in the file by visiting each node in the AST.

        Returns:
            List[Block]: A list of Block objects representing the code blocks in the file.
        """
        self.visit(self.tree)
        return self.blocks

    def get_code_lines(self) -> List[str]:
        """Lazily loads and splits the file's code lines for block extraction."""
        if self.code_lines is None:
            self.code_lines = self.read_file().splitlines()
        return self.code_lines

    def add_block(self, node, block_type: str):
        """Helper method to add a block to the list of blocks.

        Args:
            node: The AST node representing the code block.
            block_type (str): The type of the code block.
        """
        start_line, end_line = node.lineno, node.body[-1].end_lineno
        self.blocks.append(Block(start_line, end_line, block_type, ast.unparse(node)))

    def add_else_block(self, node):
        """Helper to handle 'else' blocks associated with loops or if statements."""
        else_start, else_end = node.orelse[0].lineno, node.orelse[-1].end_lineno
        else_code = "\n".join(self.get_code_lines()[else_start - 1 : else_end])
        self.blocks.append(Block(else_start, else_end, "Else", else_code))

    def visit_FunctionDef(self, node):
        """Visits function definitions."""
        self.add_block(node, "Function")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visits class definitions."""
        self.add_block(node, "Class")
        self.generic_visit(node)

    def visit_If(self, node):
        """Visits if statements and their else clauses."""
        self.add_block(node, "If")
        if node.orelse:
            self.add_else_block(node)
        self.generic_visit(node)

    def visit_For(self, node):
        """Visits for loops and their else clauses."""
        self.add_block(node, "For")
        if node.orelse:
            self.add_else_block(node)
        self.generic_visit(node)

    def visit_While(self, node):
        """Visits while loops and their else clauses."""
        self.add_block(node, "While")
        if node.orelse:
            self.add_else_block(node)
        self.generic_visit(node)

    def visit_Try(self, node):
        """Visits try-except blocks, including else and finally clauses."""
        self.add_block(node, "Try")
        if node.orelse:
            self.add_else_block(node)
        if node.finalbody:
            finally_start, finally_end = (
                node.finalbody[0].lineno,
                node.finalbody[-1].end_lineno,
            )
            finally_code = "\n".join(
                self.get_code_lines()[finally_start - 1 : finally_end]
            )
            self.blocks.append(
                Block(finally_start, finally_end, "Finally", finally_code)
            )
        self.generic_visit(node)

    def visit_With(self, node):
        """Visits with statements."""
        self.add_block(node, "With")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Visits asynchronous function definitions."""
        self.add_block(node, "Async Function")
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        """Visits asynchronous for loops and their else clauses."""
        self.add_block(node, "Async For")
        if node.orelse:
            self.add_else_block(node)
        self.generic_visit(node)

    def visit_AsyncWith(self, node):
        """Visits asynchronous with statements."""
        self.add_block(node, "Async With")
        self.generic_visit(node)
