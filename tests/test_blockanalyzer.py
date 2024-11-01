import unittest
import tempfile
from pathlib import Path

from coverageanalyzer.coverageanalyzer import BlockAnalyzer, Block


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
        analyzer = BlockAnalyzer(project_root=self.project_root)
        file_blocks = analyzer.file_blocks

        # Ensure test file was processed
        self.assertIn(self.test_file, file_blocks)
        blocks = file_blocks[self.test_file]

        # Assert the number of blocks is as expected
        self.assertEqual(len(blocks), 7)

        # Check that the expected block types are present
        block_types = [block.type for block in blocks]
        expected_types = {"Class", "Function", "If", "For", "Else"}

        for expected_type in expected_types:
            self.assertIn(expected_type, block_types)

    def test_block_attributes(self):
        """Test that extracted blocks have correct attributes for line numbers and code."""
        analyzer = BlockAnalyzer(project_root=self.project_root)
        blocks = analyzer.file_blocks[self.test_file]

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
        analyzer = BlockAnalyzer(project_root=self.project_root)

        # Assert that syntax error file was processed and no blocks were extracted
        self.assertIn(syntax_error_file, analyzer.file_blocks)
        print(analyzer.file_blocks)
        self.assertEqual(analyzer.file_blocks[syntax_error_file], [])

    def test_empty_file(self):
        """Test that BlockAnalyzer handles an empty file correctly."""
        # Create an empty file
        empty_file = self.project_root / "empty_file.py"
        empty_file.touch()

        # Run BlockAnalyzer
        analyzer = BlockAnalyzer(project_root=self.project_root)

        # Assert that empty file was processed and no blocks were extracted
        self.assertIn(empty_file, analyzer.file_blocks)
        self.assertEqual(analyzer.file_blocks[empty_file], [])

    def test_multiple_files_in_directory(self):
        """Test that BlockAnalyzer processes multiple files in a directory."""
        # Create additional test file
        additional_file = self.project_root / "additional_file.py"
        additional_code = "def another_function():\n    pass\n"
        additional_file.write_text(additional_code)

        # Run BlockAnalyzer
        analyzer = BlockAnalyzer(project_root=self.project_root)
        file_blocks = analyzer.file_blocks

        # Ensure both files are processed
        self.assertIn(self.test_file, file_blocks)
        self.assertIn(additional_file, file_blocks)

        # Assert the correct number of blocks are identified in each file
        self.assertEqual(len(file_blocks[self.test_file]), 7)
        self.assertEqual(len(file_blocks[additional_file]), 1)

    def test_repr_method_in_block(self):
        """Test that Block's __repr__ method produces the expected output."""
        block = Block(start_line=1, end_line=5, block_type="Function", code="def test():\n    pass")
        repr_output = repr(block)
        self.assertEqual(repr_output, "Block(type=Function, lines=1-5)")


if __name__ == "__main__":
    unittest.main()