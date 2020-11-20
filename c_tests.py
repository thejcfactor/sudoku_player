import sudoku_helper

def read_board(filename=None):
    file = filename if filename else 'test_board.txt'
    with open(file, 'r') as f:
        lines = f.readlines()

    cells = []
    for l in lines:
        row = []
        for c in l.strip():
            row.append(int(c))
        cells.append(row)

    return cells


if __name__ == "__main__":
    cells = read_board()
    rows = sudoku_helper.validate_board(cells)
    print(rows)
    result = sudoku_helper.solve_board(cells)
    print(result)