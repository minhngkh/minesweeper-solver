from minesweeper._global import *
from minesweeper.solver import KB, construct_CNF_clauses, combinations

import copy


def brute_force_solve(field: Field) -> Field:
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
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL

    return flagged_field
