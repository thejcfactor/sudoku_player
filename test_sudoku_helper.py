import os
import pytest

import sudoku_helper

@pytest.fixture
def easy_boards():
    board_files = ['board0.txt', 'board1.txt']
    boards = []
    for bf in board_files:
        file = os.path.join(os.getcwd(), 'boards', bf)
        with open(file, 'r') as f:
            lines = f.readlines()

        cells = []
        for l in lines:
            row = []
            for c in l.strip():
                row.append(int(c))
            cells.append(row)

        boards.append(cells)

    return boards

@pytest.fixture
def easy_boards_solutions():
    board_files = ['board0_solution.txt', 'board1_solution.txt']
    boards = []
    for bf in board_files:
        file = os.path.join(os.getcwd(), 'boards',bf)
        with open(file, 'r') as f:
            lines = f.readlines()

        cells = []
        for l in lines:
            row = []
            for c in l.strip():
                row.append(int(c))
            cells.append(row)

        boards.append(cells)

    return boards

@pytest.fixture
def invalid_row_boards():
    board_files = ['row1_square3_fail.txt', 'row5_fail.txt', 'row259_fail.txt']
    boards = []
    for bf in board_files:
        file = os.path.join(os.getcwd(), 'boards',bf)
        with open(file, 'r') as f:
            lines = f.readlines()

        cells = []
        for l in lines:
            row = []
            for c in l.strip():
                row.append(int(c))
            cells.append(row)

        boards.append(cells)

    return boards

@pytest.fixture
def invalid_col_boards():
    board_files = ['col1_fail.txt', 'col147_fail.txt']
    boards = []
    for bf in board_files:
        file = os.path.join(os.getcwd(), 'boards',bf)
        with open(file, 'r') as f:
            lines = f.readlines()

        cells = []
        for l in lines:
            row = []
            for c in l.strip():
                row.append(int(c))
            cells.append(row)

        boards.append(cells)

    return boards

@pytest.fixture
def invalid_square_boards():
    board_files = ['row1_square3_fail.txt', 'square159_fail.txt']
    boards = []
    for bf in board_files:
        file = os.path.join(os.getcwd(), 'boards',bf)
        with open(file, 'r') as f:
            lines = f.readlines()

        cells = []
        for l in lines:
            row = []
            for c in l.strip():
                row.append(int(c))
            cells.append(row)

        boards.append(cells)

    return boards

@pytest.mark.parametrize("idx, num_invalid_rows, invalid_rows", [(0,1,[0]),(1,1,[4]), (2,3,[1,4,8])])
def test_board_row_validation(invalid_row_boards, idx, num_invalid_rows, invalid_rows):
    board_validation = sudoku_helper.validate_board(invalid_row_boards[idx])

    #check num invalid rows matches
    invalid_row_count = sum(1 for r in board_validation['rows'] if r == 0)
    assert invalid_row_count == num_invalid_rows

    #check each invalid row
    rows = [i for i, r in enumerate(board_validation['rows']) if r == 0]
    assert all([a == b for a,b in zip(rows, invalid_rows)])

@pytest.mark.parametrize("idx, num_invalid_cols, invalid_cols", [(0,1,[0]),(1,3,[0,3,6])])
def test_board_col_validation(invalid_col_boards, idx, num_invalid_cols, invalid_cols):
    board_validation = sudoku_helper.validate_board(invalid_col_boards[idx])

    #check num invalid cols matches
    invalid_col_count = sum(1 for r in board_validation['columns'] if r == 0)
    assert invalid_col_count == num_invalid_cols

    #check each invalid col
    cols = [i for i, c in enumerate(board_validation['columns']) if c == 0]
    assert all([a == b for a,b in zip(cols, invalid_cols)])

@pytest.mark.parametrize("idx, num_invalid_squares, invalid_squares", [(0,1,[2]), (1,3,[0,4,8])])
def test_board_square_validation(invalid_square_boards, idx, num_invalid_squares, invalid_squares):
    board_validation = sudoku_helper.validate_board(invalid_square_boards[idx])

    #check num invalid squares matches
    invalid_square_count = sum(1 for r in board_validation['squares'] if r == 0)
    assert invalid_square_count == num_invalid_squares

    #check each invalid square
    squares = [i for i, s in enumerate(board_validation['squares']) if s == 0]
    assert all([a == b for a,b in zip(squares, invalid_squares)])

def test_solve_easy_boards(easy_boards, easy_boards_solutions):
    for b_idx, board in enumerate(easy_boards):
        solution = sudoku_helper.solve_board(board)
        for i, row in enumerate(solution['board']):
            solution_row = easy_boards_solutions[b_idx][i]
            assert len(row) == len(solution_row)
            assert all([a == b for a,b in zip(row, solution_row)])
