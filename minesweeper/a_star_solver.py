from minesweeper._global import *
from minesweeper.solver import KB, construct_CNF_clauses

import copy
import heapq
from recordclass import dataobject
import time
import builtins


class hashable_dict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class Node_old:
    __slots__ = ["model", "h"]

    def __init__(self, model: dict[int, bool], h: int):
        self.model = model
        self.h = h

    def __lt__(self, other):
        return self.h < other.h


class Node(dataobject):
    state: tuple[bool | None]
    h: int | float

    def __init__(self, state: tuple[bool | None], h: int | float):
        self.state = state
        self.h = h

    def __lt__(self, other):
        return self.h < other.h


def child_models_old(cnf: KB, parent_model: dict[int, bool]):
    for var in cnf.vars:
        if var in parent_model:
            continue

        for val in (True, False):
            child_model = hashable_dict(parent_model)
            child_model[var] = val
            yield child_model


def a_star_search_old(kb: KB, init_model: dict[int, bool]) -> bool:
    ans, h = kb.is_satisfied_r(init_model)
    if ans == Answer.FALSE:
        return False
    node = Node_old(init_model, h)

    frontier = []
    heapq.heappush(frontier, node)
    explored = set()

    l = len(kb.clauses)

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

        for child_model in child_models_old(kb, node.model):
            if child_model in explored:
                continue

            ans, h = kb.is_satisfied_r(child_model)
            if ans == Answer.FALSE:
                continue

            heapq.heappush(frontier, Node_old(child_model, h))


def gen_state(kb: KB, model: dict[int, bool]):
    return tuple(model[var] if var in model else None for var in kb.vars)


def child_states(parent_state: tuple[bool | None], exclude):
    for i, val in enumerate(parent_state):
        if i == exclude:
            continue
        if val is not None:
            continue

        for child_val in (True, False):
            yield parent_state[:i] + (child_val,) + parent_state[i + 1 :]


def a_star_search(kb: KB, init_model: dict[int, bool], exclude) -> bool:
    l = len(kb.clauses)

    state = gen_state(kb, init_model)
    ans, h = kb.is_satisfied_l(state)
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

            ans, h = kb.is_satisfied_l(child_state)
            if ans == Answer.FALSE:
                continue

            heapq.heappush(
                frontier,
                Node(child_state, h),
            )


def gen_state_test(kb: KB, model: dict[int, bool]):
    return tuple(model[var] if var in model else False for var in kb.vars)


def child_states_test(parent_state: tuple[bool | None], exclude):
    for i, val in enumerate(parent_state):
        if i != exclude:
            yield parent_state[:i] + (not val,) + parent_state[i + 1 :]


def test(kb: KB, init_model: dict[int, bool], exclude) -> bool:
    state = gen_state_test(kb, init_model)
    node = Node(state, kb.h(state))

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

        for child_state in child_states_test(node.state, exclude):
            if child_state in explored:
                continue

            heapq.heappush(frontier, Node(child_state, kb.h(child_state)))


def a_star_solve(field):
    clauses, vars_ = construct_CNF_clauses(field)

    kb = KB(clauses, vars_, create_idx_dict=True)

    # if not a_star_search(kb, hashable_dict()):
    #     raise ValueError("Unsolvable grid")

    # print("ok")

    # ans = kb.is_satisfied_r({34: False, 8: True})

    height = len(field)
    width = len(field[0])

    flagged_field = copy.deepcopy(field)
    for i, var in enumerate(vars_):
        start = time.process_time()
        if not test(kb, {var: False}, i):
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL
        print(time.process_time() - start)

    return flagged_field
