import tkinter as tk
#from tkinter import Canvas
import tkinter.scrolledtext as st
from tkinter.messagebox import showerror

from board import Board

class Window(object):

    __screen_width = 760
    __screen_height = 500

    def __init__(self, sudoku_board):

        self.window = tk.Tk()
        self.cells = sudoku_board

        self.window.title('Sudoku')
        self.window.geometry('{0}x{1}'.format(self.__screen_width, self.__screen_height))
        self.window.config(bg="#fff")

        self.board = None

        self.build_window()

    def build_window(self):
        self.build_puzzle_component()
        self.build_input_component()

        self.window.resizable(False,False)
        self.board.set_info_text("Board initialized.")
        tk.Tk.report_callback_exception = self.handle_exceptions
        self.window.mainloop()

    def handle_exceptions(self, exc, val, tb):
        showerror('Error', message=(str(val)))
        print("Found exception...exiting program.")
        exit(1)

        
    def build_puzzle_component(self):
        puzzle_label = tk.Label(self.window, text='Your puzzle is below.  Good luck!', bg="#fff", fg="#000")
        puzzle_label.config(font=("Arial", 16))
        puzzle_frame = tk.Frame(self.window, bg="#fff")

        self.board = Board(puzzle_frame, self.cells)
        self.board.init_board()

        puzzle_label.grid(row=0, column=0, columnspan=2)
        puzzle_frame.grid(row=1,column=0, sticky="N")

    def build_input_component(self):
        user_input_frame = tk.Frame(self.window, bg='#fff')
        user_input_frame.rowconfigure(0)
        user_input_frame.rowconfigure(1)
        user_input_frame.rowconfigure(2, minsize=185)

        input_frame = tk.LabelFrame(user_input_frame, bg='#fff', text='Input:', fg="#000", padx=25, pady=10 )
        puzzle_options_frame = tk.LabelFrame(user_input_frame, bg='#fff', text='Puzzle Options:', fg='#000', padx=10, pady=10)
        info_frame = tk.LabelFrame(user_input_frame, bg='#fff', text='Info:', fg='#000', pady=5)

        user_input_frame.grid(row=1,column=1, sticky="N")

        input_frame.grid(row=0,column=0, sticky="EW")
        puzzle_options_frame.grid(row=1, column=0, sticky="EW")
        info_frame.grid(row=2,column=0, sticky="NEW")

        for i in range(9):
            btn = tk.Button(input_frame, text='{0}'.format(i+1), highlightbackground="#fff", fg="#000")
            if i < 5:
                btn.grid(row=0, column=i)
            else:
                btn.grid(row=1, column=(i-5))
            btn.bind('<Button-1>', lambda event, arg=i: self.board.on_input_click(event, arg))

        erase_btn = tk.Button(input_frame, text='X', highlightbackground="#fff", fg="#000")
        erase_btn.grid(row=1, column=4)
        erase_btn.bind('<Button-1>', lambda event, arg='X': self.board.on_input_click(event, arg))

        clear_btn = tk.Button(input_frame, text="Clear All Answers",highlightbackground="#fff", fg="#000", width=10)
        clear_btn.grid(row=2, column=0, columnspan=5, pady=5)
        clear_btn.bind('<Button-1>', lambda event, arg='CLEAR': self.board.on_option_click(event, arg))
        
        self.build_options_component(puzzle_options_frame)
        self.build_info_component(info_frame)

    def build_options_component(self, frame):
        diff_label = tk.Label(frame, text="Difficulty:", bg='#fff',highlightbackground='#fff', fg='#000')
        easy_rb = tk.Radiobutton(frame, text='Easy', variable=self.board.difficulty, value=1, bg='#fff', fg='#000')
        med_rb = tk.Radiobutton(frame, text='Medium', variable=self.board.difficulty, value=2, bg='#fff', fg='#000')
        hard_rb = tk.Radiobutton(frame, text='Hard', variable=self.board.difficulty, value=3, bg='#fff', fg='#000')
        new_btn = tk.Button(frame, text="New", highlightbackground="#fff", fg="#000", width=10)
        validate_btn = tk.Button(frame, text="Validate",highlightbackground="#fff", fg="#000", width=10)
        solve_btn = tk.Button(frame, text="Solve",highlightbackground="#fff", fg="#000", width=10)

        diff_label.grid(row=0, column=0)
        easy_rb.grid(row=0, column=1)
        med_rb.grid(row=0, column=2)
        hard_rb.grid(row=0, column=3)
        new_btn.grid(row=1, column=0, columnspan=4, pady=5)
        new_btn.bind('<Button-1>', lambda event, arg='NEW': self.board.on_option_click(event, arg))
        validate_btn.grid(row=2, column=0, columnspan=4, pady=5)
        validate_btn.bind('<Button-1>', lambda event, arg='VALIDATE': self.board.on_option_click(event, arg))
        solve_btn.grid(row=3, column=0, columnspan=4, pady=5)
        solve_btn.bind('<Button-1>', lambda event, arg='SOLVE': self.board.on_option_click(event, arg))

    def build_info_component(self, frame):
        info_area = st.ScrolledText(master=frame, width=30, height=8, font=("Arial", 12), bg='#fff', fg='#000', borderwidth=0, highlightthickness=1)
        #label = tk.Label(frame, text="Test label")
        #info_area.grid(row=0, column=0, sticky="NE", padx=5)
        info_area.pack(padx=5, fill=tk.BOTH)
        self.board.set_info_area(info_area)