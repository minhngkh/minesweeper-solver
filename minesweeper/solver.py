from minesweeper._global import *

import pysat.solvers
import copy
from typing import Iterable, Generator


def combinations(iterable: Iterable, r: int) -> Generator[tuple, None, None]:
    """Python implementation of itertools.combinations

    combinations('ABCD', 2) --> AB AC AD BC BD CD
    #combinations(range(4), 3) --> 012 013 023 123
    """

    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, r):
            indices[j] = indices[j - 1] + 1
        yield tuple(pool[i] for i in indices)


def construct_CNF_clauses(field: Field) -> tuple[list[Clause], list[int]]:
    height = len(field)
    width = len(field[0])
    clauses = []
    vars_ = set()

    # Add CNF clauses for each opened cell.
    for i in range(height):
        for j in range(width):
            # We only care about "opened" cells, since only them can provide information
            # to create clauses.
            # We also ignore "opened cell" that is 0, because in the minesweeper game,
            # every cell around it has already been opened by default.
            if (
                field[i][j] == 0
                or field[i][j] == FLAGGED_VAL
                or field[i][j] == UNOPENED_VAL
            ):
                continue

            surrounded_mines = field[i][j]
            neighbors = []
            for y in range(max(0, i - 1), min(height, i + 2)):
                for x in range(max(0, j - 1), min(width, j + 2)):
                    if y == i and x == j:
                        continue

                    if field[y][x] == FLAGGED_VAL:
                        surrounded_mines -= 1
                        continue

                    if field[y][x] != UNOPENED_VAL:
                        continue

                    # Convert 2D coordinates to 1D (starting from 1)
                    pos = y * width + x + 1
                    neighbors.append(pos)

            vars_.update(neighbors)

            # Encode "at most" constraint as CNF clauses
            for c in combinations(neighbors, surrounded_mines + 1):
                clauses.append([-x for x in c])

            # Encode "at least" constraint as CNF clauses
            for c in combinations(neighbors, len(neighbors) - surrounded_mines + 1):
                clauses.append([x for x in c])

    return clauses, list(vars_)


def pysat_solve(field):
    height = len(field)
    width = len(field[0])

    clauses, vars_ = construct_CNF_clauses(field)
    solver = pysat.solvers.Solver(bootstrap_with=clauses)

    # Check if the grid is valid (solvable) or not (satisfiable check)
    if not solver.solve():
        raise ValueError("Unsolvable grid")

    # For every variable appears in the KB, we use resolution refutation to check if that
    # variable is true, which means the corresponding cell contains a mine.
    flagged_field = copy.deepcopy(field)
    for var in vars_:
        if not solver.solve(assumptions=[-var]):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL

    solver.delete()
    return flagged_field


class KB:
    def __init__(
        self,
        from_clauses: list[Clause] | None = None,
        vars_: list[int] | None = None,
        create_vars_set: bool = False,
    ) -> None:
        if from_clauses is None:
            self.clauses = []
        else:
            self.clauses = from_clauses
        if vars_ is None:
            self.vars = []
        else:
            self.vars = vars_
            if create_vars_set:
                self.vars_set = set(vars_)

    def add_clause(self, clause: list[int]) -> None:
        self.clauses.append(clause)
        self.vars.extend(map(abs, clause))

    def add_clauses(self, clauses: list[list[int]]) -> None:
        self.clauses.extend(clauses)
        for clause in clauses:
            self.vars.extend(map(abs, clause))

    def is_satisfied(self, model: dict[int, bool]) -> bool:
        """Check if a model (can be partial) satisfies all clauses

        Args:
            model (dict[int, bool]): The model to check

        Returns:
            bool: True if the model satisfies all clauses, False otherwise
        """
        for clause in self.clauses:
            correct = False

            for var in clause:
                if abs(var) in model:
                    if var > 0:
                        if model[abs(var)]:
                            correct = True
                            break
                    else:
                        if not model[abs(var)]:
                            correct = True
                            break

            if not correct:
                return False

        return True

    def is_satisfied_t(self, model: dict[int, bool]) -> Answer:
        """Check if a model (can be partial) satisfies all clauses

        Args:
            model (dict[int, bool]): The model to check

        Returns:
            bool: True if the model satisfies all clauses, False otherwise
        """
        for clause in self.clauses:
            correct = False
            has_unassigned = False

            for var in clause:
                if abs(var) in model:
                    if var > 0:
                        if model[abs(var)]:
                            correct = True
                            break
                    else:
                        if not model[abs(var)]:
                            correct = True
                            break
                else:
                    has_unassigned = True

            if not correct:
                if has_unassigned:
                    return Answer.UNKNOWN
                else:
                    return Answer.FALSE
        return Answer.TRUE

    def is_satisfied_r(self, model: dict[int, bool]) -> tuple[Answer, int]:
        count = 0

        for clause in self.clauses:
            correct = False
            has_unassigned = False

            for var in clause:
                if abs(var) in model:
                    if var > 0:
                        if model[abs(var)]:
                            correct = True
                            break
                    else:
                        if not model[abs(var)]:
                            correct = True
                            break
                else:
                    has_unassigned = True

            if not correct:
                if has_unassigned:
                    count += 1
                    # return Answer.UNKNOWN, -1
                else:
                    return Answer.FALSE, -1

        if count == 0:
            return Answer.TRUE, count
        return Answer.UNKNOWN, count

    def is_satisfied_l(self, model: list[int]) -> tuple[Answer, int]:
        count = 0

        for clause in self.clauses:
            correct = False
            has_unassigned = False

            for var in clause:
                if abs(var) in self.vars_set:
                    if var > 0:
                        if model[)]:
                            correct = True
                            break
                    else:
                        if not model[abs(var)]:
                            correct = True
                            break
                else:
                    has_unassigned = True

            if not correct:
                if has_unassigned:
                    count += 1
                    # return Answer.UNKNOWN, -1
                else:
                    return Answer.FALSE, -1

        if count == 0:
            return Answer.TRUE, count
        return Answer.UNKNOWN, count
