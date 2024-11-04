import unittest
import tempfile
from pathlib import Path

from coverageanalyzer.block import BlockCoverageReport, Block, BlockCoveragePyAnalyzer


class TestBlockAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up temporary test files for BlockAnalyzer tests."""
        # Create a temporary directory to hold test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.test_dir.name)

        # Sample Python content for testing various block types
        self.sample_code = """\
class TestClass:
    def method(self):
        pass

def function():
    if True:
        pass
    else:
        pass

for i in range(5):
    pass
else:
    pass
"""

        # Write a test file to the temporary directory
        self.test_file = self.project_root / "test_file.py"
        self.test_file.write_text(self.sample_code)

    def tearDown(self):
        """Clean up temporary files."""
        self.test_dir.cleanup()

    def test_collect_code_blocks_for_directory(self):
        """Test that BlockAnalyzer correctly identifies code blocks in a directory."""
        analyzer = BlockCoveragePyAnalyzer(project_root=self.project_root)
        file_blocks = analyzer.file_blocks

        # Ensure test file was processed
        self.assertIn(str(self.test_file), file_blocks)
        blocks = file_blocks[str(self.test_file)]

        # Assert the number of blocks is as expected
        self.assertEqual(len(blocks), 7)

        # Check that the expected block types are present
        block_types = [block.type for block in blocks]
        expected_types = {"Class", "Function", "If", "For", "Else"}

        for expected_type in expected_types:
            self.assertIn(expected_type, block_types)

    def test_block_attributes(self):
        """Test that extracted blocks have correct attributes for line numbers and code."""
        analyzer = BlockCoveragePyAnalyzer(project_root=self.project_root)
        blocks = analyzer.file_blocks[str(self.test_file)]

        # Validate first block (Class)
        first_block = blocks[0]
        self.assertEqual(first_block.type, "Class")
        self.assertEqual(first_block.start_line, 1)
        self.assertIn("class TestClass:", first_block.code)

        # Validate second block (Function)
        second_block = blocks[1]
        self.assertEqual(second_block.type, "Function")
        self.assertEqual(second_block.start_line, 2)
        self.assertIn("def method(self):", second_block.code)

    def test_syntax_error_handling(self):
        """Test that BlockAnalyzer handles files with syntax errors gracefully."""
        # Create a file with a syntax error
        syntax_error_file = self.project_root / "syntax_error.py"
        syntax_error_file.write_text("def func()\n    return")  # Missing colon

        # Run BlockAnalyzer
        analyzer = BlockCoveragePyAnalyzer(project_root=self.project_root)

        # Assert that syntax error file was processed and no blocks were extracted
        self.assertIn(str(syntax_error_file), analyzer.file_blocks)
        self.assertEqual(analyzer.file_blocks[str(syntax_error_file)], [])

    def test_empty_file(self):
        """Test that BlockAnalyzer handles an empty file correctly."""
        # Create an empty file
        empty_file = self.project_root / "empty_file.py"
        empty_file.touch()

        # Run BlockAnalyzer
        analyzer = BlockCoveragePyAnalyzer(project_root=self.project_root)

        # Assert that empty file was processed and no blocks were extracted
        self.assertIn(str(empty_file), analyzer.file_blocks)
        self.assertEqual(analyzer.file_blocks[str(empty_file)], [])

    def test_multiple_files_in_directory(self):
        """Test that BlockAnalyzer processes multiple files in a directory."""
        # Create additional test file
        additional_file = self.project_root / "additional_file.py"
        additional_code = "def another_function():\n    pass\n"
        additional_file.write_text(additional_code)

        # Run BlockAnalyzer
        analyzer = BlockCoveragePyAnalyzer(project_root=self.project_root)
        file_blocks = analyzer.file_blocks

        # Ensure both files are processed
        self.assertIn(str(self.test_file), file_blocks)
        self.assertIn(str(additional_file), file_blocks)

        # Assert the correct number of blocks are identified in each file
        self.assertEqual(len(file_blocks[str(self.test_file)]), 7)
        self.assertEqual(len(file_blocks[str(additional_file)]), 1)

    def test_repr_method_in_block(self):
        """Test that Block's __repr__ method produces the expected output."""
        block = Block(file_path= "", start_line=1, end_line=5, block_type="Function", code="def test():\n    pass")
        repr_output = repr(block)
        self.assertEqual(repr_output, "Block(type=Function, lines=1-5)")

    def test_block_coverage_analyzer(self):
        """Test that BlockAnalyzer can track coverage for blocks."""

        # Initialize a BlockAnalyzer object
        analyzer = BlockCoveragePyAnalyzer(
            project_root= Path.cwd() / "resources" / "project",
            harness = Path.cwd() / "resources" / "harness.py",
        )

        report = analyzer.get_coverage(tests=["sqrt(12)", "tan(10)", "sin(0)"], clean=True)

        for file, blocks in report.total_executable_blocks.items():
            for block in blocks:
                print(block)
                print(block.code)
                print(report.is_block_covered(block))

        print("Initial Coverage Report:", report)
        print(f"Total Project Coverage: {report.get_total_coverage() * 100:.2f}%")

        # Final reset after coverage tracking
        analyzer.reset()


if __name__ == "__main__":
    unittest.main()