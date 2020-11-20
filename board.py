import tkinter as tk
from tkinter import Canvas, IntVar
import tkinter.scrolledtext as st
import datetime

from utilities import get_new_board

import sudoku_helper


class Coordinates(object):

    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def get_coordinates(self):
        return [self.x0,self.y0,self.x1,self.y1]


class BoardCell(object):

    def __init__(self, coordinates, row, col, value, default):
        self.coordinates = coordinates
        self.row = row
        self.col = col
        self.value = value
        self.default = default if default else False
        self.invalid = False

    def point_in_cell(self, x, y):
        return x > self.coordinates.x0 and x < self.coordinates.x1 \
            and y > self.coordinates.y0 and y < self.coordinates.y1


class Board(object):

    __cell_width = 50
    __margin = 10

    def __init__(self, frame, initial_state):
        self.__board_width = (self.__margin * 2) + (self.__cell_width * 9)
        self.__board_height = self.__board_width
        self.initial_state = initial_state
        self.cells = []
        self.current_cell = None
        self.board_invalid = False
        self.difficulty = IntVar()
        self.difficulty.set(1)

        self.board = Canvas(master=frame, width=self.__board_width,
                            height=self.__board_height, bg="white", bd=0, highlightthickness=0)

        self.board.pack(fill=tk.BOTH)

        self.info_area = {
            'index': 0,
            'widget': None
        }

    def init_board(self):
        self.draw_cell_frames()
        self.draw_cells(init=True)

        self.board.bind('<Button-1>', self.cell_clicked)
        self.board.bind('<Key>', self.key_pressed)
        self.board.bind('<Left>', lambda event,
                        arg='LEFT': self.arrow_key_pressed(event, arg))
        self.board.bind('<Right>', lambda event,
                        arg='RIGHT': self.arrow_key_pressed(event, arg))
        self.board.bind('<Up>', lambda event,
                        arg='UP': self.arrow_key_pressed(event, arg))
        self.board.bind('<Down>', lambda event,
                        arg='DOWN': self.arrow_key_pressed(event, arg))

        
    def set_info_area(self, st):
        self.info_area['widget'] = st
        self.info_area['widget'].configure(state = 'disabled')

    """

    Drawing methods

    """

    def draw_cell_frames(self):
        length = self.__cell_width * 3
        for i in range(4):
            hl = self.get_frame_line_coordinates(i, length, True)
            line_width = 2

            # Adjust outter lines to get square edges
            if i in [0, 3]:
                hl.x0 -= 1
                hl.x1 += 1
                line_width = 3

            vl = self.get_frame_line_coordinates(i, length)

            self.board.create_line(hl.x0, hl.y0, hl.x1,
                                   hl.y1, fill="black", width=line_width)
            self.board.create_line(vl.x0, vl.y0, vl.x1,
                                   vl.y1, fill="black", width=line_width)

    def draw_cells(self, init=False):
        self.board.delete("filled")

        state = self.initial_state if init else self.state

        y_start = self.__margin
        for i, row in enumerate(self.initial_state):

            coords = self.get_cell_coordinates(y_start, i)
            y0 = coords[0]
            y1 = coords[1]

            x_start = self.__margin
            self.cells.append([])
            for j, cell_value in enumerate(row):

                coords = self.get_cell_coordinates(x_start, j)
                x0 = coords[0]
                x1 = coords[1]

                if cell_value != 0:
                    x = x0 + (x1 - x0) / 2
                    y = y0 + (y1 - y0) / 2
                    self.board.create_rectangle(
                        x0, y0, x1, y1, fill="#eee", outline="#000", width=1)
                    self.board.create_text(
                        x, y, text=str(cell_value), tags="numbers", fill="#000")
                else:
                    tag = '({0},{1})'.format(i,j)
                    self.board.create_rectangle(
                        x0, y0, x1, y1, fill="#fff", outline="#000", tags=tag, activeoutline="blue", width=1)

                if init:
                    coords = Coordinates(x0, y0, x1, y1)
                    cell = BoardCell(coords, i, j, cell_value,
                                     cell_value != 0)
                    self.cells[i].append(cell)

                x_start = self.update_cell_start(j, x1)

            y_start = self.update_cell_start(i, y1)

    def draw_current_cell(self, cell):
        
        if self.current_cell:
            self.board.delete("current_cell")
            x0,y0,x1,y1 = self.current_cell.coordinates.get_coordinates()
            tag = '({0},{1})'.format(self.current_cell.row, self.current_cell.col)
            color = '#fa8585' if self.current_cell.invalid else '#fff'
            self.board.create_rectangle(x0, y0, x1, y1, fill=color, outline="#000", activeoutline="blue", tags=tag, width=1)
            if self.current_cell.value != 0:
                tag = '({0},{1})::value'.format(self.current_cell.row, self.current_cell.col)
                self.board.delete(tag)
                self.draw_cell_value(self.current_cell)


        x0,y0,x1,y1 = cell.coordinates.get_coordinates()
        tag = '({0},{1})'.format(cell.row, cell.col)
        self.board.delete(tag)
        color = '#fa8585' if cell.invalid else '#fff'
        self.board.create_rectangle(x0, y0, x1, y1, fill=color, outline="red", tags='current_cell', width=1)
        if cell.value != 0:
            tag = '({0},{1})::value'.format(cell.row, cell.col)
            self.board.delete(tag)
            self.draw_cell_value(cell)

    def draw_cell(self, cell, background="#fff"):
        x0,y0,x1,y1 = cell.coordinates.get_coordinates()
        tag = '({0},{1})'.format(cell.row, cell.col)
        self.board.delete(tag)
        self.board.create_rectangle(x0, y0, x1, y1, fill=background, outline="#000", tags=tag, width=1)
        if cell.value != 0:
            tag = '({0},{1})::value'.format(cell.row, cell.col)
            self.board.delete(tag)
            self.draw_cell_value(cell)

    def mark_invalid_cells(self):
        for row in self.cells:
            for cell in row:
                if cell.default:
                    continue
                if cell.invalid:
                    self.draw_cell(cell, background="#fa8585")
                else:
                    self.draw_cell(cell)

    def draw_cell_value(self, cell, color="blue"):
        x0,y0,x1,y1 = cell.coordinates.get_coordinates()
        x = x0 + (x1 - x0) / 2
        y = y0 + (y1 - y0) / 2
        tag = '({0},{1})::value'.format(cell.row, cell.col)
        self.board.create_text(
            x, y, text=str(cell.value), tags=tag, fill=color)

    def erase_cell_value(self, cell):
        tag = '({0},{1})::value'.format(cell.row, cell.col)
        self.board.delete(tag)

    def draw_new_board(self, new_board):
        self.board.delete('all')
        self.initial_state = []
        self.initial_state = new_board
        self.cells = []
        self.init_board()

    def get_frame_line_coordinates(self, idx, length, horizontal=False):
        if horizontal:
            line = Coordinates(x0=self.__margin,
                               y0=self.__margin + idx * length,
                               x1=self.__board_width - self.__margin,
                               y1=self.__margin + idx * length)
        else:
            line = Coordinates(x0=self.__margin + idx * length,
                               y0=self.__margin,
                               x1=self.__margin + idx * length,
                               y1=self.__board_height - self.__margin)

        return line

    def get_cell_coordinates(self, start, idx):
        c0 = start
        c1 = c0 + self.__cell_width

        if idx == 0:
            c0 += 2
        else:
            c0 += 1

        if idx % 3 == 2:
            c1 -= 2

        return (c0, c1)

    def update_cell_start(self, idx, coord):
        return coord+2 if idx % 3 == 2 else coord

    def set_info_text(self, msg, erase=False):
        f_msg = '{0:%H:%M:%S}: {1}\n'.format(datetime.datetime.now(), msg)
        if erase:
            self.info_area['widget'].delete(0)
        self.info_area['widget'].configure(state = 'normal')
        self.info_area['widget'].insert(tk.INSERT,f_msg)
        self.info_area['widget'].configure(state = 'disabled')


    """

    Event handlers

    """

    def cell_clicked(self, event):
        x = event.x
        y = event.y

        if not ( self.in_bounds(x, self.__board_width) and self.in_bounds(y, self.__board_height) ):
            return

        self.board.focus_set()

        cell = self.find_cell(x, y)
        if cell and not cell.default:
            #print(cell.__dict__)
            self.set_current_cell(cell)

    def key_pressed(self, event):
        if not event.char.isnumeric():
            return 

        val = int(event.char)
        if val > 0 and val < 10:
            self.reset_cell_value()
            self.set_cell_value(val)

    def arrow_key_pressed(self, event, dir):
        if not self.current_cell:
            return

        if dir == 'UP':
            self.move_cell_up()
        elif dir == 'DOWN':
            self.move_cell_down()
        elif dir == 'LEFT':
            self.move_cell_left()
        elif dir == 'RIGHT':
            self.move_cell_right()

    def on_input_click(self, event, num):
        if not self.current_cell:
            return
        
        self.reset_cell_value()
        if num != 'X':
            val = int(num) + 1
            self.set_cell_value(val)
            
            
        if self.board_invalid and num == 'X':
            self.validate_board()

    def on_option_click(self, event, opt):
        if opt == 'NEW':
            print('Generate new {0} puzzle'.format(self.difficulty.get()))
            self.get_new_board()
        elif opt == 'CLEAR':
            self.reset_all_user_values()
        elif opt == 'VALIDATE':
            self.validate_board()
        else:
            self.solve_board()


    """

    Cell logic methods

    """

    def set_current_cell(self, cell):
        self.draw_current_cell(cell)
        self.current_cell = cell

    def move_cell_up(self):
        if self.current_cell.row == 0:
            return

        new_row = self.current_cell.row-1
        for i, r in enumerate(reversed(self.cells)):
            if i >= (8 - new_row):
                cell = next((c for c in r if c.col == self.current_cell.col and not c.default), None)
                if cell:
                    self.set_current_cell(cell)
                    break

    def move_cell_down(self):
        if self.current_cell.row == 8:
            return

        new_row = self.current_cell.row+1
        for i, r in enumerate(self.cells):
            if i >= new_row:
                cell = next((c for c in r if c.col == self.current_cell.col and not c.default), None)
                if cell:
                    self.set_current_cell(cell)
                    break

    def move_cell_right(self):
        if self.current_cell.col == 8:
            return

        for i, r in enumerate(self.cells):
            if i != self.current_cell.row:
                continue
            cell = next((c for c in r if c.col >= self.current_cell.col+1 and not c.default), None)
            if cell:
                self.set_current_cell(cell)
                break

    def move_cell_left(self):
        if self.current_cell.col == 0:
            return

        for i, r in enumerate(self.cells):
            if i != self.current_cell.row:
                continue
            cell = next((c for c in reversed(r) if c.col <= self.current_cell.col-1 and not c.default), None)
            if cell:
                self.set_current_cell(cell)
                break

    def reset_all_user_values(self):
        for row in self.cells:
            for cell in row:
                if not cell.default:
                    cell.value = 0
                    self.erase_cell_value(cell)
        self.set_info_text("Resetting board.")
        self.validate_board()

    def reset_cell_value(self):
        self.current_cell.value = 0
        self.erase_cell_value(self.current_cell)

    def set_cell_value(self, value):
        self.current_cell.value = value
        self.draw_cell_value(self.current_cell)

    def validate_board(self):
        try:
            self.set_info_text("Validating board...")
            raw_board = self.get_raw_board()
            result = sudoku_helper.validate_board(raw_board)
            self.reset_invalid_flag()
            self.handle_invalid_rows(result['rows'])
            self.handle_invalid_cols(result['columns'])
            self.handle_invalid_squares(result['squares'])

            self.mark_invalid_cells()
            self.set_info_text("Validation complete.")
        except Exception as ex:
            self.set_info_text("Exception: {}".format(ex))
            raise

    def reset_invalid_flag(self):
        self.board_invalid = False
        for row in self.cells:
            for cell in row:
                cell.invalid = False

    def handle_invalid_rows(self, rows):
        for row, valid in enumerate(rows):
            if valid != 0:
                continue
            self.set_info_text('Row {0} is invalid.'.format(row+1))
            self.board_invalid = True
            for cell in self.cells[row]:
                if not cell.default:
                    cell.invalid = True

    def handle_invalid_cols(self, cols):
        for col, valid in enumerate(cols):
            if valid != 0:
                continue
            self.set_info_text('Column {0} is invalid.'.format(col+1))
            self.board_invalid = True
            for row in range(len(self.cells)):
                if not self.cells[row][col].default:
                    self.cells[row][col].invalid = True

    def handle_invalid_squares(self, squares):
        for s, square in enumerate(squares):
            if square != 0:
                continue
            min_col = 3 * (s % 3)
            max_col = min_col + (3 - 1)
            min_row = 3 * (s // 3)
            max_row = min_row + (3 - 1)
            self.set_info_text('Square {0} is invalid.'.format(s+1))
            self.board_invalid = True
            for i in range(min_row, max_row+1):
                for j in range(min_col, max_col+1):
                    if not self.cells[i][j].default:
                        self.cells[i][j].invalid = True

    def solve_board(self):
        try:
            raw_board = self.get_raw_board()
            result = sudoku_helper.solve_board(raw_board)
            self.set_info_text("Solving board...")
            if not result['board']:
                self.set_info_text("Could not solve board!")
                self.validate_board()
                return
            
            self.set_info_text("Yay!  Board solved!")
            for i, row in enumerate(result['board']):
                for j, val in enumerate(row):
                    if self.cells[i][j].value == 0:
                        self.cells[i][j].value = val
                        self.draw_cell_value(self.cells[i][j], "green")
        except Exception as ex:
            self.set_info_text("Exception: {}".format(ex))
            raise

        self.validate_board()

    """

    Helper methods

    """

    def in_bounds(self, coord, edge):
        return self.__margin < coord and coord < edge - self.__margin

    def find_cell(self, x, y):

        for row in self.cells:
            for cell in row:
                if cell.point_in_cell(x, y):
                    return cell

        return None

    def get_new_board(self):
        #url = 'http://www.websudoku.com/?level={0}'.format(self.difficulty.get())
        #print(url)
        url = 'https://www.sudokuweb.org/'
        board = get_new_board(url)
        if not board:
            return

        self.draw_new_board(board)

    def get_raw_board(self):
        board = []
        for row in self.cells:
            board_cols = []
            for cell in row:
                board_cols.append(cell.value)
            board.append(board_cols)

        return board


        

