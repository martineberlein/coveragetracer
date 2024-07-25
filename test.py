from src.coverageanalyzer.coverageanalyzer import CoveragePyAnalyzer
from pathlib import Path

if __name__ == "__main__":
    analyzer = CoveragePyAnalyzer(
        project_root=Path.cwd() / "dummy" / "project",
        harness=Path.cwd() / "dummy" / "harness.py",
        test=["sin(0)", "sqrt(1)"],)

    report = analyzer.get_coverage()
    print(report)
    print(report.coverage_data)
    print(report.total_executable_lines)