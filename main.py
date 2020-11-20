import os
from os.path import join

from window import Window


def read_board(filename=None):
    file = filename if filename else os.path.join(os.getcwd(), 'boards','board5.txt')
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
    try:
        board = read_board()

        window = Window(board)
    except Exception as ex:
        print("Found exception...exiting program.")
        print(ex)
        exit(1)

















