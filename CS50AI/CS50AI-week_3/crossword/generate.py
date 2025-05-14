import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # For hver variabel i self.domains
        for variable in self.domains:
            # For hver variabel i self.domains går vi igennem settet af alle ord der kan udfylde variablens plads i krydsordet
            for word in list(self.domains[variable]):
                # Hvis længden af ordet ikke er lig med længden af variablen fjerner vi ordet fra settet tilknyttet variablen
                if len(word) != variable.length:
                    self.domains[variable].remove(word)



    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        if not overlap:
            return False
        x_index, y_index = overlap

        removed = False
        for word_x in self.domains[x].copy():
            found_match = False
            for word_y in self.domains[y].copy():
                if word_x[x_index] == word_y[y_index]:
                    found_match = True
                    break

            if not found_match:
                self.domains[x].remove(word_x)
                removed = True

        return removed



    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = []
            for x in self.crossword.variables:
                for y in self.crossword.variables:
                    if not x == y:
                        if self.crossword.overlaps[x, y]:
                            arcs.append((x, y))

        while arcs:
            (x, y) = arcs.pop(0)
            consistent = self.revise(x, y)

            if consistent:
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        arcs.append((z, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for variable in self.crossword.variables:
            if not variable in assignment.keys():
                return False
        return True



    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        for variable in assignment:
            if len(assignment[variable]) != variable.length:
                return False

        assigned_words = list(assignment.values())
        if len(assigned_words) != len(set(assigned_words)):
            return False

        for x in self.crossword.variables:
            for y in self.crossword.variables:
                if x in assignment and y in assignment:
                    if x != y and self.crossword.overlaps[x, y]:
                        i, j = self.crossword.overlaps[x, y]
                        if assignment[x][i] != assignment[y][j]:
                            return False

        return True



    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        candidate_scores = []
        for value in self.domains[var]:
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    if self.crossword.overlaps[var, neighbor]:
                        i, j = self.crossword.overlaps[var, neighbor]
                        for neighbor_value in self.domains[neighbor]:
                            if value[i] != neighbor_value[j]:
                                count += 1
            candidate_scores.append((value, count))

        candidate_scores.sort(key=lambda pair: pair[1])
        ordered_values = [value for value, score in candidate_scores]
        return ordered_values





    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        unassigned_variables = []
        for variable in self.crossword.variables:
            if not variable in assignment:
                unassigned_variables.append(variable)

        best = unassigned_variables[0]
        for unassigned_variable in unassigned_variables:
            if len(self.domains[unassigned_variable]) < len(self.domains[best]):
                best = unassigned_variable
            if len(self.domains[unassigned_variable]) == len(self.domains[best]):
                if len(self.crossword.neighbors(unassigned_variable)) > len(self.crossword.neighbors(best)):
                    best = unassigned_variable

        return best





    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        complete = self.assignment_complete(assignment)
        if complete:
            return assignment
        else:
            unassigned_variable = self.select_unassigned_variable(assignment)
            words = self.order_domain_values(unassigned_variable, assignment)


            for word in words:
                copy_assignment = assignment.copy()
                copy_assignment[unassigned_variable] = word
                consistent = self.consistent(copy_assignment)
                if consistent:
                    complete_assignment = self.backtrack(copy_assignment)
                    if self.assignment_complete(complete_assignment):
                        return complete_assignment
            return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
