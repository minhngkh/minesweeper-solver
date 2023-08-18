import minesweeper as ms
import time


folder = "testcases"
test_file = [
    ["input_4x4.txt", "output_4x4.txt", "evaluate/4x4.txt"],
    ["input_5x5.txt", "output_5x5.txt", "evaluate/5x5.txt"],
    ["input_9x9.txt", "output_9x9.txt", "evaluate/9x9.txt"],
    ["input_11x11.txt", "output_11x11.txt", "evaluate/11x11.txt"],
    ["input_15x15.txt", "output_15x15.txt", "evaluate/15x15.txt"],
    ["input_20x20.txt", "output_20x20.txt", "evaluate/20x20.txt"],
]


if __name__ == "__main__":
    to_check_field = False
    count = 0

    for i_path, o_path, eval_path in test_file:
        print(f"Testing {i_path}...")

        data = ms.read_field(folder + "/" + i_path)
        ms.print_field(data)

        try:
            start = time.process_time()
            solution = ms.brute_force_solve(data, to_check_field)
            elapsed = time.process_time() - start

            ms.print_field(solution)
            ms.write_field(solution, folder + "/" + o_path)
            print(f"Time solving: {elapsed} s")

            expected = ms.read_field(folder + "/" + eval_path)
            if solution == expected:
                print("→ Correct!")
                count += 1
            else:
                print("Wrong!")
        except Exception as e:
            print(e)

        print("-" * 20)

    print(f"Correct: {count}/{len(test_file)}")


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
