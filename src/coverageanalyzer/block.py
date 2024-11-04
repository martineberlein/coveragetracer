from typing import Dict, List, Optional, Set
import ast
import os
from pathlib import Path

from .report import CoverageReport
from .line import CoveragePyAnalyzer


class Block:
    """Represents a code block in a Python file, such as a function or class.

    Attributes:
        file_path (str): Path to the file containing the block.
        start_line (int): Starting line number of the block.
        end_line (int): Ending line number of the block.
        type (str): Type of the block (e.g., "Function", "Class").
        code (str): Source code within the block.
    """

    def __init__(
        self, file_path: str, start_line: int, end_line: int, block_type: str, code: str
    ):
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.type = block_type
        self.code = code

    def __repr__(self):
        return f"Block(type={self.type}, lines={self.start_line}-{self.end_line})"

    def __eq__(self, other):
        if not isinstance(other, Block):
            return False
        return (
            self.file_path == other.file_path
            and self.start_line == other.start_line
            and self.end_line == other.end_line
            and self.type == other.type
        )

    def __hash__(self):
        return hash((self.file_path, self.start_line, self.end_line, self.type))


class BlockCoverageReport(CoverageReport):
    """Block-level coverage data report for Python files.

    Attributes:
        coverage_data (Dict[str, Set[int]]): Maps file names to sets of executed line numbers.
        total_executable_blocks (Dict[str, List[Block]]): Maps file names to lists of code blocks.
    """

    def __init__(
        self,
        coverage_data: Dict[str, Set[int]],
        total_executable_blocks: Dict[str, List[Block]],
    ):
        super().__init__()
        self.coverage_data = coverage_data
        self.total_executable_blocks = total_executable_blocks

    def _get_covered_blocks(self, file: str) -> Set['Block']:
        """Identifies blocks in a file that have been executed.

        Args:
            file (str): Path to the file to analyze.

        Returns:
            Set[Block]: Executed blocks within the file.
        """
        covered_lines = self.coverage_data.get(file, set())
        covered_blocks = set()

        for block in self.total_executable_blocks.get(file, []):
            if any(
                line in covered_lines
                for line in range(block.start_line + 1, block.end_line + 1)
            ):
                covered_blocks.add(block)

        return covered_blocks

    def get_file_coverage(self, file: str) -> float:
        """Calculates block coverage for a specific file.

        Args:
            file (str): Path to the file.

        Returns:
            float: Percentage of blocks covered in the file.
        """
        total_blocks = len(self.total_executable_blocks.get(file, []))
        covered_blocks = len(self._get_covered_blocks(file))
        return covered_blocks / total_blocks if total_blocks > 0 else 0.0

    def get_total_coverage(self) -> float:
        """Calculates total block coverage across all files.

        Returns:
            float: Total block coverage percentage across the project.
        """
        total_blocks = sum(
            len(blocks) for blocks in self.total_executable_blocks.values()
        )
        covered_blocks = sum(
            len(self._get_covered_blocks(file)) for file in self.total_executable_blocks
        )
        return covered_blocks / total_blocks if total_blocks > 0 else 0.0

    def is_block_covered(self, block: Block) -> bool:
        """Checks if a specific block has been covered.

        Args:
            block (Block): Code block to check.

        Returns:
            bool: True if the block is covered, False otherwise.
        """
        return block in self._get_covered_blocks(block.file_path)

    def __repr__(self):
        return (
            f"BlockCoverageReport("
            f"{[file + ': ' + str(len(self._get_covered_blocks(file))) + '/' + str(len(blocks)) for file, blocks in self.total_executable_blocks.items()]}, "
            f"total_coverage={self.get_total_coverage() * 100:.2f}%)"
        )


class BlockCoveragePyAnalyzer(CoveragePyAnalyzer):
    """Analyzes Python files for block-level coverage.

    Attributes:
        project_root (os.PathLike): Root directory of the project.
        file_blocks (Dict[str, List[Block]]): Maps file paths to lists of Block objects.
    """

    def __init__(
        self, project_root: os.PathLike, harness: Optional[os.PathLike] = None
    ):
        super().__init__(project_root, harness)
        self.file_blocks: Dict[str, List[Block]] = {}
        self.collect_code_blocks_for_directory(Path(project_root))

    def get_coverage(self, tests: List[str], clean: bool = True) -> BlockCoverageReport:
        """Runs tests with coverage and analyzes block-level coverage results.

        Args:
            tests: List of test commands or scripts to execute.
            clean: Whether to erase previous coverage data before running.

        Returns:
            BlockCoverageReport: Report with block-level coverage data.
        """
        coverage_report = super().get_coverage(tests, clean)
        return BlockCoverageReport(coverage_report.coverage_data, self.file_blocks)

    def append_coverage(self, test: str) -> BlockCoverageReport:
        """Appends coverage data for an additional test.

        Args:
            test: The test script or command to run.

        Returns:
            BlockCoverageReport: Updated report with appended block coverage data.
        """
        coverage_report = super().append_coverage(test)
        return BlockCoverageReport(coverage_report.coverage_data, self.file_blocks)

    def collect_code_blocks_for_directory(self, directory: Path):
        """Collects code blocks from Python files in a directory.

        Args:
            directory (Path): Directory to analyze.
        """
        for file in directory.rglob("*.py"):
            self.file_blocks[str(file)] = self.get_code_blocks(file)

    @staticmethod
    def get_code_blocks(file: Path) -> List[Block]:
        """Extracts code blocks from a Python file.

        Args:
            file (Path): Path to the file.

        Returns:
            List[Block]: Code blocks identified in the file.
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

    def extract_code_blocks(self) -> list[Block]:
        """Extracts all code blocks in the file by visiting each node in the AST.

        Returns:
            List[Block]: A list of Block objects representing the code blocks in the file.
        """
        self.visit(self.tree)
        return self.blocks

    def get_code_lines(self) -> list[str]:
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
        self.blocks.append(
            Block(
                str(self.file_path), start_line, end_line, block_type, ast.unparse(node)
            )
        )

    def add_else_block(self, node):
        """Helper to handle 'else' blocks associated with loops or if statements."""
        else_start, else_end = node.orelse[0].lineno - 1, node.orelse[-1].end_lineno
        else_code = "\n".join(self.get_code_lines()[else_start:else_end])
        self.blocks.append(
            Block(str(self.file_path), else_start, else_end, "Else", else_code)
        )

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
                Block(
                    str(self.file_path),
                    finally_start,
                    finally_end,
                    "Finally",
                    finally_code,
                )
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
