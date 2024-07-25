import subprocess
from pathlib import Path

import coverage


def run_coverage():
    # Define the command to run the tests with coverage

    path_to_dir = Path.cwd() / 'dummy'
    project_root = Path.cwd() / 'dummy' / 'project'

    run_command = [
        'coverage',
        'run',
        f'--source={project_root}',
        'harness.py',
        'sqrt(-1)'
    ]

    try:
        # Run the command
        result = subprocess.run(run_command,
                                #text=True,
                                cwd=path_to_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=True
                                )

        # Print the output and any errors from running the command
        print(result.stdout)
        if result.stderr:
            print(f"Errors:\n{result.stderr}")

    except Exception as e:
        print(f"Error running command: {e}")

    coverage_file = path_to_dir / '.coverage'

    print("Using coverage module")

    cov = coverage.Coverage(data_file=coverage_file)
    cov.load()
    data = cov.get_data()

    # Calculate total possible executable lines
    total_executable_lines = 0

    # Print executed lines for each file
    for file in data.measured_files():
        print(f'File: {file}')
        executed_lines = sorted(data.lines(file))
        print(f'Executed lines: {executed_lines}')
        analysis = cov.analysis2(file)
        executable_lines = analysis[1]
        print(f'Executable lines: {executable_lines}')
        total_executable_lines += len(executable_lines)
        # print(analysis)

    print(f'Total executable lines: {total_executable_lines}')


if __name__ == "__main__":
    run_coverage()
