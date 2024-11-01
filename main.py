if __name__ == '__main__':
    import coverage

    # Define the coverage configuration
    cov = coverage.Coverage(source=['./tmp/example'], branch=True)

    # Start the coverage measurement
    # cov = coverage.Coverage()
    cov.start()

    # Run the main script
    from dummy.example import main

    main()
    from tmp.example.calc import main
    try:
        main("sqrt(36)")
        main("sqrt(0)")
        main("sin(0)")
        main("cos(36)")
        main("tan(36)")
    except ZeroDivisionError:
        print("Caught an AssertionError")

    # Stop the coverage measurement
    cov.stop()
    cov.save()

    # Print the coverage report
    #cov.report()

    # Get the coverage data
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
        total_executable_lines += len(executable_lines)
        # print(analysis)

    print(f'Total executable lines: {total_executable_lines}')
    print(f'Total coverage: {cov.report()}')