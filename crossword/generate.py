import sys
from copy import deepcopy

from crossword import *


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
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
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/foself.domainsnts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
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
        # Taking the length Constraint from Variable object and removing
        # words which doesn't match the length constraint from its domain
        for variable, domain in self.domains.items():
            len_constraint = variable.length
            eligible_words = [word for word in domain if len(word) == len_constraint]
            self.domains[variable] = set(eligible_words)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # checking for conflicts between X and Y
        # if there is a conflict then there is no need of removing words from X.domain
        # because we need more words to alter the exact conflict
        overlap = self.crossword.overlaps[x, y]
        if overlap:
            return False

        # Subtracting the intersection of X.domain and Y.domain from X.domain
        x_domain = self.domains[x]
        y_domain = self.domains[y]
        to_remove = set()  # Its the intersection
        revise = False

        for word in x_domain:
            if word in y_domain:
                to_remove.add(word)
                revise = True

        x_domain -= to_remove  # Job Done
        return revise

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # if there is no arcs constraints then
        # add the subsets of x.variable and y.variable
        # actually the keys in x.variable and y.variable
        if arcs is None:
            arcs = []
            for v1 in self.domains:
                for v2 in self.domains:
                    if v1 == v2:
                        continue
                    arcs.append((v1, v2))

        # The main working of AC-3
        while arcs:
            v1, v2 = arcs.pop(0)
            if self.revise(v1, v2):
                if len(self.domains[v1]) == 0:
                    return False
                for v3 in self.crossword.neighbors(v1) - {v2}:
                    arcs.append((v3, v1))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for word in self.domains:
            if word not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        ass = assignment
        for var in ass:
            word = ass[var]

            # This is the check for the unary constraints (for this problem its the length of word and blanks in puzzle)
            if len(word) != var.length:
                return False

            # This part ensures that all the assignments are distinct
            for other in ass:
                if var != other and word == ass[other]:
                    return False

            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if overlap is None:
                        continue
                    char_index, neighbor_char_index = overlap
                    if word[char_index] != ass[neighbor][neighbor_char_index]:
                        return False
        return True

    def order_domain_values(self, var, assignment: dict) -> list:
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        ranking = {val: 0 for val in self.domains[var]}
        neighbors = {
            var: self.domains[var]
            for var in self.crossword.neighbors(var)
            if var not in assignment
        }
        for val in ranking:
            for neighbor in neighbors:
                for val2 in neighbor:
                    # overlap = self.crossword.overlaps[var, neighbor]
                    # var_index, neighbor_index = overlap
                    # if val[var_index] != val2[neighbor_index]:
                    if val == val2:
                        ranking[val] += 1
        ranking = sorted(ranking, key=lambda val: ranking[val])

    def select_unassigned_variable(self, assignment: dict):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        best_choice = None
        domains = {}
        for var, domain in self.domains.items():
            if var not in assignment:
                domains[var] = domain

        for var, domain in domains.items():
            degree = len(self.crossword.neighbors(var))
            domain_len = len(domain)
            if best_choice is None:
                best_choice = (var, domain_len, degree)
            else:
                _, domain_len_of_best_choice, degree_of_best_choice = best_choice
                if domain_len < domain_len_of_best_choice:
                    best_choice = (var, domain_len, degree)
                elif domain_len == domain_len_of_best_choice:
                    if degree > degree_of_best_choice:
                        best_choice = (var, domain_len, degree)
        return best_choice[0]

    def backtrack(self, assignment: dict):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(
            assignment
        )  # This chooses Variable which has the smallest domain and highest range or degree
        for value in self.order_domain_values(var, assignment):
            per_assigned_domain = deepcopy(self.domains)
            assignment[var] = value
            if self.consistent(assignment):
                arcs = [(other, var) for other in self.crossword.neighbors(var)]
                self.ac3(arcs)
                result = self.backtrack(assignment)
                if result:
                    return result
            self.domains = per_assigned_domain
            del assignment[var]
        return False


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
