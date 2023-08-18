from minesweeper._global import Field, Answer, FLAGGED_VAL
from minesweeper.solver import KB, construct_CNF_clauses

import copy
import time


def backtracking_search(
    kb: KB, model: dict[int, bool], exclude: int = -1, idx: int = 0
) -> bool:
    ans, _ = kb.is_satisfied_extended(model)
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


def backtracking_solve(
    field: Field, check_field: bool = False, display_checking_time: bool = True
) -> Field:
    clauses, vars_ = construct_CNF_clauses(field)
    kb = KB(clauses, vars_, create_idx_dict=True)

    if check_field:
        start = 0
        if display_checking_time:
            start = time.process_time()

        if not backtracking_search(kb, {}):
            raise ValueError("Unsolvable grid")

        if display_checking_time:
            print("check: ", time.process_time() - start, "s")

    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for i, var in enumerate(vars_):
        if not backtracking_search(kb, {var: False}, i):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL

    return flagged_field
