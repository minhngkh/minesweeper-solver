from minesweeper._global import Field, FLAGGED_VAL
from minesweeper.solver import KB, construct_CNF_clauses, combinations

import copy
import time


def brute_force_solve(
    field: Field, check_field: bool = False, display_checking_time: bool = True
) -> Field:
    clauses, vars_ = construct_CNF_clauses(field)
    kb = KB(clauses, vars_)

    # Check if the grid is valid (solvable) or not if required
    if check_field:
        start = 0
        if display_checking_time:
            start = time.process_time()

        found_model = False
        for i in range(1, len(vars_)):
            for true_vars in combinations(vars_, i):
                model = {var: True if var in true_vars else False for var in vars_}
                if kb.is_satisfied(model):
                    found_model = True
                    break
            if found_model:
                break
        if not found_model:
            raise ValueError("Unsolvable grid")

        if display_checking_time:
            print("check: ", time.process_time() - start, "s")

    # Finding solution
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
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL

    return flagged_field
