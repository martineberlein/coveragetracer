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

    trigg = dict()
    for file, lines in report.total_executable_lines.items():
        trigg[file] = lines.intersection(report.coverage_data[file])

    print(trigg)
    su = 0
    for file, lines in trigg.items():
        print(f"{file}: {len(lines)}")
        su += len(lines)

    print(f"Total: {su}")
    print(f"Coverage: {su / sum(len(lines) for lines in report.total_executable_lines.values())}")
