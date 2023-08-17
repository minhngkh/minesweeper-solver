from minesweeper._global import *
from enum import Enum

UNOPENED_PRINT_CHAR = "■"
FLAGGED_PRINT_CHAR = "⚐"
EMPTY_PRINT_CHAR = " "


def read_field(file_name: str) -> Field:
    """Reads input file and returns an array"""
    with open(file_name, "r") as f:
        data = []
        for line in f:
            row = []
            for item in line.split(","):
                item = item.strip()

                if item.isdigit():
                    row.append(int(item))
                elif item == UNOPENED_CHAR:
                    row.append(UNOPENED_VAL)
                elif item == FLAGGED_CHAR:
                    row.append(FLAGGED_VAL)
                else:
                    raise ValueError("Invalid character in input file")

            data.append(row)

    return data


def write_field(data: Field, file_name: str) -> None:
    """Writes array to file"""
    with open(file_name, "w") as f:
        for row in data:
            to_write = []
            for item in row:
                if item == UNOPENED_VAL:
                    to_write.append(UNOPENED_CHAR)
                elif item == FLAGGED_VAL:
                    to_write.append(FLAGGED_CHAR)
                else:
                    to_write.append(str(item))

            f.write(", ".join(to_write))
            f.write("\n")


def print_field(data: Field) -> None:
    for row in data:
        for cell in row:
            if cell == UNOPENED_VAL:
                print(UNOPENED_PRINT_CHAR, end=" ")
            elif cell == FLAGGED_VAL:
                print(FLAGGED_PRINT_CHAR, end=" ")
            else:
                if cell == 0:
                    print(EMPTY_PRINT_CHAR, end=" ")
                else:
                    print(cell, end=" ")
        print()
    print()
