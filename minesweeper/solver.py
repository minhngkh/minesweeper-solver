from minesweeper._global import *

import pysat.solvers
import copy
import heapq
from enum import Enum


def combinations(iterable, r):
    "Python implementation of itertools.combinations"

    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
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


def construct_CNF_clauses(field):
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
            if field[i][j] == 0 or field[i][j] == FLAGGED or field[i][j] == UNOPENED:
                continue

            surrounded_mines = field[i][j]
            neighbors = []
            for y in range(max(0, i - 1), min(height, i + 2)):
                for x in range(max(0, j - 1), min(width, j + 2)):
                    if y == i and x == j:
                        continue

                    if field[y][x] == FLAGGED:
                        surrounded_mines -= 1
                        continue

                    if field[y][x] != UNOPENED:
                        continue

                    # Convert 2D coordinates to 1D (starting from 1)
                    pos = y * width + x + 1
                    neighbors.append(pos)
                    vars_.add(pos)

            # Encode "at most" constraint as CNF clauses
            for c in combinations(neighbors, surrounded_mines + 1):
                clauses.append([-x for x in c])

            # Encode "at least" constraint as CNF clauses
            for c in combinations(neighbors, len(neighbors) - surrounded_mines + 1):
                clauses.append([x for x in c])

    return clauses, vars_


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
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED

    solver.delete()
    return flagged_field


class KB:
    def __init__(self, from_clauses: list[list[int]] = None, vars_: set[int] = None):
        self.clauses: list[list[int]] = []
        self.vars: set[int] = set()

        if from_clauses is not None:
            self.clauses = from_clauses
        if vars_ is not None:
            self.vars = vars_

    def add_clause(self, clause: list[int]):
        self.clauses.append(clause)
        self.vars.update(map(abs, clause))

    def add_clauses(self, clauses: list[list[int]]):
        self.clauses.extend(clauses)
        for clause in clauses:
            self.vars.update(map(abs, clause))

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


class KB_l:
    def __init__(self, from_clauses: list[list[int]] = None, vars_: list[int] = None):
        self.clauses: list[list[int]] = []
        self.vars: list[int] = []

        if from_clauses is not None:
            self.clauses = from_clauses
        if vars_ is not None:
            self.vars = vars_

    def add_clause(self, clause: list[int]):
        self.clauses.append(clause)
        self.vars.update(map(abs, clause))

    def add_clauses(self, clauses: list[list[int]]):
        self.clauses.extend(clauses)
        for clause in clauses:
            self.vars.update(map(abs, clause))

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


def undetermined_clauses(kb: KB, model: dict[int, bool]) -> int | None:
    """Get the number of undetermined clauses when applying in a model.

    Args:
        cnf (CNF): clauses
        model (dict[int, bool]): model to check

    Returns:
        int | None: return the number unless the model does not satisfy KB
    """
    if kb.is_satisfied(model):
        return 0
    else:
        return 1

    count = 0

    for clause in kb.clauses:
        correct = False
        has_unknown_var = False

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
                has_unknown_var = True

        if correct:
            continue
        elif has_unknown_var:
            count += 1
        else:
            return None

    return count


def child_models(cnf: KB, parent_model: dict[int, bool]):
    for var in cnf.vars:
        if var in parent_model:
            continue

        for val in (True, False):
            child_model = copy.deepcopy(parent_model)
            child_model[var] = val
            yield child_model


class hashable_dict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class Node:
    __slots__ = ["model", "h"]

    def __init__(self, model: hashable_dict[int, bool], h: int):
        self.model = model
        self.h = h

    def __lt__(self, other):
        return self.h < other.h


def a_star_search(kb: KB, init_model: hashable_dict[int, bool]) -> bool:
    h = undetermined_clauses(kb, init_model)
    # if h is None:
    #     return False

    node = Node(copy.deepcopy(init_model), h)

    frontier = []
    heapq.heappush(frontier, node)
    explored = set()

    while True:
        if not frontier:
            return False

        node = heapq.heappop(frontier)

        if node.model in explored:
            continue

        # if kb.is_satisfied(node.model):
        #     return True

        if node.h == 0:
            return True

        explored.add(node.model)

        for child_model in child_models(kb, node.model):
            if child_model in explored:
                continue

            h = undetermined_clauses(kb, child_model)
            if h is None:
                continue

            heapq.heappush(frontier, Node(child_model, h))


def a_star_solve(field):
    clauses, vars_ = construct_CNF_clauses(field)

    kb = KB(clauses, vars_)

    # if not a_star_search(kb, hashable_dict()):
    #     raise ValueError("Unsolvable grid")

    # print("ok")

    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for var in vars_:
        if not a_star_search(kb, hashable_dict({var: False})):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED

    return flagged_field


def brute_force_solve(field):
    clauses, vars_ = construct_CNF_clauses(field)

    kb = KB(clauses, vars_)

    # for true_vars in combinations(vars_, len(vars_)):
    #     model = {var: True if var in true_vars else False for var in vars_}
    #     if kb.is_satisfied(model):
    #         break

    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for var in vars_:
        new_vars = [x for x in vars_ if x != var]

        to_flag = True
        for i in range(1, len(vars_)):
            for true_vars in combinations(new_vars, i):
                model = {var: True if var in true_vars else False for var in new_vars}
                model[var] = False
                if kb.is_satisfied(model):
                    to_flag = False
                    break
            if not to_flag:
                break
        if to_flag:
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED

    return flagged_field


def backtracking_search(kb: KB, model: dict[int, bool]) -> bool:
    if kb.is_satisfied(model):
        return True

    assigned = set(model.keys())
    for var in kb.vars:
        if var in assigned:
            continue

        child_model = copy.deepcopy(model)
        child_model[var] = False
        if backtracking_search(kb, child_model):
            return True

        child_model = copy.deepcopy(model)
        child_model[var] = True
        if backtracking_search(kb, child_model):
            return True

    return False


def test(kb: KB_l, model: dict[int, bool], exclude, idx=0) -> bool:
    ans = kb.is_satisfied_t(model)
    if ans == Answer.TRUE:
        return True
    if ans == Answer.FALSE:
        return False

    if idx == exclude:
        return test(kb, model, exclude, idx + 1)
    if idx == len(kb.vars):
        return False

    for child in (False, True):
        child_model = model.copy()
        child_model[kb.vars[idx]] = child
        if test(kb, child_model, exclude, idx + 1):
            return True

    return False


def test2(kb: KB, model: dict[int, bool]) -> bool:
    ans = kb.is_satisfied_t(model)
    if ans == Answer.TRUE:
        return True
    if ans == Answer.FALSE:
        return False

    for var in kb.vars:
        if var in model:
            continue

        for val in (False, True):
            child_model = model.copy()
            child_model[var] = val
            if test2(kb, child_model):
                return True
        break

    return False


def backtracking_solve(field):
    clauses, vars_ = construct_CNF_clauses(field)

    kb = KB(clauses, vars_)

    # TODO: checking if the model is solvable or not

    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for i, var in enumerate(vars_):
        model = dict()
        model[var] = False
        if not test2(kb, model):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED

    return flagged_field


def backtracking_solve2(field):
    clauses, vars_ = construct_CNF_clauses(field)

    kb = KB_l(clauses, list(vars_))

    # TODO: checking if the model is solvable or not

    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for i, var in enumerate(vars_):
        model = dict()
        model[var] = False
        if not test(kb, model, i):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED

    return flagged_field
