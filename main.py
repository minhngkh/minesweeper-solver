import minesweeper as ms
import time


size = "5x5"
i_path = f"testcases/input_{size}.txt"
o_path = f"testcases/output_{size}.txt"

if __name__ == "__main__":
    data = ms.read_field("test.txt")
    ms.print_field(data)

    try:
        start = time.process_time()
        solution = ms.brute_force_solve(data)
        elapsed = time.process_time() - start
        if solution:
            ms.print_field(solution)
            ms.write_field(solution, "out.txt")
            print(f"Time elapsed: {elapsed}")
        else:
            print("No solution found")
    except Exception as e:
        print(e)


# if __name__ == "__main__":
#     kb = ms.KB()

#     kb.add_clauses([[-1, 2], [-1, -2]])
#     model = {2: False}

#     start = time.process_time()
#     ans = ms.undetermined_clauses(kb, model)
#     print(ans, time.process_time() - start)

#     start = time.process_time()
#     ans = kb.is_satisfied(model)
#     print(ans, time.process_time() - start)
