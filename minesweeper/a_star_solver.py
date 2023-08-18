from minesweeper._global import Field, FLAGGED_VAL
from minesweeper.solver import KB, construct_CNF_clauses

import copy
import heapq
import time
from recordclass import dataobject
from typing import Generator


class Node(dataobject):
    state: tuple[bool | None]
    h: int | float

    def __init__(self, state: tuple[bool | None], h: int | float):
        self.state = state
        self.h = h

    def __lt__(self, other):
        return self.h < other.h


def gen_state(kb: KB, model: dict[int, bool]) -> tuple[bool | None]:
    return tuple(model[var] if var in model else False for var in kb.vars)


def child_states(
    parent_state: tuple[bool | None], exclude: int
) -> Generator[tuple[bool | None], None, None]:
    for i, val in enumerate(parent_state):
        if i != exclude:
            yield parent_state[:i] + (not val,) + parent_state[i + 1 :]


def a_star_search(kb: KB, init_model: dict[int, bool], exclude: int = -1) -> bool:
    state = gen_state(kb, init_model)
    node = Node(state, kb.num_false_clauses(state))

    frontier: list[Node] = []
    heapq.heappush(frontier, node)
    explored: set[tuple[bool | None]] = set()

    l = len(kb.clauses)

    while True:
        if not frontier:
            return False

        node = heapq.heappop(frontier)

        if node.state in explored:
            # print(1, end="")
            continue

        # if kb.is_satisfied(node.model):
        #     return True

        if node.h == 0:
            return True

        explored.add(node.state)

        for child_state in child_states(node.state, exclude):
            if child_state in explored:
                continue

            heapq.heappush(
                frontier, Node(child_state, kb.num_false_clauses(child_state))
            )


def a_star_solve(
    field: Field, check_field: bool = False, display_checking_time: bool = True
) -> Field:
    clauses, vars_ = construct_CNF_clauses(field)
    kb = KB(clauses, vars_, create_idx_dict=True)

    if check_field:
        start = 0
        if display_checking_time:
            start = time.process_time()

        if not a_star_search(kb, {}):
            raise ValueError("Unsolvable grid")

        if display_checking_time:
            print("check: ", time.process_time() - start, "s")

    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for i, var in enumerate(vars_):
        if not a_star_search(kb, {var: False}, i):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL

    return flagged_field
