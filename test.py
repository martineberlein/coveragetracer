from src.coverageanalyzer.coverageanalyzer import CoveragePyAnalyzer
from pathlib import Path

if __name__ == "__main__":
    analyzer = CoveragePyAnalyzer(
        project_root=Path.cwd() / "dummy" / "project",
        harness=Path.cwd() / "dummy" / "harness.py",
        test=["sqrt(12)", "sin(10)", "tan(10)"],)

    report = analyzer.get_coverage()
    print(report)
    print(report.get_total_coverage())

    print("--- gradient coverage ---")
    analyzer.reset()
    initial_inputs = ["sqrt(12)", "sin(10)", "tan(10)", "cos(1)"]
    for inp in initial_inputs:
        report = analyzer.append_coverage(inp)
        print(report.get_total_coverage())

    analyzer.reset()
