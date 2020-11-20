from distutils.core import setup, Extension

def main():
    setup(name="sudoku_helper",
          version="1.0.0",
          description="Python interface for the sudoku helper C library function",
          author="jjc",
          author_email="jared.casey@couchbase.com",
          ext_modules=[Extension("sudoku_helper", sources=["sudoku_helper.c"])])

if __name__ == "__main__":
    main()