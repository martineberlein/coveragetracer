from coverageanalyzer.coverageanalyzer import CoveragePyAnalyzer
from pathlib import Path

if __name__ == "__main__":
    # Initialize the Coverage Analyzer for the project
    analyzer = CoveragePyAnalyzer(
        project_root=Path.cwd() / "dummy" / "project",
        harness=Path.cwd() / "dummy" / "harness.py",
    )

    # Run initial coverage and print report
    report = analyzer.get_coverage(tests=["sqrt(12)", "tan(10)"])
    print("Initial Coverage Report:")
    print(report)
    print(f"Total Project Coverage: {report.get_total_coverage() * 100:.2f}%")

    # Reset coverage for gradient coverage tracking
    print("\n--- Gradient Coverage ---")
    analyzer.reset()

    # Define initial test inputs and gradually add them
    initial_inputs = ["sqrt(12)", "sin(10)", "tan(10)", "cos(1)"]
    for inp in initial_inputs:
        report = analyzer.append_coverage(inp)
        print(f"Coverage after adding '{inp}': {report.get_total_coverage() * 100:.2f}%")

    # Final reset after coverage tracking
    analyzer.reset()

