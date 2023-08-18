from minesweeper._global import Field, Answer, FLAGGED_VAL
from minesweeper.solver import KB, construct_CNF_clauses
from minesweeper.a_star_solver import Node

import heapq
import copy
import time
from typing import Generator


def is_satisfied(kb: KB, model: tuple[bool | None]) -> tuple[Answer, int]:
    """Check if a model (can be partial) satisfies all clauses

    Args:
        model (tuple[bool  |  None]): _description_

    Returns:
        tuple[Answer, int]: _description_
    """

    count = 0

    for clause in kb.clauses:
        correct = False
        has_unassigned = False

        for var in clause:
            val = model[kb.idx_dict[abs(var)]]
            if val is not None:
                if var > 0:
                    if val:
                        correct = True
                        break
                else:
                    if not val:
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


def gen_state(kb: KB, model: dict[int, bool]) -> tuple[bool | None]:
    return tuple(model[var] if var in model else None for var in kb.vars)


def child_states(
    parent_state: tuple[bool | None], exclude: int
) -> Generator[tuple[bool | None], None, None]:
    for i, val in enumerate(parent_state):
        if i == exclude:
            continue
        if val is not None:
            continue

        for child_val in (True, False):
            yield parent_state[:i] + (child_val,) + parent_state[i + 1 :]


def a_star_search_inc(kb: KB, init_model: dict[int, bool], exclude: int = -1) -> bool:
    l = len(kb.clauses)

    state = gen_state(kb, init_model)
    ans, h = is_satisfied(kb, state)
    if ans == Answer.FALSE:
        return False
    node = Node(state, h)

    frontier: list[Node] = []
    heapq.heappush(frontier, node)
    explored: set[tuple[bool | None]] = set()

    while True:
        if not frontier:
            return False

        node = heapq.heappop(frontier)

        if node.state in explored:
            print(1, end="")
            continue

        if node.h == 0:
            return True

        explored.add(node.state)

        for child_state in child_states(node.state, exclude):
            if child_state in explored:
                continue

            ans, h = is_satisfied(kb, child_state)
            if ans == Answer.FALSE:
                continue

            heapq.heappush(
                frontier,
                Node(child_state, h),
            )


def a_star_solve_inc(
    field: Field, check_field: bool = False, display_checking_time: bool = True
) -> Field:
    clauses, vars_ = construct_CNF_clauses(field)
    kb = KB(clauses, vars_, create_idx_dict=True)

    if check_field:
        start = 0
        if display_checking_time:
            start = time.process_time()

        if not a_star_search_inc(kb, {}):
            raise ValueError("Unsolvable grid")

        if display_checking_time:
            print("check: ", time.process_time() - start, "s")

    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for i, var in enumerate(vars_):
        if not a_star_search_inc(kb, {var: False}, i):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL

    return flagged_field
