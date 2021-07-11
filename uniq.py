import sys
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "fileName", nargs='?', type=argparse.FileType('r', encoding="utf-8"), default="-")
parser.add_argument(
    "-c", "--count", help="prefix lines by the number of occurrences")
parser.add_argument("-d", "--repeated",
                    help="only print duplicate lines, one for each group")
parser.add_argument("-D", "--all-repeated", help="increase output verbosity")
parser.add_argument("-f", "--skip-fields=N",
                    help="avoid comparing the first N fields")
parser.add_argument("-i", "--igonore-case",
                    help="ignore differences in case when comparing")
parser.add_argument("-s", "--skip-chars=N",
                    help="avoid comparing the first N characters")
parser.add_argument(
    "-u", "--unique", help="only print unique lines")
parser.add_argument("-z", "--zero-terminated",
                    help="line delimiter is NUL, not newline")
parser.add_argument("-w", "--check-chars",
                    help="compare no more than N characters in lines")


args = parser.parse_args()


def removeLines(file) -> bool:
    lines = file.read().splitlines()
    if not lines:
        return False
    NumOfLines = len(lines)
    for s_line in range(1, NumOfLines):
        # 行-１とその一行前の行を比較
        if lines[s_line] != lines[s_line-1]:
            print(lines[s_line-1])
        if s_line == NumOfLines-1:
            print(lines[s_line])


def printLines(file):
    while True:
        if removeLines(file) is False:
            break


if args.fileName.name != '<stdin>':
    try:
        with open(args.fileName.name) as file:
            removeLines(file)
        file.close()
    except FileNotFoundError:
        sys.exit("wo such file or directory:" + file)

else:
    printLines(args.fileName)
