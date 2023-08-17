from minesweeper._global import *
from minesweeper.solver import KB, construct_CNF_clauses

import copy


def backtracking_search(kb: KB, model: dict[int, bool], exclude, idx=0) -> bool:
    ans, _= kb.is_satisfied_r(model)
    if ans == Answer.TRUE:
        return True
    if ans == Answer.FALSE:
        return False

    if idx == exclude:
        return backtracking_search(kb, model, exclude, idx + 1)
    if idx == len(kb.vars):
        return False

    for val in (False, True):
        child_model = model.copy()
        child_model[kb.vars[idx]] = val
        if backtracking_search(kb, child_model, exclude, idx + 1):
            return True

    return False


def backtracking_solve(field):
    clauses, vars_ = construct_CNF_clauses(field)

    kb = KB(clauses, vars_)

    # TODO: checking if the model is solvable or not

    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for i, var in enumerate(vars_):
        if not backtracking_search(kb, {var: False}, i):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL

    return flagged_field
