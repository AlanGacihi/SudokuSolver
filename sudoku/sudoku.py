class Sudoku():
    """
    Represents a sudoku puzzle.
    """
    def __init__(self, assignment):

        self.board = []
        self.cells = set()
        self.assignment = assignment

        # Initialize an empty board
        for i in range(9):
            row = []
            for j in range(9):
                self.cells.add((i, j))
                row.append(None)
            self.board.append(row)

        # Allocate values in the assignment
        for cell in self.assignment:
            self.board[cell[0]][cell[1]] = assignment[cell]

    def print_board(self):   
        """
        Print the sudoku puzzle.
        """
        print("\n-------------------------")
        for i in range(9):
            for j in range(9):
                if j == 0:
                    print("|", end=" ")
                print(f"{self.board[i][j]} ",end="")
                if (j + 1) % 3 == 0:
                    print("|", end=" ")
            if (i + 1) % 3 == 0:
                print("\n-------------------------", end=" ")
            print()

    def draw_board(self, old_assignment):
        """
        Save sudoku assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 40
        cell_border = 1.2
        interior_size = cell_size - 2 * cell_border

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (9 * cell_size,
             9 * cell_size),
            "black"
        )
        font = ImageFont.truetype(r"assets\fonts\OpenSans-Regular.ttf", 25, encoding="unic")
        draw = ImageDraw.Draw(img)

        for i in range(9):
            for j in range(9):
                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if (i in [3, 4, 5] or j in [3, 4, 5]) and not (i in [3, 4, 5] and j in [3, 4, 5]):
                    draw.rectangle(rect, fill="#32CD32")
                else:
                    draw.rectangle(rect, fill="white")

                if self.board[i][j]:
                    w, h = draw.textsize(str(self.board[i][j]), font=font)
                    draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 4),
                            str(self.board[i][j]), fill="black" if (i, j) in old_assignment else "red", font=font
                        )

        img.save("sudoku/static/sudoku/output.png")


    def neighbours(self, cell):
        """Given a cell, return set of its neighbours."""
        
        neighbours = set()
        for i in range(9):
            neighbours.add((cell[0], i))
            neighbours.add((i, cell[1]))

        for i in range((cell[0] // 3) * 3, ((cell[0] // 3) * 3) + 3):
            for j in range((cell[1] // 3 * 3), ((cell[1] // 3) * 3) + 3):
                neighbours.add((i, j))

        neighbours.remove(cell)
        return neighbours


class SudokuSolver():
    def __init__(self, sudoku):
        """
        Create new CSP sudoku generate.
        """
        self.sudoku = sudoku
        self.domains = {
            cell: {1, 2, 3, 4, 5, 6, 7, 8, 9}
            if cell not in self.sudoku.assignment
            else
            {self.sudoku.assignment[cell]}
            for cell in self.sudoku.cells
        }

    def solve(self):
        """
        Enforce arc consistency, and then solve the CSP.
        """
        if not self.consistent(self.sudoku.assignment):
            return False
        self.ac3()
        complete_assignment = self.backtrack(self.sudoku.assignment.copy())
        Sudoku(complete_assignment).draw_board(self.sudoku.assignment)
        return True

    def revise(self, x, y):
        """
        Make cell `x` arc consistent with cell `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        """
        for v1 in self.domains[x].copy():
            for v2 in self.domains[y]:
                if v1 == v2:
                    self.domains[x].remove(v1)
                    break

    def ac3(self):
        """
        Update `self.domains` such that each cell is arc consistent.
        """
        queue = []
        for cell in self.sudoku.assignment:
            for neighbour in self.sudoku.neighbours(cell):
                queue.append((neighbour, cell))
        while queue:
            x, y = queue.pop(0)
            self.revise(x, y)
            if len(self.domains[x]) == 0:
                    return False
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        sudoku cell); return False otherwise.
        """
        if self.sudoku.cells == set(assignment):
            return True
        return False


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., numbers fit in sudoku
        puzzle without conflicting); return False otherwise.
        """
        for cell in assignment:
            for neighbour in self.sudoku.neighbours(cell):
                if neighbour in assignment:
                    if assignment[neighbour] == assignment[cell]:
                        return False
        return True

    def order_domain_values(self, cell, assignment):
        """
        Return a list of values in the domain of `cell`, in order by
        the number of values they rule out for neighboring cells.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `cell`.
        """
        v = {}
        for value in self.domains[cell]:
            v[value] = 0
            for neighbour in self.sudoku.neighbours(cell) - set(assignment):
                if value in self.domains[neighbour]:
                    v[value] += 1

        return sorted(v, key=lambda x: v[x])

    def select_unassigned_cell(self, assignment):
        """
        Return an unassigned cell not already part of `assignment`.
        Choose the cell with the minimum number of remaining values
        in its domain. If there is a tie, choose the cell with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_cells = {}
        for cell in self.sudoku.cells - set(assignment):
            unassigned_cells[cell] = (len(self.domains[cell]), len(self.sudoku.neighbours(cell)))

        return sorted(unassigned_cells, key=lambda x: unassigned_cells[x])[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        sudoku and return a complete assignment if possible to do so.

        `assignment` is a mapping from cells (keys) to numbers (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        cell = self.select_unassigned_cell(assignment)

        for value in self.order_domain_values(cell, assignment):
            assignment[cell] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result != None:
                    return result
            del assignment[cell]

        return None
