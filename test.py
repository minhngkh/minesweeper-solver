import minesweeper as ms

explored = set()

model = ms.hashable_dict({1: True, 2: False})
explored.add(model)

print(ms.hashable_dict({1: True, 2: False}) in explored)