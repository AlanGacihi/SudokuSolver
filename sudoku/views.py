from django.shortcuts import render
from . import sudoku
import time

# Create your views here.

def index(request):
    """
    Default index. Renders a form and produces an image as solution
    """
    if request.method == "POST":
        assignment = {}
        for i in range(9):
            for j in range(9):
                if request.POST[f"({i}, {j})"]:
                    assignment[(i, j)] = int(request.POST[f"({i}, {j})"])


        if len(assignment) == 0:
            time.sleep(2)
            return render(request, "sudoku/output.html", {
                "output1": True
            })

               
        valid = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for value in assignment.values():
            if value not in valid:
                time.sleep(2)
                return render(request, "sudoku/output.html", {
                    "message": "Input values should be between 0 and 10!"
                })


        if sudoku.SudokuSolver(sudoku.Sudoku(assignment)).solve():
            return render(request, "sudoku/output.html", {
                "output1": False
            })

        else:
            time.sleep(2)
            return render(request, "sudoku/output.html",  {
                "message": "Couldn't solve the sudoku puzzle!"
            })

    else:    
        return render(request, "sudoku/index.html")
