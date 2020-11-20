#define PY_SSITE_T_CLEAN
#include <Python.h>
#include <stdbool.h>

#if PY_MAJOR_VERSION >= 3
#define PY3K
#endif

struct board 
{
    struct boardCell **cells;
    int rows;
    int cols;
};

struct boardCell 
{
    int row;
    int col;
    int value;
    bool isDefault;
};

int initializeBoard(PyObject*, struct board*);
int freeBoard(struct board*);
PyObject* validateBoard(struct board*);
int isBoardValid(struct board*);
void printBoard(struct board*);

bool contains(int*, int, int);

int validateRows(struct boardCell**, int, int*);
int validateCols(struct boardCell**, int, int, int*);
int validateSquares(struct boardCell**, int, int, int*);

bool inRow(struct boardCell**, int, int, int);
bool inColumn(struct boardCell**, int, int, int);
bool inSquare(struct boardCell**, int, int, int);

bool canUseValue(struct board*, int, int, int, int);

void nextBlankCell(struct board*, int*);

int solveBoard(struct board*, int, int);

PyObject* getBoard(struct board*);



static PyObject *method_validate_board(PyObject *self, PyObject *args){
    PyObject *input;

    if(!PyArg_ParseTuple(args, "O", &input)){
        return NULL;
    }

    int length;
    length = PyObject_Length(input);
    if(length < 0){
        return NULL;
    }

    struct board b;
    int success = initializeBoard(input, &b);
    if(success < 0){
        return NULL;
    }
    PyObject *boardValidation = validateBoard(&b);
    success = freeBoard(&b);

    return boardValidation;
}

static PyObject *method_solve_board(PyObject *self, PyObject *args){
    PyObject *input;

    if(!PyArg_ParseTuple(args, "O", &input)){
        return NULL;
    }

    int length;
    length = PyObject_Length(input);
    if(length < 0){
        return NULL;
    }

    struct board b;
    int success = initializeBoard(input, &b);
    if(success < 0){
        return NULL;
    }
    success = isBoardValid(&b);
    if(success < 0){
        return NULL;
    }else if(!success){
        freeBoard(&b);
        Py_IncRef(Py_None);
        return Py_BuildValue("{s:s,s:O}", "result", "Board is invalid.", "board", Py_None);
    }

    int solved = solveBoard(&b, 0, 0);
    if(solved < 0){
        freeBoard(&b);
        return NULL;
    }else if(!solved){
        freeBoard(&b);
        Py_IncRef(Py_None);
        return Py_BuildValue("{s:s,s:O}", "result", "Board cannot be solved.", "board", Py_None);
    }

    PyObject* result = getBoard(&b);
    success = freeBoard(&b);

    return Py_BuildValue("{s:s,s:O}", "result", "Board solved!.", "board", result);
}

PyDoc_STRVAR(module_docs, "Provides helper methods to validate and/or solve a sudoku board.\n" );
PyDoc_STRVAR(validate_board_docs, "validate_board():  pass in a board to validate\n" );
PyDoc_STRVAR(solve_board_docs, "validate_board():  pass in a board to get a solution.\n" );

static PyMethodDef sudoku_helper_methods[] = {
    {"validate_board", (PyCFunction)method_validate_board, METH_VARARGS, validate_board_docs},
    {"solve_board", (PyCFunction)method_solve_board, METH_VARARGS, solve_board_docs},
    {NULL, NULL, 0, NULL}
};

#ifdef PY3K
static struct PyModuleDef sudoku_helper_module = {
    PyModuleDef_HEAD_INIT,
    "sudoku_helper",
    module_docs,
    -1,
    sudoku_helper_methods
};

PyMODINIT_FUNC PyInit_sudoku_helper()
{
    Py_Initialize();
    return PyModule_Create(&sudoku_helper_module);
}

#else

PyMODINIT_FUNC initModule(){
    return Py_InitModule3("sudoku_helper", sudoku_helper_methods, "Python interface for sudoku help C library.");
}

#endif

int initializeBoard(PyObject *inputBoard, struct board *b){
    int length;
    length = PyObject_Length(inputBoard);
    if(length < 0){
        PyErr_SetString(PyExc_Exception, "initializeBoard():  Invalid board size.");
        return -1;
    }

    struct boardCell **cellsPtr;
    cellsPtr = (struct boardCell **) calloc(length, sizeof(struct boardCell *));
    if(cellsPtr == NULL){
        free(cellsPtr);
        PyErr_SetString(PyExc_Exception, "initializeBoard():  Could not allocate cells memory.");
        return -1;
    }

    b->cells = cellsPtr;
    for(int row = 0; row < length; row++){
        PyObject *columns;
        columns = PyList_GetItem(inputBoard, row);
        int colsLength = PyObject_Length(columns);
        if(colsLength < 0){
            freeBoard(b);
            PyErr_SetString(PyExc_Exception, "initializeBoard():  Invalid column length.");
            return -1;
        }

        struct boardCell *rowsPtr;
        rowsPtr = (struct boardCell *) calloc(colsLength, sizeof(struct boardCell));

        if(rowsPtr == NULL){
            free(rowsPtr);
            freeBoard(b);
            PyErr_SetString(PyExc_Exception, "initializeBoard():  Could not allocate rows memory.");
            return -1;
        }
        b->cells[row] = rowsPtr;

        for(int col = 0; col < colsLength; col++){
            PyObject *cell;
            cell = PyList_GetItem(columns, col);
            if(!PyLong_Check(cell)){
                freeBoard(b);
                PyErr_SetString(PyExc_Exception, "initializeBoard():  Invalid board character.");
                return -1;
            }
            (b->cells[row][col]).row = row;
            (b->cells[row][col]).col = col;
            (b->cells[row][col]).value = (int)PyLong_AsLong(cell);
            (b->cells[row][col]).isDefault = cell != 0;
        }
        
        if(row == 0){
            b->cols = colsLength;
        }
    }
    b->rows = length;

    return 0;
}

int freeBoard(struct board *b){

    for(int i= 0; i < b->rows; i++){
        free(b->cells[i]);
        b->cells[i] = NULL;
    }
    free(b->cells);
    b->cells = NULL;
    b->rows = 0;
    b->cols = 0;

    return 0;
}

bool contains(int *values, int size, int value){
    for(int i = 0; i < size; i++){
        if(*(values+i) == value){
            return true;
        }
    }

    return false;
}

int validateRows(struct boardCell **cells, int numRows, int* result){

    int *validInput = (int *)calloc(numRows, sizeof(int));
    if(validInput == NULL){
        free(validInput);
        PyErr_SetString(PyExc_Exception, "validateRows():  Unable to allocate validInput memory.");
        return -1;        
    }

    int *prevValues = (int *)calloc(numRows, sizeof(int));
    if(prevValues == NULL){
        free(validInput);
        free(prevValues);
        PyErr_SetString(PyExc_Exception, "validateRows():  Unable to allocate prevValues memory.");
    }

    for(int i = 0; i < numRows; i++){
        *(validInput + i) = (i+1);
        *(prevValues + i) = 0;
    }

    for(int row= 0; row < numRows; row++){
        int value, numPrevValues = 0, valid = 1;
        for(int col = 0; col < numRows; col++){
            value = (*(cells+row)+col)->value;
            if(value == 0){
                continue;
            }
            //verify only numbers 1-9 in row
            if(!contains(validInput, numRows, value)){          
                valid = 0;
                break;
            }
            //verify only 1 of numbers 1-9 in row
            if(contains(prevValues, numPrevValues, value)){
                valid = 0;
                break;
            }
            *(prevValues + numPrevValues++) = value;
        }
        for(int i = 0; i < numRows; i++){
            *(prevValues+i) = 0;
        }
        *(result+row) = valid;
    }

    free(validInput);
    free(prevValues);
    return 0;
}

int validateColumns(struct boardCell **cells, int numRows, int numCols, int* result)
{
    int *prevValues = (int *)calloc(numCols, sizeof(int));
    if(prevValues == NULL){
        PyErr_SetString(PyExc_Exception, "areColumnsValid():  Unable to allocate prevValues memory.");
        return -1;
    }

    for(int i = 0; i < numCols; i++){
        *(prevValues + i) = 0;
    }

    for(int col= 0; col < numCols; col++){
        int value, numPrevValues = 0, valid = 1;
        for(int row = 0; row < numRows; row++){
            //if value == 0, no value in cell
            value = (*(cells+row)+col)->value;
            if(value == 0){
                continue;
            }
            //verify only 1 of numbers 1-9 in column
            if(contains(prevValues, numPrevValues, value)){
                valid = 0;
                break;
            }
            *(prevValues + numPrevValues++) = value;
        }
        for(int j = 0; j < numCols; j++){
            *(prevValues+j) = 0;
        }
        *(result+col) = valid;
    }

    free(prevValues);
    return 0;
}

int validateSquares(struct boardCell **cells, int numRows, int squareRows, int *result)
{
    int *prevValues = (int *)calloc(numRows, sizeof(int));
    if(prevValues == NULL){
        free(prevValues);
        PyErr_SetString(PyExc_Exception, "validateSquares():  Unable to allocate prevValues memory.");
        return -1;
    }

    for(int i = 0; i < numRows; i++){
        *(prevValues + i) = 0;
    }

    for(int s = 0; s < (squareRows*squareRows); s++){

        int minCol = squareRows * (s % squareRows);
        int maxCol = minCol + (squareRows - 1);
        int minRow = squareRows * (s / squareRows);
        int maxRow = minRow + (squareRows - 1);
        int value, numPrevValues = 0, valid = 1;
        for(int row = minRow; row <= maxRow; row++){
            
            for(int col = minCol; col <= maxCol; col++){
                //if value == 0, no value in cell
                value = (*(cells+row)+col)->value;
                if( value == 0){
                    continue;
                }
                //verify only 1 of numbers 1-9 in square
                if(contains(prevValues, numPrevValues, value)){
                    valid = 0;
                    break;
                }
                *(prevValues + numPrevValues++) = value;
            }
            if(valid == 0){
                break;
            }
        }

        for(int i = 0; i < numRows; i++){
            *(prevValues+i) = 0;
        }
        *(result+s) = valid;
    }

    free(prevValues);
    return 0;
}

PyObject* validateBoard(struct board *b){
    
    int *result = (int *)calloc(b->rows, sizeof(int));
    if(result == NULL){
        free(result);
        PyErr_SetString(PyExc_Exception, "validateBoard():  Unable to allocate result memory.");
        return (PyObject*) NULL;
    }
    for(int i = 0; i < b->rows; i++){
        *(result+i) = 0;
    }

    int success = validateRows(b->cells, b->rows, result);
    if(success < 0){
        free(result);
        return (PyObject*) NULL;
    }
    PyObject *rowValidation = PyList_New(b->rows);
    for(int i =0; i < b->rows; i++){
        PyList_SetItem(rowValidation, i, Py_BuildValue("i", result[i]));
        *(result+i) = 0;
    }

    success = validateColumns(b->cells, b->rows, b->cols, result);
    if(success < 0){
        free(result);
        return (PyObject*) NULL;
    }
    PyObject *columnValidation = PyList_New(b->cols);
    for(int i =0; i < b->cols; i++){
        PyList_SetItem(columnValidation, i, Py_BuildValue("i", result[i]));
        *(result+i) = 0;
    }

    success = validateSquares(b->cells, b->rows, 3, result);
    if(success < 0){
        free(result);
        return (PyObject*) NULL;
    }
    PyObject *squaresValidation = PyList_New(9);
    for(int i =0; i < b->cols; i++){
        PyList_SetItem(squaresValidation, i, Py_BuildValue("i", result[i]));
        *(result+i) = 0;
    }

    free(result);

    return Py_BuildValue("{s:O,s:O,s:O}", "rows", rowValidation, "columns", columnValidation, "squares", squaresValidation); 
}

int isBoardValid(struct board *b){
    
    int *result = (int *)calloc(b->rows, sizeof(int));
    if(result == NULL){
        free(result);
        PyErr_SetString(PyExc_Exception, "isBoardValid():  Unable to allocate result memory.");
        return -1;
    }
    for(int i = 0; i < b->rows; i++){
        *(result+i) = 0;
    }

    int success = validateRows(b->cells, b->rows, result);
    if(success < 0){
        free(result);
        return -1;
    }
    bool rowValidation = 1;
    for(int i =0; i < b->rows; i++){
        if(result[i] == 0){
            rowValidation = 0;
        }
        *(result+i) = 0;
    }

    success = validateColumns(b->cells, b->rows, b->cols, result);
    if(success < 0){
        free(result);
        return -1;
    }
    bool columnValidation = 1;
    for(int i =0; i < b->rows; i++){
        if(result[i] == 0){
            columnValidation = 0;
        }
        *(result+i) = 0;
    }

    success = validateSquares(b->cells, b->rows, 3, result);
    if(success < 0){
        free(result);
        return -1;
    }
    bool squaresValidation = 1;
    for(int i =0; i < b->rows; i++){
        if(result[i] == 0){
            squaresValidation = 0;
            break;
        }
        *(result+i) = 0;
    }

    free(result);

    return rowValidation == 1 && columnValidation == 1 && squaresValidation == 1;
}

bool inRow(struct boardCell **cells, int row, int numCols, int value){
    for(int col = 0; col < numCols; col++){
        if((*(cells+row)+col)->value == value){
            return true;
        }
    }
    return false;
}

bool inColumn(struct boardCell **cells, int col, int numRows, int value){
    for(int row = 0; row < numRows; row++){
        if((*(cells+row)+col)->value == value){
            return true;
        }
    }
    return false;
}

bool inSquare(struct boardCell **cells, int square, int squareRows, int value){

    int minCol = squareRows * (square % squareRows);
    int maxCol = minCol + (squareRows - 1);
    int minRow = squareRows * (square / squareRows);
    int maxRow = minRow + (squareRows - 1);

    for(int row = minRow; row <= maxRow; row++){            
        for(int col = minCol; col <= maxCol; col++){
            if((*(cells+row)+col)->value == value){
                return true;
            }
        }
    }

    return false;
}

bool canUseValue(struct board *b, int row, int col, int squareRows, int value){

    int square = 3*(row / squareRows) + (col / squareRows);
    return !inRow(b->cells, row, b->cols, value)
        && !inColumn(b->cells, col, b->rows, value)
        && !inSquare(b->cells, square, squareRows, value);

}

void nextBlankCell(struct board *b, int *nextCell){
    for(int i = 0; i < b->rows; i++){
        for(int j = 0; j < b->cols; j++){
            int value = (*(b->cells+i)+j)->value;
            if(value == 0){
                nextCell[0] = i;
                nextCell[1] = j;
                return;
            }
        }
    }
    nextCell[0] = -1;
    nextCell[1] = -1;
    return;
}

int solveBoard(struct board *b, int row, int col){

    int *nextCell = (int *)calloc(2, sizeof(int));
    if(nextCell == NULL){
        free(nextCell);
        PyErr_SetString(PyExc_Exception, "solvePuzzle():  Unable to allocate nextCell memory.");
        return -1;
    }

    nextBlankCell(b, nextCell);

    //board is full
    if(nextCell[0] < 0 && nextCell[1] < 0){
        return 1;
    }

    int *validInput = (int *)calloc(b->rows, sizeof(int));
    if(validInput == NULL){
        free(nextCell);
        free(validInput);
        PyErr_SetString(PyExc_Exception, "solvePuzzle():  Unable to allocate validInput memory.");
        return -1;
    }

    for(int i = 0; i < b->rows; i++){
        *(validInput + i) = (i+1);
    }

    for(int i = 0; i < b->rows; i++){
        if(canUseValue(b, nextCell[0], nextCell[1], 3, *(validInput+i))){

            (*(b->cells+nextCell[0])+nextCell[1])->value = *(validInput+i);
            int success = solveBoard(b, nextCell[0], nextCell[1]);
            if(success != 0){
                free(validInput);
                free(nextCell);
                return success;
            }

            (*(b->cells+nextCell[0])+nextCell[1])->value = 0;
        }
    }

    free(validInput);
    free(nextCell);
    return 0;
}

PyObject* getBoard(struct board *b){
    PyObject *rows = PyList_New(b->rows);
    for(int row = 0; row < b->rows; row++){
        PyObject *cells = PyList_New(b->rows);
        for(int col = 0; col < b->cols; col++){
            PyList_SetItem(cells, col, Py_BuildValue("i", (b->cells[row][col]).value));
        }
        PyList_SetItem(rows, row, Py_BuildValue("O", cells));
    }

    return rows;
}

void printBoard(struct board *b){
    for(int row = 0; row < b->rows; row++){
        for(int col = 0; col < b->cols; col++){
            printf("(%i,%i): %i\t", row, col, (b->cells[row][col]).value);
        }
        printf("\n");
    }
}