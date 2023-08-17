from minesweeper._global import *
from minesweeper.solver import KB, construct_CNF_clauses

import copy
import heapq


class hashable_dict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class Node:
    __slots__ = ["model", "h"]

    def __init__(self, model: dict[int, bool], h: int):
        self.model = model
        self.h = h

    def __lt__(self, other):
        return self.h < other.h
    
def 


def child_models(cnf: KB, parent_model: dict[int, bool]):
    for var in cnf.vars:
        if var in parent_model:
            continue

        for val in (True, False):
            child_model = copy.copy(parent_model)
            child_model[var] = val
            yield child_model


def a_star_search(kb: KB, init_model: dict[int, bool]) -> bool:
    ans, h = kb.is_satisfied_r(init_model)
    if ans == Answer.FALSE:
        return False
    node = Node(init_model, h)

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

        for child_model in child_models(kb, node.model):
            if child_model in explored:
                continue

            ans, h = kb.is_satisfied_r(child_model)
            if ans == Answer.FALSE:
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
            flagged_field[(var - 1) // width][(var - 1) % width] = FLAGGED_VAL

    return flagged_field
