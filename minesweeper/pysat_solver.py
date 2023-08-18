from minesweeper._global import Field, FLAGGED_VAL
from minesweeper.solver import construct_CNF_clauses

import pysat.solvers
import copy
import time


def pysat_solve(
    field: Field, check_field: bool = False, display_checking_time: bool = True
) -> Field:
    clauses, vars_ = construct_CNF_clauses(field)
    solver = pysat.solvers.Solver(bootstrap_with=clauses)

    # Check if the grid is valid (solvable) or not if required
    if check_field:
        start = 0
        if display_checking_time:
            start = time.process_time()

        if not solver.solve():
            raise ValueError("Unsolvable grid")

        if display_checking_time:
            print("check: ", time.process_time() - start, "s")

    # Finding process
    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for var in vars_:
        if not solver.solve(assumptions=[-var]):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL

    solver.delete()
    return flagged_field
