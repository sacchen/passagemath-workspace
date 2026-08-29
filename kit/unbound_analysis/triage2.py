def show_matrix_space():
    with open('unbound_results.txt') as f:
        print_mode = False
        for line in f:
            if line.startswith('matrix/matrix_space.py'):
                print_mode = True
                print(line, end='')
                continue
            if print_mode:
                if line.startswith('\n') or not line.startswith('  -'):
                    break
                print(line, end='')

show_matrix_space()
